package com.flink.app;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;

import java.util.Properties;
import java.util.Random;
import java.util.concurrent.TimeUnit;

public class DataGenerator {
    
    private static final String[] EVENT_TYPES = {"click", "view", "purchase", "signup"};
    private static final Random random = new Random();
    
    public static void main(String[] args) throws InterruptedException {
        String bootstrapServers = args.length > 0 ? args[0] : "localhost:9092";
        
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        
        KafkaProducer<String, String> producer = new KafkaProducer<>(props);
        
        System.out.println("Starting data generator... (Press Ctrl+C to stop)");
        
        try {
            while (true) {
                String event = generateEvent();
                ProducerRecord<String, String> record = new ProducerRecord<>("input-events", event);
                producer.send(record);
                System.out.println("Sent event: " + event);
                TimeUnit.MILLISECONDS.sleep(500); // Send event every 500ms
            }
        } finally {
            producer.close();
        }
    }
    
    private static String generateEvent() {
        String eventType = EVENT_TYPES[random.nextInt(EVENT_TYPES.length)];
        double value = 10.0 + (random.nextDouble() * 90.0); // Random value between 10-100
        long timestamp = System.currentTimeMillis();
        
        return String.format("{\"event_type\":\"%s\",\"value\":%.2f,\"timestamp\":%d}", 
            eventType, value, timestamp);
    }
}
