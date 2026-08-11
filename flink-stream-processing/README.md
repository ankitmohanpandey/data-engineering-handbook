# Flink Stream Processing Application

A containerized Apache Flink stream processing application with Java and Kafka integration. This application demonstrates real-time event processing with windowing and aggregation capabilities.

## Overview

This project includes:
- **Apache Flink 1.18** for stream processing
- **Apache Kafka** for event streaming
- **Docker Compose** for easy container orchestration
- **Maven** for build management
- **Java 11** for application development

## Architecture

The application processes JSON events from a Kafka topic, performs windowed aggregations, and writes results to an output Kafka topic. All components run in Docker containers:

```
Docker Build → Maven Container → JAR File → Flink Containers
                                                    ↓
Data Generator (Docker) → Kafka (input-events) → Flink Job → Kafka (output-events)
                                                    ↓
                                               Console Output
```

### Stream Processing Pipeline

1. **Data Generator**: Produces JSON events with random data
2. **Kafka Source**: Consumes events from `input-events` topic
3. **JSON Parser**: Parses incoming JSON messages
4. **Window Aggregator**: Groups events by type and computes statistics (count, sum, average) in 10-second windows
5. **Kafka Sink**: Writes aggregated results to `output-events` topic
6. **Console Output**: Also prints results for debugging

## Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** (for cloning, if needed)

**Note**: This setup is fully containerized and does not require local Java or Maven installation.

## Quick Start

### 1. Start the Complete Stack

The easiest way to start everything is to use the provided orchestration script:

```bash
cd flink-stream-processing
./run.sh start
```

This command will:
- Build the application JAR
- Start Docker containers (Flink JobManager, TaskManager, Kafka, Zookeeper)
- Create Kafka topics
- Submit the Flink job

### 2. Generate Test Data

In a separate terminal, start the data generator:

```bash
cd flink-stream-processing
./run.sh generator
```

This will start sending JSON events to the Kafka topic every 500ms.

### 3. Monitor the Application

- **Flink Dashboard**: http://localhost:8081
- **View Logs**: `./run.sh logs`
- **Check Output**: The aggregated results will be printed to the Flink TaskManager logs

### 4. Stop Everything

```bash
./run.sh stop
```

## Manual Setup

If you prefer to run components individually:

### Build the Application

The build is now fully containerized:

```bash
./run.sh build
```

This uses Docker to build the application without requiring local Java/Maven.

### Start Docker Containers

```bash
docker-compose up -d
```

### Create Kafka Topics

```bash
docker exec flink-kafka kafka-topics --create --topic input-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --if-not-exists
docker exec flink-kafka kafka-topics --create --topic output-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --if-not-exists
```

### Submit Flink Job

```bash
docker exec flink-jobmanager flink run -d /opt/flink/usrlib/flink-stream-processing.jar
```

### Run Data Generator

```bash
./run.sh generator
```

This also runs inside Docker with the proper network configuration.

## Application Structure

```
flink-stream-processing/
├── docker-compose.yml          # Docker orchestration configuration
├── Dockerfile                   # Build container definition
├── pom.xml                      # Maven build configuration
├── build.sh                     # Docker-based build script
├── run.sh                       # Main orchestration script
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
├── src/
│   └── main/
│       ├── java/
│       │   └── com/
│       │       └── flink/
│       │           └── app/
│       │               ├── StreamProcessingJob.java    # Main Flink job
│       │               └── DataGenerator.java          # Test data generator
│       └── resources/
└── build/                       # Build output directory
    └── libs/
        └── flink-stream-processing.jar                # Deployable JAR
```

## Configuration

### Docker Compose Services

- **flink-jobmanager**: Flink JobManager (port 8081)
- **flink-taskmanager**: Flink TaskManager with 2 task slots
- **flink-kafka**: Kafka broker 7.4.0 (port 9092)
- **flink-zookeeper**: Zookeeper 7.4.0 for Kafka coordination (port 2181)

### Kafka Topics

- **input-events**: Input topic for raw JSON events
- **output-events**: Output topic for aggregated results

### Event Format

Input events follow this JSON format:

```json
{
  "event_type": "click|view|purchase|signup",
  "value": 10.0-100.0,
  "timestamp": 1234567890
}
```

Output events contain aggregated statistics:

```json
{
  "event_type": "click",
  "count": 5,
  "sum": 250.50,
  "average": 50.10,
  "window_end": 1234567890
}
```

## Stream Processing Logic

The Flink job implements the following processing pipeline:

1. **Source**: Reads from Kafka `input-events` topic
2. **Parse**: Converts JSON to structured data (event_type, value, timestamp)
3. **KeyBy**: Groups events by `event_type`
4. **Window**: 10-second tumbling windows
5. **Aggregate**: Computes count, sum, and average per window
6. **Sink**: Writes results to Kafka `output-events` topic

## Containerized Build Process

This application uses a fully containerized build process:

1. **Docker-based Build**: Maven runs inside a Docker container with Java 11 pre-installed
2. **No Local Dependencies**: You don't need Java or Maven on your host machine
3. **Network Isolation**: All services run in a dedicated Docker network
4. **Volume Mounting**: Source code and build artifacts are shared between containers

The build process uses the official Maven Docker image (`maven:3.8.6-openjdk-11`) to compile and package the application.

## Troubleshooting

### Docker Not Running

Start Docker Desktop and wait for it to fully initialize:

```bash
docker info
```

### Port Conflicts

If ports are already in use, modify the `docker-compose.yml` file:

```yaml
ports:
  - "8082:8081"  # Change Flink dashboard port
  - "9093:9092"  # Change Kafka port
```

### Build Failures

Since the build is containerized, check if Docker is working properly:

```bash
docker run --rm maven:3.8.6-openjdk-11 mvn -version
```

### Docker Issues

Check if Docker is running:

```bash
docker info
```

### Kafka Connection Issues

Verify Kafka is ready:

```bash
docker exec flink-kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

### Flink Job Submission Issues

Check the Flink logs:

```bash
docker logs flink-jobmanager
docker logs flink-taskmanager
```

## Development

### Modify the Stream Processing Job

Edit `src/main/java/com/flink/app/StreamProcessingJob.java` to customize:
- Window sizes
- Aggregation logic
- Kafka topics
- Event parsing

### Modify the Data Generator

Edit `src/main/java/com/flink/app/DataGenerator.java` to customize:
- Event types
- Value ranges
- Generation frequency

### Rebuild After Changes

```bash
./run.sh build
docker-compose restart jobmanager taskmanager
```

Then resubmit the job:

```bash
docker exec flink-jobmanager flink run -d /opt/flink/usrlib/flink-stream-processing.jar
```

## Technology Stack

- **Apache Flink 1.18**: Stream processing framework
- **Apache Kafka 7.4.0**: Distributed event streaming platform
- **Java 11**: Programming language
- **Maven 3.10.1**: Build and dependency management
- **Docker & Docker Compose**: Container orchestration
- **Jackson 2.15.2**: JSON processing

## License

This is a demonstration project for educational purposes.

## Support

For issues with:
- **Flink**: https://flink.apache.org/
- **Kafka**: https://kafka.apache.org/
- **Docker**: https://www.docker.com/