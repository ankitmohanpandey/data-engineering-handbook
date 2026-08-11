package com.flink.app;

import org.apache.flink.api.common.functions.AggregateFunction;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

import java.util.Properties;

public class StreamProcessingJob {

    public static void main(String[] args) throws Exception {
        // Set up the execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Enable checkpointing for fault tolerance
        env.enableCheckpointing(5000); // checkpoint every 5 seconds

        // Create Kafka source for input topic using new API
        KafkaSource<String> kafkaSource = KafkaSource.<String>builder()
            .setBootstrapServers("kafka:29092")
            .setTopics("input-events")
            .setGroupId("flink-consumer-group")
            .setStartingOffsets(OffsetsInitializer.earliest())
            .setValueOnlyDeserializer(new SimpleStringSchema())
            .build();

        // Add Kafka source to the streaming environment
        DataStream<String> eventStream = env.fromSource(kafkaSource, 
            org.apache.flink.api.common.eventtime.WatermarkStrategy.noWatermarks(), "Kafka Source")
            .uid("kafka-source");

        // Parse JSON events
        DataStream<Tuple3<String, Double, Long>> parsedStream = eventStream
            .map(new JsonParser())
            .name("JSON Parser")
            .uid("json-parser");

        // Apply windowing and aggregation
        DataStream<String> aggregatedStream = parsedStream
            .keyBy(value -> value.f0) // Group by event type
            .window(TumblingProcessingTimeWindows.of(Time.seconds(10)))
            .aggregate(new EventAggregator())
            .name("Event Aggregator")
            .uid("event-aggregator");

        // Create Kafka sink for output topic using new API
        KafkaSink<String> kafkaSink = KafkaSink.<String>builder()
            .setBootstrapServers("kafka:29092")
            .setRecordSerializer(
                org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema.builder()
                    .setTopic("output-events")
                    .setValueSerializationSchema(new SimpleStringSchema())
                    .build()
            )
            .setDeliverGuarantee(org.apache.flink.connector.base.DeliveryGuarantee.EXACTLY_ONCE)
            .build();

        // Add Kafka sink to the streaming environment
        aggregatedStream.sinkTo(kafkaSink)
            .name("Kafka Sink")
            .uid("kafka-sink");

        // Also print to console for debugging
        aggregatedStream.print();

        // Execute the job
        System.out.println("Starting Flink Stream Processing Job...");
        env.execute("Flink Stream Processing with Kafka");
    }

    // JSON Parser MapFunction
    public static class JsonParser implements MapFunction<String, Tuple3<String, Double, Long>> {
        private static final ObjectMapper mapper = new ObjectMapper();

        @Override
        public Tuple3<String, Double, Long> map(String value) throws Exception {
            try {
                JsonNode node = mapper.readTree(value);
                String eventType = node.has("event_type") ? node.get("event_type").asText() : "unknown";
                double valueField = node.has("value") ? node.get("value").asDouble() : 0.0;
                long timestamp = node.has("timestamp") ? node.get("timestamp").asLong() : System.currentTimeMillis();
                return new Tuple3<>(eventType, valueField, timestamp);
            } catch (Exception e) {
                System.err.println("Failed to parse JSON: " + value);
                return new Tuple3<>("error", 0.0, System.currentTimeMillis());
            }
        }
    }

    // Event Aggregator
    public static class EventAggregator implements AggregateFunction<
        Tuple3<String, Double, Long>, 
        Tuple3<String, Double, Integer>, 
        String> {

        @Override
        public Tuple3<String, Double, Integer> createAccumulator() {
            return new Tuple3<>("", 0.0, 0);
        }

        @Override
        public Tuple3<String, Double, Integer> add(
            Tuple3<String, Double, Long> value, 
            Tuple3<String, Double, Integer> accumulator) {
            return new Tuple3<>(
                value.f0, // event type
                accumulator.f1 + value.f1, // sum of values
                accumulator.f2 + 1 // count
            );
        }

        @Override
        public Tuple3<String, Double, Integer> merge(
            Tuple3<String, Double, Integer> a, 
            Tuple3<String, Double, Integer> b) {
            return new Tuple3<>(
                a.f0,
                a.f1 + b.f1,
                a.f2 + b.f2
            );
        }

        @Override
        public String getResult(Tuple3<String, Double, Integer> accumulator) {
            double average = accumulator.f2 > 0 ? accumulator.f1 / accumulator.f2 : 0.0;
            return String.format("{\"event_type\":\"%s\",\"count\":%d,\"sum\":%.2f,\"average\":%.2f,\"window_end\":%d}",
                accumulator.f0, accumulator.f2, accumulator.f1, average, System.currentTimeMillis());
        }
    }
}
