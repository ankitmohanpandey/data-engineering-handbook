#!/bin/bash

# Build script for Flink Stream Processing Application
# Uses Docker-based build - no local Maven required

echo "Building Flink Stream Processing Application using Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker Desktop first."
    exit 1
fi

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
