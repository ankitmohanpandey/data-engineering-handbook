"""
Basic Consumer Example - Apache Kafka

This example demonstrates:
1. Creating a basic Kafka consumer
2. Consuming messages from topics
3. Consumer groups
4. Offset management (auto vs manual commit)
5. Seeking to specific offsets
6. Consumer configuration

Run this example:
    python 02_basic_consumer.py
"""

from kafka import KafkaConsumer, TopicPartition
from kafka.errors import KafkaError
import json
import time

# ============================================================================
# EXAMPLE 1: Basic Consumer
# ============================================================================

def basic_consumer():
    """
    Create a simple consumer and read messages
    """
    print("=" * 60)
    print("EXAMPLE 1: Basic Consumer")
    print("=" * 60)
    
    # Create consumer
    consumer = KafkaConsumer(
        'test-topic',
        bootstrap_servers=['localhost:9092'],
        group_id='basic-consumer-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest'  # Start from beginning
    )
    
    print("Consuming messages (Press Ctrl+C to stop)...")
    print()
    
    try:
        message_count = 0
        for message in consumer:
            message_count += 1
            print(f"Message {message_count}:")
            print(f"  Topic: {message.topic}")
            print(f"  Partition: {message.partition}")
            print(f"  Offset: {message.offset}")
            print(f"  Key: {message.key}")
            print(f"  Value: {message.value}")
            print(f"  Timestamp: {message.timestamp}")
            print()
            
            # Stop after 10 messages for demo
            if message_count >= 10:
                break
    
    except KeyboardInterrupt:
        print("Stopping consumer...")
    
    finally:
        consumer.close()
        print(f"Consumed {message_count} messages\n")


# ============================================================================
# EXAMPLE 2: Consumer with Multiple Topics
# ============================================================================

def multi_topic_consumer():
    """
    Subscribe to multiple topics
    """
    print("=" * 60)
    print("EXAMPLE 2: Multi-Topic Consumer")
    print("=" * 60)
    
    consumer = KafkaConsumer(
        bootstrap_servers=['localhost:9092'],
        group_id='multi-topic-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest'
    )
    
    # Subscribe to multiple topics
    consumer.subscribe(['test-topic', 'user-events'])
    
    print("Subscribed to: test-topic, user-events")
    print("Consuming messages...")
    print()
    
    try:
        message_count = 0
        for message in consumer:
            message_count += 1
            print(f"[{message.topic}] Partition {message.partition}, "
                  f"Offset {message.offset}: {message.value}")
            
            if message_count >= 10:
                break
    
    except KeyboardInterrupt:
        print("Stopping consumer...")
    
    finally:
        consumer.close()
        print()


# ============================================================================
# EXAMPLE 3: Manual Offset Commit
# ============================================================================

def manual_commit_consumer():
    """
    Manually commit offsets after processing
    """
    print("=" * 60)
    print("EXAMPLE 3: Manual Offset Commit")
    print("=" * 60)
    
    consumer = KafkaConsumer(
        'test-topic',
        bootstrap_servers=['localhost:9092'],
        group_id='manual-commit-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=False,  # Disable auto-commit
        auto_offset_reset='earliest'
    )
    
    print("Manual commit mode enabled")
    print("Processing messages...")
    print()
    
    try:
        message_count = 0
        for message in consumer:
            message_count += 1
            
            # Process message
            print(f"Processing message {message_count}: {message.value}")
            
            # Simulate processing
            time.sleep(0.1)
            
            # Manually commit offset after successful processing
            consumer.commit()
            print(f"  ✓ Committed offset {message.offset}")
            print()
            
            if message_count >= 5:
                break
    
    except KeyboardInterrupt:
        print("Stopping consumer...")
    
    finally:
        consumer.close()
        print()


# ============================================================================
# EXAMPLE 4: Batch Processing with Manual Commit
# ============================================================================

def batch_commit_consumer():
    """
    Process messages in batches and commit periodically
    """
    print("=" * 60)
    print("EXAMPLE 4: Batch Processing")
    print("=" * 60)
    
    consumer = KafkaConsumer(
        'test-topic',
        bootstrap_servers=['localhost:9092'],
        group_id='batch-commit-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=False,
        auto_offset_reset='earliest'
    )
    
    print("Batch processing mode (commit every 5 messages)")
    print()
    
    try:
        batch = []
        batch_size = 5
        
        for message in consumer:
            batch.append(message.value)
            print(f"Added to batch: {message.value}")
            
            # Process batch when size reached
            if len(batch) >= batch_size:
                print(f"\nProcessing batch of {len(batch)} messages...")
                
                # Process batch
                for item in batch:
                    # Simulate processing
                    pass
                
                # Commit offset after batch processed
                consumer.commit()
                print(f"✓ Batch processed and committed")
                print()
                
                # Clear batch
                batch = []
                
                # Stop after one batch for demo
                break
    
    except KeyboardInterrupt:
        print("Stopping consumer...")
    
    finally:
        # Process remaining messages in batch
        if batch:
            print(f"Processing final batch of {len(batch)} messages...")
            consumer.commit()
        
        consumer.close()
        print()


# ============================================================================
# EXAMPLE 5: Seeking to Specific Offset
# ============================================================================

def seek_consumer():
    """
    Seek to specific offset or beginning/end
    """
    print("=" * 60)
    print("EXAMPLE 5: Seeking to Offsets")
    print("=" * 60)
    
    consumer = KafkaConsumer(
        'test-topic',
        bootstrap_servers=['localhost:9092'],
        group_id='seek-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=False
    )
    
    # Get assigned partitions
    consumer.poll(timeout_ms=1000)
    partitions = consumer.assignment()
    
    print(f"Assigned partitions: {partitions}")
    
    # Seek to beginning
    print("\n1. Seeking to beginning...")
    consumer.seek_to_beginning()
    
    message_count = 0
    for message in consumer:
        message_count += 1
        print(f"  Offset {message.offset}: {message.value}")
        if message_count >= 3:
            break
    
    # Seek to end
    print("\n2. Seeking to end...")
    consumer.seek_to_end()
    print("  At end of topic")
    
    # Seek to specific offset
    if partitions:
        partition = list(partitions)[0]
        print(f"\n3. Seeking to offset 5 in partition {partition.partition}...")
        consumer.seek(partition, 5)
        
        for message in consumer:
            print(f"  Offset {message.offset}: {message.value}")
            if message.offset >= 7:
                break
    
    consumer.close()
    print()


# ============================================================================
# EXAMPLE 6: Consumer with Configuration
# ============================================================================

def configured_consumer():
    """
    Create consumer with various configuration options
    """
    print("=" * 60)
    print("EXAMPLE 6: Consumer with Configuration")
    print("=" * 60)
    
    consumer = KafkaConsumer(
        'test-topic',
        
        # Broker connection
        bootstrap_servers=['localhost:9092'],
        
        # Consumer group
        group_id='configured-group',
        
        # Deserialization
        key_deserializer=lambda k: k.decode('utf-8') if k else None,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        
        # Offset management
        auto_offset_reset='earliest',  # earliest, latest, none
        enable_auto_commit=True,
        auto_commit_interval_ms=5000,  # Commit every 5 seconds
        
        # Fetch settings
        fetch_min_bytes=1,  # Minimum bytes to fetch
        fetch_max_wait_ms=500,  # Max wait time for fetch
        max_partition_fetch_bytes=1048576,  # 1MB per partition
        
        # Session management
        session_timeout_ms=10000,  # 10 seconds
        heartbeat_interval_ms=3000,  # 3 seconds
        
        # Consumer behavior
        max_poll_records=500,  # Max records per poll
        max_poll_interval_ms=300000,  # 5 minutes
    )
    
    print("Consumer configuration:")
    print(f"  - Group ID: configured-group")
    print(f"  - Auto offset reset: earliest")
    print(f"  - Auto commit: enabled (every 5s)")
    print(f"  - Session timeout: 10s")
    print(f"  - Max poll records: 500")
    print()
    
    try:
        message_count = 0
        for message in consumer:
            message_count += 1
            print(f"Message {message_count}: {message.value}")
            
            if message_count >= 5:
                break
    
    except KeyboardInterrupt:
        print("Stopping consumer...")
    
    finally:
        consumer.close()
        print()


# ============================================================================
# EXAMPLE 7: Partition Assignment
# ============================================================================

def partition_assignment():
    """
    Manually assign partitions instead of subscribing
    """
    print("=" * 60)
    print("EXAMPLE 7: Manual Partition Assignment")
    print("=" * 60)
    
    consumer = KafkaConsumer(
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest'
    )
    
    # Manually assign specific partitions
    partition_0 = TopicPartition('test-topic', 0)
    partition_1 = TopicPartition('test-topic', 1)
    
    consumer.assign([partition_0, partition_1])
    
    print(f"Manually assigned partitions: 0, 1")
    print()
    
    try:
        message_count = 0
        for message in consumer:
            message_count += 1
            print(f"Partition {message.partition}, Offset {message.offset}: "
                  f"{message.value}")
            
            if message_count >= 10:
                break
    
    except KeyboardInterrupt:
        print("Stopping consumer...")
    
    finally:
        consumer.close()
        print()


# ============================================================================
# EXAMPLE 8: Error Handling
# ============================================================================

def error_handling_consumer():
    """
    Demonstrate error handling in consumer
    """
    print("=" * 60)
    print("EXAMPLE 8: Error Handling")
    print("=" * 60)
    
    try:
        consumer = KafkaConsumer(
            'test-topic',
            bootstrap_servers=['localhost:9092'],
            group_id='error-handling-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            consumer_timeout_ms=5000  # Timeout after 5 seconds of no messages
        )
        
        print("Consuming with error handling...")
        print()
        
        message_count = 0
        for message in consumer:
            try:
                message_count += 1
                
                # Process message
                print(f"Processing: {message.value}")
                
                # Simulate processing that might fail
                if 'error' in str(message.value).lower():
                    raise ValueError("Simulated processing error")
                
                print(f"  ✓ Successfully processed")
                
            except ValueError as e:
                print(f"  ✗ Processing error: {e}")
                # Log error, send to dead letter queue, etc.
                continue
            
            except Exception as e:
                print(f"  ✗ Unexpected error: {e}")
                continue
            
            print()
            
            if message_count >= 5:
                break
        
        consumer.close()
        
    except KafkaError as e:
        print(f"Kafka error: {e}")
    
    except Exception as e:
        print(f"Consumer error: {e}")
    
    print()


# ============================================================================
# Main execution
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("KAFKA CONSUMER EXAMPLES")
    print("=" * 60 + "\n")
    
    print("NOTE: Make sure you have messages in 'test-topic'")
    print("Run 01_basic_producer.py first to produce messages\n")
    
    # Run examples
    basic_consumer()
    multi_topic_consumer()
    manual_commit_consumer()
    batch_commit_consumer()
    seek_consumer()
    configured_consumer()
    partition_assignment()
    error_handling_consumer()
    
    print("=" * 60)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 60)


"""
DETAILED EXPLANATION
====================

1. BASIC CONSUMER

   Steps to create consumer:
   1. Import KafkaConsumer
   2. Create consumer with topic(s) and bootstrap_servers
   3. Iterate over messages
   4. Process each message
   5. Close consumer

2. CONSUMER GROUPS

   Purpose:
   - Parallel processing
   - Load balancing
   - Fault tolerance
   
   Behavior:
   - Each partition consumed by one consumer in group
   - Consumers automatically rebalanced
   - Each group tracks its own offsets

3. OFFSET MANAGEMENT

   Auto-commit (default):
   - Offsets committed automatically
   - Interval: auto_commit_interval_ms
   - Risk: Message loss if consumer crashes
   
   Manual commit:
   - enable_auto_commit=False
   - Call consumer.commit() after processing
   - Better control, at-least-once delivery

4. AUTO_OFFSET_RESET

   earliest:
   - Start from beginning of topic
   - Use for new consumer groups
   
   latest:
   - Start from end of topic
   - Only consume new messages
   
   none:
   - Throw exception if no offset found
   - Strict offset management

5. DESERIALIZATION

   Deserializers convert bytes to Python objects:
   - value_deserializer: For message value
   - key_deserializer: For message key
   
   Common deserializers:
   - JSON: lambda m: json.loads(m.decode('utf-8'))
   - String: lambda m: m.decode('utf-8')
   - Bytes: No deserializer needed

6. SEEKING

   Methods:
   - seek(partition, offset): Specific offset
   - seek_to_beginning(): Start of topic
   - seek_to_end(): End of topic
   
   Use cases:
   - Replay messages
   - Skip to specific point
   - Reset processing

7. PARTITION ASSIGNMENT

   Subscribe (automatic):
   consumer.subscribe(['topic1', 'topic2'])
   - Automatic partition assignment
   - Automatic rebalancing
   
   Assign (manual):
   consumer.assign([TopicPartition('topic', 0)])
   - Manual partition control
   - No rebalancing

8. CONSUMER CONFIGURATION

   Key settings:
   - group_id: Consumer group identifier
   - auto_offset_reset: Where to start reading
   - enable_auto_commit: Auto vs manual commit
   - session_timeout_ms: Max time without heartbeat
   - max_poll_records: Messages per poll
   - fetch_min_bytes: Minimum fetch size
   - fetch_max_wait_ms: Max wait for fetch

9. REBALANCING

   Triggers:
   - Consumer joins group
   - Consumer leaves group
   - Consumer crashes
   - Partition count changes
   
   During rebalance:
   - Consumers stop processing
   - Partitions reassigned
   - Processing resumes

10. ERROR HANDLING

    Common errors:
    - KafkaError: General Kafka error
    - ConsumerTimeout: No messages within timeout
    - OffsetOutOfRangeError: Invalid offset
    
    Best practices:
    - Use try-except blocks
    - Log errors
    - Implement retry logic
    - Dead letter queue for failed messages

11. PERFORMANCE TIPS

    ✅ Use consumer groups for parallelism
    ✅ Tune fetch_min_bytes and fetch_max_wait_ms
    ✅ Batch process messages
    ✅ Use manual commit for better control
    ✅ Monitor consumer lag
    
    ❌ Don't process too slowly (causes rebalancing)
    ❌ Don't commit before processing (data loss)
    ❌ Don't ignore errors

12. CONSUMER LAG

    What is lag:
    - Difference between latest offset and consumer offset
    - Indicates processing delay
    
    Monitoring:
    kafka-consumer-groups.sh --describe \
      --group my-group \
      --bootstrap-server localhost:9092
    
    Reducing lag:
    - Add more consumers
    - Optimize processing
    - Increase partitions

13. AT-LEAST-ONCE vs AT-MOST-ONCE

    At-least-once (manual commit after processing):
    for message in consumer:
        process(message)
        consumer.commit()
    
    At-most-once (auto-commit or commit before processing):
    for message in consumer:
        consumer.commit()
        process(message)

14. TESTING

    # Start consumer
    python 02_basic_consumer.py
    
    # In another terminal, produce messages
    python 01_basic_producer.py
    
    # Check consumer group
    kafka-consumer-groups.sh --describe \
      --group basic-consumer-group \
      --bootstrap-server localhost:9092

15. PRODUCTION CHECKLIST

    ✅ Use consumer groups
    ✅ Enable manual commit for critical data
    ✅ Implement error handling
    ✅ Monitor consumer lag
    ✅ Set appropriate timeouts
    ✅ Handle rebalancing gracefully
    ✅ Log all errors
    ✅ Implement dead letter queue
"""
