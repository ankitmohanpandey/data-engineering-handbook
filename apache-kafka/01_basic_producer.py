"""
Basic Producer Example - Apache Kafka

This example demonstrates:
1. Creating a basic Kafka producer
2. Sending simple messages
3. Sending messages with keys
4. Synchronous vs asynchronous sending
5. Producer callbacks
6. Error handling

Run this example:
    python 01_basic_producer.py
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time

# ============================================================================
# EXAMPLE 1: Basic Producer
# ============================================================================

def basic_producer():
    """
    Create a simple producer and send messages
    """
    print("=" * 60)
    print("EXAMPLE 1: Basic Producer")
    print("=" * 60)
    
    # Create producer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Send messages
    for i in range(5):
        message = {'message_id': i, 'text': f'Hello Kafka {i}'}
        print(f"Sending: {message}")
        
        # Send message (asynchronous by default)
        producer.send('test-topic', message)
    
    # Flush to ensure all messages are sent
    producer.flush()
    print("All messages sent successfully!\n")
    
    producer.close()


# ============================================================================
# EXAMPLE 2: Producer with Keys
# ============================================================================

def producer_with_keys():
    """
    Send messages with keys for partitioning
    Messages with same key go to same partition
    """
    print("=" * 60)
    print("EXAMPLE 2: Producer with Keys")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        key_serializer=lambda k: k.encode('utf-8'),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Send messages with different keys
    users = ['user-1', 'user-2', 'user-3']
    
    for i in range(9):
        user = users[i % 3]
        message = {
            'user_id': user,
            'action': f'action-{i}',
            'timestamp': time.time()
        }
        
        print(f"Sending to key '{user}': {message}")
        
        # Messages with same key go to same partition
        producer.send('user-events', key=user, value=message)
    
    producer.flush()
    print("Messages with keys sent successfully!\n")
    
    producer.close()


# ============================================================================
# EXAMPLE 3: Synchronous Send
# ============================================================================

def synchronous_send():
    """
    Send messages synchronously (wait for acknowledgment)
    """
    print("=" * 60)
    print("EXAMPLE 3: Synchronous Send")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    for i in range(3):
        message = {'id': i, 'data': f'sync-message-{i}'}
        print(f"Sending synchronously: {message}")
        
        try:
            # .get() blocks until message is sent or timeout
            future = producer.send('test-topic', message)
            record_metadata = future.get(timeout=10)
            
            print(f"  ✓ Sent to partition {record_metadata.partition} "
                  f"at offset {record_metadata.offset}")
        except KafkaError as e:
            print(f"  ✗ Error: {e}")
    
    print()
    producer.close()


# ============================================================================
# EXAMPLE 4: Asynchronous Send with Callbacks
# ============================================================================

def async_with_callbacks():
    """
    Send messages asynchronously with success/error callbacks
    """
    print("=" * 60)
    print("EXAMPLE 4: Asynchronous Send with Callbacks")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Success callback
    def on_send_success(record_metadata):
        print(f"  ✓ Success! Topic: {record_metadata.topic}, "
              f"Partition: {record_metadata.partition}, "
              f"Offset: {record_metadata.offset}")
    
    # Error callback
    def on_send_error(excp):
        print(f"  ✗ Error occurred: {excp}")
    
    # Send messages with callbacks
    for i in range(3):
        message = {'id': i, 'data': f'async-message-{i}'}
        print(f"Sending asynchronously: {message}")
        
        future = producer.send('test-topic', message)
        future.add_callback(on_send_success)
        future.add_errback(on_send_error)
    
    # Wait for all messages to be sent
    producer.flush()
    print()
    
    producer.close()


# ============================================================================
# EXAMPLE 5: Producer with Configuration
# ============================================================================

def producer_with_config():
    """
    Create producer with various configuration options
    """
    print("=" * 60)
    print("EXAMPLE 5: Producer with Configuration")
    print("=" * 60)
    
    producer = KafkaProducer(
        # Broker connection
        bootstrap_servers=['localhost:9092'],
        
        # Serialization
        key_serializer=lambda k: k.encode('utf-8') if k else None,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        
        # Acknowledgments
        # 0: No acknowledgment (fastest, least safe)
        # 1: Leader acknowledgment (balanced)
        # 'all': All replicas acknowledgment (slowest, safest)
        acks='all',
        
        # Retries
        retries=3,
        retry_backoff_ms=100,
        
        # Batching for better throughput
        batch_size=16384,  # 16KB
        linger_ms=10,  # Wait up to 10ms to batch messages
        
        # Compression
        compression_type='gzip',  # None, gzip, snappy, lz4, zstd
        
        # Buffer
        buffer_memory=33554432,  # 32MB
        max_block_ms=60000,  # Block for max 60 seconds
        
        # Request timeout
        request_timeout_ms=30000,
    )
    
    print("Producer configuration:")
    print(f"  - Acknowledgments: all")
    print(f"  - Retries: 3")
    print(f"  - Compression: gzip")
    print(f"  - Batch size: 16KB")
    print(f"  - Linger: 10ms")
    
    # Send messages
    for i in range(5):
        message = {'id': i, 'data': f'configured-message-{i}'}
        producer.send('test-topic', message)
    
    producer.flush()
    print("Messages sent with custom configuration!\n")
    
    producer.close()


# ============================================================================
# EXAMPLE 6: Error Handling
# ============================================================================

def error_handling():
    """
    Demonstrate error handling in producer
    """
    print("=" * 60)
    print("EXAMPLE 6: Error Handling")
    print("=" * 60)
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=3,
            retry_backoff_ms=100
        )
        
        # Send message
        message = {'id': 1, 'data': 'test-message'}
        print(f"Sending: {message}")
        
        future = producer.send('test-topic', message)
        
        try:
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            print(f"  ✓ Message sent successfully to partition "
                  f"{record_metadata.partition} at offset {record_metadata.offset}")
        except KafkaError as e:
            print(f"  ✗ Failed to send message: {e}")
        
        producer.close()
        
    except Exception as e:
        print(f"Producer error: {e}")
    
    print()


# ============================================================================
# EXAMPLE 7: Sending Different Data Types
# ============================================================================

def different_data_types():
    """
    Send different types of data
    """
    print("=" * 60)
    print("EXAMPLE 7: Different Data Types")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Simple string data
    producer.send('test-topic', {'type': 'string', 'data': 'Hello'})
    print("Sent: String data")
    
    # Numeric data
    producer.send('test-topic', {'type': 'number', 'data': 12345})
    print("Sent: Numeric data")
    
    # List data
    producer.send('test-topic', {'type': 'list', 'data': [1, 2, 3, 4, 5]})
    print("Sent: List data")
    
    # Nested object
    producer.send('test-topic', {
        'type': 'nested',
        'data': {
            'user': {'id': 1, 'name': 'John'},
            'order': {'id': 100, 'total': 250.50}
        }
    })
    print("Sent: Nested object")
    
    # Timestamp data
    producer.send('test-topic', {
        'type': 'timestamp',
        'data': time.time(),
        'formatted': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    print("Sent: Timestamp data")
    
    producer.flush()
    print("All data types sent successfully!\n")
    
    producer.close()


# ============================================================================
# EXAMPLE 8: Batch Sending
# ============================================================================

def batch_sending():
    """
    Send messages in batches for better performance
    """
    print("=" * 60)
    print("EXAMPLE 8: Batch Sending")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        batch_size=16384,  # 16KB batch
        linger_ms=100  # Wait up to 100ms to fill batch
    )
    
    print("Sending 100 messages in batches...")
    start_time = time.time()
    
    for i in range(100):
        message = {
            'id': i,
            'data': f'batch-message-{i}',
            'timestamp': time.time()
        }
        producer.send('test-topic', message)
    
    producer.flush()
    
    elapsed = time.time() - start_time
    print(f"Sent 100 messages in {elapsed:.3f} seconds")
    print(f"Throughput: {100/elapsed:.2f} messages/second\n")
    
    producer.close()


# ============================================================================
# Main execution
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("KAFKA PRODUCER EXAMPLES")
    print("=" * 60 + "\n")
    
    # Run examples
    basic_producer()
    producer_with_keys()
    synchronous_send()
    async_with_callbacks()
    producer_with_config()
    error_handling()
    different_data_types()
    batch_sending()
    
    print("=" * 60)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 60)


"""
DETAILED EXPLANATION
====================

1. BASIC PRODUCER

   Steps to create producer:
   1. Import KafkaProducer
   2. Create producer instance with bootstrap_servers
   3. Send messages using .send()
   4. Flush to ensure delivery
   5. Close producer

2. SERIALIZATION

   Serializers convert Python objects to bytes:
   - value_serializer: For message value
   - key_serializer: For message key
   
   Common serializers:
   - JSON: lambda v: json.dumps(v).encode('utf-8')
   - String: lambda v: v.encode('utf-8')
   - Bytes: No serializer needed

3. MESSAGE KEYS

   Purpose of keys:
   - Partitioning: Same key → same partition
   - Ordering: Messages with same key are ordered
   - Compaction: Latest value per key retained
   
   Usage:
   producer.send('topic', key='user-123', value=data)

4. SYNCHRONOUS vs ASYNCHRONOUS

   Synchronous (blocking):
   future = producer.send('topic', data)
   metadata = future.get(timeout=10)  # Blocks
   
   Asynchronous (non-blocking):
   producer.send('topic', data)  # Returns immediately
   producer.flush()  # Wait for all

5. CALLBACKS

   Success callback:
   def on_success(metadata):
       print(f"Sent to {metadata.partition}")
   
   Error callback:
   def on_error(e):
       print(f"Error: {e}")
   
   Usage:
   future = producer.send('topic', data)
   future.add_callback(on_success)
   future.add_errback(on_error)

6. ACKNOWLEDGMENTS (acks)

   acks=0: No acknowledgment
   - Fastest
   - No guarantee
   - Possible data loss
   
   acks=1: Leader acknowledgment
   - Balanced
   - Leader confirms write
   - Possible data loss if leader fails
   
   acks='all': All replicas acknowledgment
   - Slowest
   - Highest durability
   - No data loss (if min.insync.replicas met)

7. BATCHING

   Benefits:
   - Higher throughput
   - Better compression
   - Reduced network overhead
   
   Configuration:
   - batch_size: Maximum batch size in bytes
   - linger_ms: Wait time to fill batch
   
   Trade-off: Latency vs throughput

8. COMPRESSION

   Types:
   - None: No compression (fastest)
   - gzip: Good compression, moderate CPU
   - snappy: Fast, moderate compression
   - lz4: Very fast, good compression
   - zstd: Best compression, moderate CPU
   
   Benefits:
   - Reduced network usage
   - Reduced storage
   - Lower bandwidth costs

9. RETRIES

   Configuration:
   - retries: Number of retry attempts
   - retry_backoff_ms: Wait between retries
   
   Automatic retry on:
   - Network errors
   - Broker unavailable
   - Leader election

10. ERROR HANDLING

    Common errors:
    - KafkaTimeoutError: Timeout waiting for send
    - KafkaError: General Kafka error
    - SerializationError: Serialization failed
    
    Best practices:
    - Use try-except blocks
    - Implement callbacks
    - Log errors
    - Monitor failed sends

11. PERFORMANCE TIPS

    ✅ Use batching (batch_size, linger_ms)
    ✅ Enable compression
    ✅ Use asynchronous sends
    ✅ Tune buffer_memory
    ✅ Use connection pooling
    
    ❌ Don't send very large messages
    ❌ Don't use synchronous sends for high throughput
    ❌ Don't ignore errors

12. TESTING

    # Start Kafka
    bin/kafka-server-start.sh config/server.properties
    
    # Create topic
    bin/kafka-topics.sh --create --topic test-topic \
      --bootstrap-server localhost:9092 --partitions 3
    
    # Run producer
    python 01_basic_producer.py
    
    # Verify messages
    bin/kafka-console-consumer.sh --topic test-topic \
      --bootstrap-server localhost:9092 --from-beginning

13. MONITORING

    Producer metrics:
    - record-send-rate: Messages sent per second
    - record-error-rate: Failed sends per second
    - request-latency-avg: Average request latency
    - batch-size-avg: Average batch size
    - compression-rate-avg: Compression ratio

14. PRODUCTION CHECKLIST

    ✅ Set acks='all' for durability
    ✅ Enable retries
    ✅ Use compression
    ✅ Implement error handling
    ✅ Monitor producer metrics
    ✅ Set appropriate timeouts
    ✅ Use connection pooling
    ✅ Log all errors
"""
