"""
Advanced Producer Example - Apache Kafka

This example demonstrates:
1. Custom partitioners
2. Transactions
3. Idempotent producer
4. Producer interceptors
5. Compression strategies
6. Performance optimization

Run this example:
    python 03_advanced_producer.py
"""

from kafka import KafkaProducer
from kafka.partitioner import Partitioner
from kafka.errors import KafkaError
import json
import time
import hashlib

# ============================================================================
# EXAMPLE 1: Custom Partitioner
# ============================================================================

class CustomPartitioner(Partitioner):
    """
    Custom partitioner that routes messages based on custom logic
    """
    
    def partition(self, key, all_partitions, available_partitions):
        """
        Determine partition for message
        
        Args:
            key: Message key
            all_partitions: List of all partition IDs
            available_partitions: List of available partition IDs
        
        Returns:
            Partition ID
        """
        if key is None:
            # Round-robin for messages without key
            return all_partitions[0]
        
        # Hash-based partitioning for messages with key
        key_hash = int(hashlib.md5(key).hexdigest(), 16)
        return all_partitions[key_hash % len(all_partitions)]


def custom_partitioner_example():
    """
    Use custom partitioner for message routing
    """
    print("=" * 60)
    print("EXAMPLE 1: Custom Partitioner")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        key_serializer=lambda k: k.encode('utf-8'),
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        partitioner=CustomPartitioner()
    )
    
    print("Using custom partitioner...")
    
    # Send messages with different keys
    for i in range(10):
        key = f"key-{i % 3}"  # 3 different keys
        message = {'id': i, 'key': key, 'data': f'message-{i}'}
        
        future = producer.send('test-topic', key=key, value=message)
        metadata = future.get(timeout=10)
        
        print(f"Key '{key}' → Partition {metadata.partition}")
    
    producer.flush()
    producer.close()
    print()


# ============================================================================
# EXAMPLE 2: Idempotent Producer
# ============================================================================

def idempotent_producer_example():
    """
    Enable idempotence to prevent duplicate messages
    """
    print("=" * 60)
    print("EXAMPLE 2: Idempotent Producer")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        
        # Enable idempotence
        enable_idempotence=True,
        
        # Required settings for idempotence
        acks='all',
        retries=3,
        max_in_flight_requests_per_connection=5
    )
    
    print("Idempotent producer enabled")
    print("Configuration:")
    print("  - enable_idempotence: True")
    print("  - acks: all")
    print("  - retries: 3")
    print()
    
    # Send messages
    for i in range(5):
        message = {'id': i, 'data': f'idempotent-message-{i}'}
        print(f"Sending: {message}")
        
        future = producer.send('test-topic', message)
        metadata = future.get(timeout=10)
        
        print(f"  ✓ Sent to partition {metadata.partition} at offset {metadata.offset}")
    
    producer.flush()
    producer.close()
    print("\nIdempotence ensures no duplicates even with retries!\n")


# ============================================================================
# EXAMPLE 3: Transactional Producer
# ============================================================================

def transactional_producer_example():
    """
    Use transactions for exactly-once semantics
    """
    print("=" * 60)
    print("EXAMPLE 3: Transactional Producer")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        
        # Enable transactions
        transactional_id='my-transactional-producer',
        enable_idempotence=True,
        acks='all'
    )
    
    # Initialize transactions
    producer.init_transactions()
    
    print("Transactional producer initialized")
    print()
    
    try:
        # Begin transaction
        producer.begin_transaction()
        print("Transaction started")
        
        # Send multiple messages in transaction
        for i in range(3):
            message = {'id': i, 'data': f'transactional-message-{i}'}
            print(f"Sending in transaction: {message}")
            producer.send('test-topic', message)
        
        # Simulate additional operation
        print("Performing additional operations...")
        time.sleep(0.5)
        
        # Commit transaction
        producer.commit_transaction()
        print("✓ Transaction committed successfully")
        print("All messages are now visible to consumers\n")
        
    except Exception as e:
        print(f"✗ Error occurred: {e}")
        print("Aborting transaction...")
        producer.abort_transaction()
        print("Transaction aborted - no messages sent\n")
    
    finally:
        producer.close()


# ============================================================================
# EXAMPLE 4: Compression Comparison
# ============================================================================

def compression_comparison():
    """
    Compare different compression types
    """
    print("=" * 60)
    print("EXAMPLE 4: Compression Comparison")
    print("=" * 60)
    
    # Large message for compression testing
    large_message = {
        'id': 1,
        'data': 'x' * 10000,  # 10KB of data
        'metadata': {
            'timestamp': time.time(),
            'source': 'compression-test'
        }
    }
    
    compression_types = ['none', 'gzip', 'snappy', 'lz4']
    
    for comp_type in compression_types:
        print(f"\nTesting {comp_type.upper()} compression:")
        
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type=comp_type if comp_type != 'none' else None
        )
        
        start_time = time.time()
        
        # Send 10 messages
        for i in range(10):
            producer.send('test-topic', large_message)
        
        producer.flush()
        elapsed = time.time() - start_time
        
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Throughput: {10/elapsed:.2f} messages/sec")
        
        producer.close()
    
    print("\nCompression reduces network usage and storage!")
    print("Trade-off: CPU usage vs network/storage\n")


# ============================================================================
# EXAMPLE 5: Batching Optimization
# ============================================================================

def batching_optimization():
    """
    Optimize throughput with batching
    """
    print("=" * 60)
    print("EXAMPLE 5: Batching Optimization")
    print("=" * 60)
    
    configs = [
        {'name': 'No batching', 'batch_size': 1, 'linger_ms': 0},
        {'name': 'Small batches', 'batch_size': 1024, 'linger_ms': 10},
        {'name': 'Large batches', 'batch_size': 16384, 'linger_ms': 100},
    ]
    
    for config in configs:
        print(f"\n{config['name']}:")
        print(f"  batch_size: {config['batch_size']} bytes")
        print(f"  linger_ms: {config['linger_ms']} ms")
        
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=config['batch_size'],
            linger_ms=config['linger_ms']
        )
        
        start_time = time.time()
        
        # Send 100 messages
        for i in range(100):
            message = {'id': i, 'data': f'batch-test-{i}'}
            producer.send('test-topic', message)
        
        producer.flush()
        elapsed = time.time() - start_time
        
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Throughput: {100/elapsed:.2f} messages/sec")
        
        producer.close()
    
    print("\nBatching improves throughput significantly!")
    print("Trade-off: Latency vs throughput\n")


# ============================================================================
# EXAMPLE 6: Message Headers
# ============================================================================

def message_headers_example():
    """
    Add metadata using message headers
    """
    print("=" * 60)
    print("EXAMPLE 6: Message Headers")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Send message with headers
    headers = [
        ('source', b'python-producer'),
        ('version', b'1.0'),
        ('timestamp', str(time.time()).encode('utf-8')),
        ('content-type', b'application/json')
    ]
    
    message = {'id': 1, 'data': 'message with headers'}
    
    print(f"Sending message with headers:")
    print(f"  Message: {message}")
    print(f"  Headers: {headers}")
    
    future = producer.send(
        'test-topic',
        value=message,
        headers=headers
    )
    
    metadata = future.get(timeout=10)
    print(f"  ✓ Sent to partition {metadata.partition} at offset {metadata.offset}")
    
    producer.flush()
    producer.close()
    print("\nHeaders are useful for metadata, routing, and filtering!\n")


# ============================================================================
# EXAMPLE 7: Callback Chaining
# ============================================================================

def callback_chaining():
    """
    Chain multiple callbacks for complex workflows
    """
    print("=" * 60)
    print("EXAMPLE 7: Callback Chaining")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Multiple callbacks
    def log_success(metadata):
        print(f"  [LOG] Message sent to {metadata.topic}:{metadata.partition}:{metadata.offset}")
    
    def update_metrics(metadata):
        print(f"  [METRICS] Updated send counter")
    
    def notify_monitoring(metadata):
        print(f"  [MONITOR] Notified monitoring system")
    
    def handle_error(exception):
        print(f"  [ERROR] Failed to send: {exception}")
    
    # Send message with multiple callbacks
    message = {'id': 1, 'data': 'callback-chain-test'}
    print(f"Sending: {message}")
    
    future = producer.send('test-topic', message)
    
    # Add multiple callbacks
    future.add_callback(log_success)
    future.add_callback(update_metrics)
    future.add_callback(notify_monitoring)
    future.add_errback(handle_error)
    
    producer.flush()
    producer.close()
    print()


# ============================================================================
# EXAMPLE 8: Performance Monitoring
# ============================================================================

def performance_monitoring():
    """
    Monitor producer performance metrics
    """
    print("=" * 60)
    print("EXAMPLE 8: Performance Monitoring")
    print("=" * 60)
    
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        batch_size=16384,
        linger_ms=10,
        compression_type='gzip'
    )
    
    print("Sending messages and collecting metrics...")
    
    start_time = time.time()
    message_count = 100
    
    # Send messages
    for i in range(message_count):
        message = {'id': i, 'data': f'perf-test-{i}', 'timestamp': time.time()}
        producer.send('test-topic', message)
    
    producer.flush()
    elapsed = time.time() - start_time
    
    # Calculate metrics
    print("\nPerformance Metrics:")
    print(f"  Total messages: {message_count}")
    print(f"  Total time: {elapsed:.3f}s")
    print(f"  Throughput: {message_count/elapsed:.2f} messages/sec")
    print(f"  Average latency: {(elapsed/message_count)*1000:.2f}ms per message")
    
    # Get producer metrics (if available)
    try:
        metrics = producer.metrics()
        if metrics:
            print("\nProducer Metrics:")
            for metric_name, metric_value in list(metrics.items())[:5]:
                print(f"  {metric_name}: {metric_value}")
    except:
        print("\nDetailed metrics not available in this version")
    
    producer.close()
    print()


# ============================================================================
# Main execution
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("KAFKA ADVANCED PRODUCER EXAMPLES")
    print("=" * 60 + "\n")
    
    # Run examples
    custom_partitioner_example()
    idempotent_producer_example()
    transactional_producer_example()
    compression_comparison()
    batching_optimization()
    message_headers_example()
    callback_chaining()
    performance_monitoring()
    
    print("=" * 60)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 60)


"""
DETAILED EXPLANATION
====================

1. CUSTOM PARTITIONER

   Purpose:
   - Control message routing
   - Implement custom logic
   - Optimize data distribution
   
   Implementation:
   class CustomPartitioner(Partitioner):
       def partition(self, key, all_partitions, available_partitions):
           # Custom logic
           return partition_id
   
   Use cases:
   - Geographic routing
   - Load balancing
   - Data locality

2. IDEMPOTENT PRODUCER

   What is idempotence:
   - Prevents duplicate messages
   - Safe to retry
   - Exactly-once delivery to partition
   
   Configuration:
   enable_idempotence=True
   acks='all'
   retries > 0
   max_in_flight_requests_per_connection <= 5
   
   Benefits:
   - No duplicates on retry
   - Stronger guarantees
   - Safe for critical data

3. TRANSACTIONAL PRODUCER

   Purpose:
   - Atomic multi-message sends
   - Exactly-once semantics
   - All-or-nothing delivery
   
   Usage:
   producer.init_transactions()
   producer.begin_transaction()
   # Send messages
   producer.commit_transaction()
   # or
   producer.abort_transaction()
   
   Use cases:
   - Multi-topic writes
   - Database + Kafka updates
   - Critical workflows

4. COMPRESSION

   Types and characteristics:
   
   None:
   - No compression
   - Fastest
   - Highest network usage
   
   gzip:
   - Best compression ratio
   - Moderate CPU
   - Good for text data
   
   snappy:
   - Fast compression
   - Moderate ratio
   - Low CPU overhead
   
   lz4:
   - Very fast
   - Good compression
   - Recommended for most cases
   
   zstd:
   - Best compression
   - Moderate CPU
   - Newest option

5. BATCHING

   Parameters:
   - batch_size: Max batch size in bytes
   - linger_ms: Wait time to fill batch
   
   Benefits:
   - Higher throughput
   - Better compression
   - Reduced network overhead
   
   Trade-offs:
   - Increased latency
   - Memory usage
   
   Tuning:
   - High throughput: Large batch_size, higher linger_ms
   - Low latency: Small batch_size, low linger_ms

6. MESSAGE HEADERS

   Purpose:
   - Add metadata
   - Routing information
   - Tracing/correlation IDs
   - Content type
   
   Usage:
   headers = [
       ('key1', b'value1'),
       ('key2', b'value2')
   ]
   producer.send('topic', value=data, headers=headers)
   
   Use cases:
   - Message routing
   - Filtering
   - Tracing
   - Versioning

7. CALLBACKS

   Types:
   - Success callback: Called on successful send
   - Error callback: Called on failure
   
   Multiple callbacks:
   future.add_callback(callback1)
   future.add_callback(callback2)
   future.add_errback(error_handler)
   
   Use cases:
   - Logging
   - Metrics
   - Notifications
   - Error handling

8. PERFORMANCE OPTIMIZATION

   Key strategies:
   ✅ Enable batching
   ✅ Use compression
   ✅ Tune buffer_memory
   ✅ Optimize batch_size and linger_ms
   ✅ Use async sends
   ✅ Monitor metrics
   
   Metrics to monitor:
   - record-send-rate
   - record-error-rate
   - request-latency-avg
   - batch-size-avg
   - compression-rate-avg

9. EXACTLY-ONCE SEMANTICS

   Requirements:
   - Idempotent producer
   - Transactions
   - Consumer with isolation_level='read_committed'
   
   Configuration:
   producer = KafkaProducer(
       enable_idempotence=True,
       transactional_id='my-id',
       acks='all'
   )

10. PARTITIONING STRATEGIES

    Default (round-robin):
    - No key specified
    - Even distribution
    
    Key-based:
    - Hash of key
    - Same key → same partition
    - Maintains order per key
    
    Custom:
    - Implement Partitioner
    - Custom logic
    - Full control

11. PRODUCER GUARANTEES

    acks=0:
    - No guarantee
    - Fire and forget
    - Highest throughput
    
    acks=1:
    - Leader acknowledgment
    - Balanced
    - Possible data loss
    
    acks='all':
    - All ISR acknowledgment
    - Strongest guarantee
    - Lowest throughput

12. BEST PRACTICES

    ✅ Use idempotence for critical data
    ✅ Enable compression
    ✅ Tune batching for use case
    ✅ Monitor producer metrics
    ✅ Implement proper error handling
    ✅ Use transactions for multi-message atomicity
    ✅ Set appropriate timeouts
    
    ❌ Don't ignore errors
    ❌ Don't use acks=0 for critical data
    ❌ Don't send very large messages
    ❌ Don't block on synchronous sends

13. TESTING

    # Create topic with multiple partitions
    kafka-topics.sh --create --topic test-topic \
      --bootstrap-server localhost:9092 \
      --partitions 3 --replication-factor 1
    
    # Run producer
    python 03_advanced_producer.py
    
    # Verify messages
    kafka-console-consumer.sh --topic test-topic \
      --bootstrap-server localhost:9092 --from-beginning

14. MONITORING

    Key metrics:
    - Throughput (messages/sec)
    - Latency (ms per message)
    - Error rate
    - Batch size
    - Compression ratio
    
    Tools:
    - JMX metrics
    - Prometheus
    - Grafana
    - Kafka Manager

15. PRODUCTION CHECKLIST

    ✅ Enable idempotence
    ✅ Set acks='all' for durability
    ✅ Configure retries
    ✅ Use compression
    ✅ Tune batching
    ✅ Implement error handling
    ✅ Monitor metrics
    ✅ Set timeouts
    ✅ Use transactions if needed
    ✅ Test failover scenarios
"""
