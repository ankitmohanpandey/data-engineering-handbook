#!/bin/bash

# Main orchestration script for Flink Stream Processing Application
# Fully containerized - no local Java/Maven required

set -e

echo "=== Flink Stream Processing Application Setup ==="

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "Docker is not running. Please start Docker Desktop first."
        exit 1
    fi
    echo "Docker is running ✓"
}

# Function to build the application using Docker
build_app() {
    echo "Building the application using Docker..."
    
    # Create build directory if it doesn't exist
    mkdir -p build/libs
    
    # Build using Docker
    docker run --rm \
        -v "$(pwd)":/app \
        -v "$(pwd)/build":/build \
        -w /app \
        maven:3.8.6-openjdk-11 \
        mvn clean package -DskipTests
    
    if [ $? -eq 0 ]; then
        # Copy the JAR to the expected location
        cp target/flink-stream-processing.jar build/libs/
        echo "Build successful! JAR file created in build/libs/"
        ls -lh build/libs/
    else
        echo "Build failed!"
        exit 1
    fi
}

# Function to start Docker containers
start_containers() {
    echo "Starting Docker containers..."
    
    # Create network if it doesn't exist
    docker network create flink-network 2>/dev/null || true
    
    docker-compose up -d
    
    echo "Waiting for services to be ready..."
    sleep 15
    
    # Check if Flink JobManager is ready
    echo "Checking Flink JobManager..."
    for i in {1..30}; do
        if curl -s http://localhost:8081 > /dev/null 2>&1; then
            echo "Flink JobManager is ready ✓"
            break
        fi
        echo "Waiting for Flink JobManager... ($i/30)"
        sleep 2
    done
    
    # Check if Kafka is ready
    echo "Checking Kafka..."
    for i in {1..30}; do
        if docker exec flink-kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
            echo "Kafka is ready ✓"
            break
        fi
        echo "Waiting for Kafka... ($i/30)"
        sleep 2
    done
}

# Function to create Kafka topics
create_topics() {
    echo "Creating Kafka topics..."
    docker exec flink-kafka kafka-topics --create --topic input-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --if-not-exists
    docker exec flink-kafka kafka-topics --create --topic output-events --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --if-not-exists
    echo "Kafka topics created ✓"
}

# Function to submit Flink job
submit_job() {
    echo "Submitting Flink job..."
    docker exec flink-jobmanager flink run -d /opt/flink/usrlib/flink-stream-processing.jar
    echo "Flink job submitted ✓"
}

# Function to start data generator
start_data_generator() {
    echo "Starting data generator..."
    echo "The data generator will start sending events to Kafka..."
    echo "Press Ctrl+C to stop the data generator."
    
    # Run data generator using Docker
    docker run --rm \
        -v "$(pwd)":/app \
        -w /app \
        --network flink-network \
        maven:3.8.6-openjdk-11 \
        mvn exec:java -Dexec.mainClass="com.flink.app.DataGenerator" -Dexec.args="kafka:29092"
}

# Function to stop everything
stop_all() {
    echo "Stopping Docker containers..."
    docker-compose down
    echo "All containers stopped ✓"
}

# Function to show logs
show_logs() {
    echo "Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f
}

# Main menu
case "${1:-}" in
    "build")
        check_docker
        build_app
        ;;
    "start")
        check_docker
        build_app
        start_containers
        create_topics
        submit_job
        echo ""
        echo "=== Setup Complete ==="
        echo "Flink Dashboard: http://localhost:8081"
        echo "Kafka: localhost:9092"
        echo ""
        echo "To start the data generator, run: ./run.sh generator"
        echo "To view logs, run: ./run.sh logs"
        echo "To stop everything, run: ./run.sh stop"
        ;;
    "generator")
        start_data_generator
        ;;
    "stop")
        stop_all
        ;;
    "logs")
        show_logs
        ;;
    "restart")
        stop_all
        start_containers
        create_topics
        submit_job
        ;;
    *)
        echo "Usage: ./run.sh {build|start|generator|stop|logs|restart}"
        echo ""
        echo "Commands:"
        echo "  build     - Build the application JAR using Docker"
        echo "  start     - Build and start the complete stack (Flink + Kafka + Job)"
        echo "  generator - Start the data generator (requires stack to be running)"
        echo "  stop      - Stop all Docker containers"
        echo "  logs      - Show logs from all containers"
        echo "  restart   - Restart the stack"
        echo ""
        echo "Note: This setup is fully containerized and does not require local Java/Maven."
        exit 1
        ;;
esac
