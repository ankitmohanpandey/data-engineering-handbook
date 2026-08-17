"""
Example 7: End-to-End Kafka Streaming Pipeline

This example demonstrates a realistic, end-to-end pipeline that ties
together concepts from all previous examples:
- Reading from Kafka with a KafkaSource + watermark strategy
- Deserializing JSON events
- Keying, windowing, and aggregating in event time
- Writing results back to Kafka with a KafkaSink (exactly-once capable)
- Checkpointing enabled for fault tolerance

WHAT IT DOES:
Consumes JSON "order" events from a Kafka topic, computes a 1-minute
tumbling-window revenue total per customer, and writes the results to
another Kafka topic.

PREREQUISITES:
A running Kafka broker at localhost:9092 with topics `orders-input` and
`orders-output` (see SETUP.md for a quick local Kafka via Docker).

HOW TO RUN:
python 07_kafka_streaming_pipeline.py

To produce sample data for testing, from a separate terminal:
    echo '{"customer_id": 1, "amount": 42.5, "event_time": 1700000000000}' | \\
        kafka-console-producer.sh --broker-list localhost:9092 --topic orders-input
"""

import json

from pyflink.datastream import StreamExecutionEnvironment, CheckpointingMode
from pyflink.datastream.connectors.kafka import (
    KafkaSource,
    KafkaSink,
    KafkaRecordSerializationSchema,
    KafkaOffsetsInitializer,
)
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.common.watermark_strategy import WatermarkStrategy, TimestampAssigner
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import Duration, Time
from pyflink.common.typeinfo import Types

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
INPUT_TOPIC = "orders-input"
OUTPUT_TOPIC = "orders-output"
CONSUMER_GROUP = "flink-learning-orders-group"


class OrderTimestampAssigner(TimestampAssigner):
    """Extracts the event_time field (ms since epoch) from a parsed order dict."""

    def extract_timestamp(self, value, record_timestamp):
        return value["event_time"]


def parse_order_json(raw_json: str):
    """Parse a raw Kafka message into a Python dict."""
    return json.loads(raw_json)


def build_kafka_source():
    return (
        KafkaSource.builder()
        .set_bootstrap_servers(KAFKA_BOOTSTRAP_SERVERS)
        .set_topics(INPUT_TOPIC)
        .set_group_id(CONSUMER_GROUP)
        .set_starting_offsets(KafkaOffsetsInitializer.latest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )


def build_kafka_sink():
    return (
        KafkaSink.builder()
        .set_bootstrap_servers(KAFKA_BOOTSTRAP_SERVERS)
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(OUTPUT_TOPIC)
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
        )
        # DeliveryGuarantee.EXACTLY_ONCE relies on Kafka transactions --
        # requires transactional.id prefix + broker support.
        .build()
    )


def run_pipeline():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(2)

    # Fault tolerance: checkpoint every 30s so Kafka consumer offsets and
    # windowed aggregation state survive failures.
    env.enable_checkpointing(30_000, CheckpointingMode.EXACTLY_ONCE)

    # 1) SOURCE: read raw JSON strings from Kafka.
    kafka_source = build_kafka_source()
    raw_stream = env.from_source(
        kafka_source, WatermarkStrategy.no_watermarks(), "kafka-orders-source"
    )

    # 2) PARSE: turn each JSON string into a Python dict.
    parsed_stream = raw_stream.map(parse_order_json, output_type=Types.PICKLED_BYTE_ARRAY())

    # 3) ASSIGN EVENT TIME + WATERMARKS: tolerate up to 10s of out-of-order
    #    arrival before considering an event "late".
    watermark_strategy = (
        WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(10))
        .with_timestamp_assigner(OrderTimestampAssigner())
        .with_idleness(Duration.of_seconds(60))  # tolerate idle partitions
    )
    orders_with_time = parsed_stream.assign_timestamps_and_watermarks(watermark_strategy)

    # 4) KEY + WINDOW + AGGREGATE: 1-minute tumbling window revenue per customer.
    windowed_revenue = (
        orders_with_time.key_by(lambda order: order["customer_id"])
        .window(TumblingEventTimeWindows.of(Time.minutes(1)))
        .reduce(
            lambda a, b: {
                "customer_id": a["customer_id"],
                "amount": a["amount"] + b["amount"],
                "event_time": max(a["event_time"], b["event_time"]),
            }
        )
    )

    # 5) SERIALIZE back to JSON for the output topic.
    output_stream = windowed_revenue.map(
        lambda order: json.dumps(order), output_type=Types.STRING()
    )

    # 6) SINK: write results back to Kafka.
    kafka_sink = build_kafka_sink()
    output_stream.sink_to(kafka_sink)

    # Also print to console for local debugging/visibility.
    output_stream.print()

    env.execute("kafka-orders-windowed-revenue-pipeline")


# DETAILED EXPLANATION:-
"""
END-TO-END PIPELINE CONCEPTS:

This example combines every concept from the previous six examples into a
single, realistic streaming application:

1. Source (KafkaSource):
   - Reads from a Kafka topic starting at the 'latest' offset
   - Uses a consumer group so multiple parallel subtasks split partitions
   - Kafka partition offsets are checkpointed automatically -- on
     recovery, Flink resumes reading from the exact offset recorded in
     the last successful checkpoint (no data loss, no unbounded replay)

2. Parsing:
   - Raw Kafka messages are opaque bytes/strings until deserialized --
     here we parse JSON into a Python dict for downstream processing
   - In production, prefer a schema (Avro/Protobuf) over raw JSON for
     stronger contracts between producers and consumers

3. Event Time + Watermarks:
   - `event_time` field comes from the source event, not Flink's wall clock
   - `for_bounded_out_of_orderness` tolerates up to 10 seconds of
     out-of-order arrival, which is realistic for many real-world systems
   - `.with_idleness()` prevents an idle Kafka partition from stalling the
     watermark (and therefore stalling window firing) for the whole job

4. Windowed Aggregation:
   - `key_by(customer_id)` ensures revenue is aggregated per customer
   - Tumbling 1-minute windows produce one revenue total per customer
     per minute, only once the watermark confirms the window is complete

5. Sink (KafkaSink):
   - Serializes results back to JSON and writes to an output topic
   - `DeliveryGuarantee.EXACTLY_ONCE` (configurable on the builder) uses
     Kafka transactions so that, combined with EXACTLY_ONCE checkpointing,
     you get true end-to-end exactly-once semantics: no duplicate or
     missing revenue totals even after a failure and recovery

6. Checkpointing:
   - Every 30 seconds, Flink snapshots: Kafka consumer offsets + windowed
     aggregation state (partial sums for open windows)
   - On failure, the job resumes from the last checkpoint: offsets rewind,
     partial aggregation state is restored, and processing continues
     seamlessly

PRODUCTIONIZING THIS PIPELINE:

1. Add a Dead Letter Queue (side output) for JSON parse failures instead
   of letting the job crash on malformed input
2. Use Avro/Protobuf with a schema registry instead of raw JSON
3. Configure `DeliveryGuarantee.EXACTLY_ONCE` on the KafkaSink with a
   `transactional_id_prefix` for true end-to-end exactly-once
4. Deploy via Application Mode on Kubernetes rather than running locally
5. Set up alerting on checkpoint failures/duration and consumer lag
6. Tune parallelism to match the input topic's partition count
"""


if __name__ == "__main__":
    print("\n" + "#" * 60)
    print("# APACHE FLINK - END-TO-END KAFKA STREAMING PIPELINE")
    print("#" * 60)
    print(
        f"\nConnecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}"
        f"\nConsuming from: {INPUT_TOPIC}"
        f"\nProducing to:   {OUTPUT_TOPIC}\n"
    )

    run_pipeline()
