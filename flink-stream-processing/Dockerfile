FROM maven:3.8.6-openjdk-11

WORKDIR /app

# Copy pom.xml first for better Docker layer caching
COPY pom.xml .

# Download dependencies
RUN mvn dependency:go-offline -B

# Copy source code
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Copy the built JAR to a location that will be mounted
RUN mkdir -p /build && cp target/flink-stream-processing.jar /build/

# Set the working directory for the final image
WORKDIR /build