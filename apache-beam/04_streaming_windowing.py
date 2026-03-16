"""
Example 4: Streaming Data with Windowing

This example demonstrates:
- Simulating streaming data
- Fixed time windows
- Sliding windows
- Session windows
- Triggers and late data handling

WHAT IT DOES:
Simulates a stream of events and applies different windowing strategies.

HOW TO RUN:
python 04_streaming_windowing.py

EXPECTED OUTPUT:
Files showing windowed aggregations of streaming data.

NOTE: This uses simulated streaming with timestamps. For real streaming,
you'd connect to sources like Pub/Sub, Kafka, or Kinesis.
"""

import apache_beam as beam
from apache_beam import window
from apache_beam.transforms.window import TimestampedValue
from datetime import datetime, timedelta


def run_fixed_windows():
    """
    Fixed Windows: Non-overlapping time intervals
    Example: Every 1 minute window
    
    Timeline:
    [0-60s] [60-120s] [120-180s]
    """
    # Simulated click events: (user_id, page, timestamp_offset_seconds)
    events = [
        ('user1', '/home', 5),
        ('user2', '/products', 10),
        ('user1', '/cart', 15),
        ('user3', '/home', 65),      # Next window
        ('user2', '/checkout', 70),   # Next window
        ('user1', '/home', 125),      # Third window
    ]
    
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'CreateEvents' >> beam.Create(events)
            # Add timestamps to elements
            | 'AddTimestamps' >> beam.Map(
                lambda x: TimestampedValue(
                    (x[0], x[1]),  # (user_id, page)
                    x[2]           # timestamp in seconds
                )
            )
            # Apply 60-second fixed windows
            | 'FixedWindow' >> beam.WindowInto(window.FixedWindows(60))
            # Count events per window
            | 'CountPerWindow' >> beam.combiners.Count.Globally()
            # Format output with window info
            | 'FormatFixed' >> beam.Map(
                lambda count, window=beam.DoFn.WindowParam: 
                    f'Window [{window.start}s - {window.end}s]: {count} events'
            )
            | 'WriteFixed' >> beam.io.WriteToText('output/fixed_windows')
        )
    
    print("✅ Fixed windows example completed!")


def run_sliding_windows():
    """
    Sliding Windows: Overlapping time intervals
    Example: 60-second window, sliding every 30 seconds
    
    Timeline:
    [0-60s]
       [30-90s]
          [60-120s]
             [90-150s]
    """
    events = [
        ('user1', 100, 10),   # In windows: [0-60], [0-90] (if exists)
        ('user2', 200, 40),   # In windows: [0-60], [30-90]
        ('user3', 150, 70),   # In windows: [30-90], [60-120]
        ('user1', 300, 100),  # In windows: [60-120], [90-150]
    ]
    
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'CreatePurchases' >> beam.Create(events)
            | 'AddTimestamps' >> beam.Map(
                lambda x: TimestampedValue(
                    ('purchase', x[1]),  # ('purchase', amount)
                    x[2]                 # timestamp
                )
            )
            # 60-second windows, sliding every 30 seconds
            | 'SlidingWindow' >> beam.WindowInto(
                window.SlidingWindows(60, 30)  # size=60s, period=30s
            )
            # Sum amounts per window
            | 'ExtractAmount' >> beam.Map(lambda x: x[1])
            | 'SumPerWindow' >> beam.CombineGlobally(sum).without_defaults()
            | 'FormatSliding' >> beam.Map(
                lambda total, window=beam.DoFn.WindowParam:
                    f'Window [{window.start}s - {window.end}s]: ${total}'
            )
            | 'WriteSliding' >> beam.io.WriteToText('output/sliding_windows')
        )
    
    print("✅ Sliding windows example completed!")


def run_session_windows():
    """
    Session Windows: Dynamic windows based on activity gaps
    Example: Group events with gaps < 30 seconds into same session
    
    Timeline:
    Event1 Event2 ----gap(>30s)---- Event3 Event4
    [--- Session 1 ---]             [-- Session 2 --]
    """
    # User activity events with gaps
    events = [
        ('user1', 'login', 0),
        ('user1', 'view_product', 10),
        ('user1', 'add_to_cart', 20),
        # 50-second gap (new session starts)
        ('user1', 'login', 70),
        ('user1', 'checkout', 80),
        # Another user
        ('user2', 'login', 5),
        ('user2', 'view_product', 15),
    ]
    
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'CreateActivity' >> beam.Create(events)
            | 'AddTimestamps' >> beam.Map(
                lambda x: TimestampedValue(
                    (x[0], x[1]),  # (user_id, action)
                    x[2]           # timestamp
                )
            )
            # Session windows with 30-second gap
            | 'SessionWindow' >> beam.WindowInto(
                window.Sessions(30)  # gap_size=30s
            )
            # Group by user and count actions per session
            | 'ExtractUser' >> beam.Map(lambda x: (x[0], 1))
            | 'CountPerSession' >> beam.CombinePerKey(sum)
            | 'FormatSession' >> beam.Map(
                lambda kv, window=beam.DoFn.WindowParam:
                    f'{kv[0]} - Session [{window.start}s - {window.end}s]: '
                    f'{kv[1]} actions'
            )
            | 'WriteSession' >> beam.io.WriteToText('output/session_windows')
        )
    
    print("✅ Session windows example completed!")


def run_with_triggers():
    """
    Triggers: Control when results are emitted
    
    Useful for:
    - Early results (before window closes)
    - Late data handling (after window closes)
    - Speculative results
    """
    events = [
        ('sensor1', 23.5, 10),
        ('sensor1', 24.0, 20),
        ('sensor1', 23.8, 30),
        ('sensor1', 25.0, 40),
        ('sensor1', 24.5, 50),
    ]
    
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'CreateReadings' >> beam.Create(events)
            | 'AddTimestamps' >> beam.Map(
                lambda x: TimestampedValue(
                    (x[0], x[1]),  # (sensor_id, temperature)
                    x[2]
                )
            )
            | 'Window' >> beam.WindowInto(
                window.FixedWindows(60),
                # Trigger: Emit results every 20 seconds AND at window end
                trigger=beam.trigger.AfterWatermark(
                    early=beam.trigger.AfterProcessingTime(20),
                    late=beam.trigger.AfterCount(1)
                ),
                accumulation_mode=beam.trigger.AccumulationMode.ACCUMULATING
            )
            | 'ExtractTemp' >> beam.Map(lambda x: x[1])
            | 'AvgTemp' >> beam.CombineGlobally(
                beam.combiners.MeanCombineFn()
            ).without_defaults()
            | 'FormatTrigger' >> beam.Map(
                lambda avg, window=beam.DoFn.WindowParam:
                    f'Window [{window.start}s - {window.end}s]: '
                    f'Avg temp = {avg:.2f}°C'
            )
            | 'WriteTrigger' >> beam.io.WriteToText('output/triggered_windows')
        )
    
    print("✅ Triggers example completed!")


# DETAILED EXPLANATION:
"""
WINDOWING CONCEPTS:

1. Event Time vs Processing Time:
   - Event Time: When the event actually occurred (embedded in data)
   - Processing Time: When the system processes the event
   - Beam uses Event Time by default (more accurate for analytics)

2. Watermark:
   - Tracks progress of event time in the pipeline
   - Indicates "all data before time T has been processed"
   - Helps determine when to close windows

3. Window Types:

   a) Fixed Windows (Tumbling):
      - Non-overlapping, fixed-size intervals
      - Use case: Hourly/daily aggregations
      - Example: [0-60s], [60-120s], [120-180s]
   
   b) Sliding Windows (Hopping):
      - Overlapping, fixed-size intervals
      - Use case: Moving averages, trend analysis
      - Example: 60s window, sliding every 30s
   
   c) Session Windows:
      - Dynamic windows based on activity gaps
      - Use case: User sessions, activity tracking
      - Example: Group events with <30s gap
   
   d) Global Window:
      - Default, entire dataset as one window
      - Use case: Batch processing

4. Triggers:
   - Control when results are emitted
   - Types:
     * AfterWatermark: After window closes (default)
     * AfterProcessingTime: After certain processing time
     * AfterCount: After N elements
     * Repeatedly: Emit multiple times
   
5. Accumulation Modes:
   - DISCARDING: Each pane is independent
   - ACCUMULATING: Each pane includes previous data

6. Late Data:
   - Data arriving after watermark passes window end
   - Can be handled with late triggers
   - Set allowed_lateness parameter

REAL-WORLD STREAMING SOURCES:
- Google Cloud Pub/Sub: beam.io.ReadFromPubSub()
- Apache Kafka: beam.io.ReadFromKafka()
- AWS Kinesis: beam.io.ReadFromKinesis()
- Files (simulated streaming): beam.io.ReadFromText() with watch parameter
"""


if __name__ == '__main__':
    print("Running Streaming and Windowing Examples...")
    print("=" * 60)
    
    print("\n1. Fixed Windows")
    print("-" * 60)
    run_fixed_windows()
    
    print("\n2. Sliding Windows")
    print("-" * 60)
    run_sliding_windows()
    
    print("\n3. Session Windows")
    print("-" * 60)
    run_session_windows()
    
    print("\n4. Triggers")
    print("-" * 60)
    run_with_triggers()
    
    print("\n" + "=" * 60)
    print("✅ All streaming examples completed!")
    print("Check output/ directory for results.")
