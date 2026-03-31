# Apache Hadoop Setup Guide

> **Complete installation and configuration guide for Apache Hadoop**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Single Node Setup](#single-node-setup)
4. [Multi-Node Cluster Setup](#multi-node-cluster-setup)
5. [Verification](#verification)
6. [Common Commands](#common-commands)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum**:
- 4GB RAM
- 20GB disk space
- 2 CPU cores

**Recommended**:
- 8GB+ RAM
- 50GB+ disk space
- 4+ CPU cores

### Software Requirements

1. **Java (Required)**
   ```bash
   # Install Java 8 or 11
   # Ubuntu/Debian
   sudo apt update
   sudo apt install openjdk-11-jdk
   
   # macOS
   brew install openjdk@11
   
   # Verify
   java -version
   ```

2. **SSH (Required)**
   ```bash
   # Ubuntu/Debian
   sudo apt install openssh-server openssh-client
   
   # macOS (already installed)
   
   # Setup passwordless SSH
   ssh-keygen -t rsa -P ""
   cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   
   # Test
   ssh localhost
   ```

3. **Python (Optional - for examples)**
   ```bash
   python3 --version  # Should be 3.7+
   pip3 install -r requirements.txt
   ```

---

## Installation Methods

### Method 1: Download Binary (Recommended)

```bash
# 1. Download Hadoop
cd ~
wget https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz

# 2. Extract
tar -xzf hadoop-3.3.6.tar.gz
mv hadoop-3.3.6 hadoop

# 3. Set environment variables
echo 'export HADOOP_HOME=~/hadoop' >> ~/.bashrc
echo 'export HADOOP_INSTALL=$HADOOP_HOME' >> ~/.bashrc
echo 'export HADOOP_MAPRED_HOME=$HADOOP_HOME' >> ~/.bashrc
echo 'export HADOOP_COMMON_HOME=$HADOOP_HOME' >> ~/.bashrc
echo 'export HADOOP_HDFS_HOME=$HADOOP_HOME' >> ~/.bashrc
echo 'export YARN_HOME=$HADOOP_HOME' >> ~/.bashrc
echo 'export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native' >> ~/.bashrc
echo 'export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin' >> ~/.bashrc
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc  # Adjust path

# 4. Reload
source ~/.bashrc

# 5. Verify
hadoop version
```

### Method 2: Using Docker

```bash
# Pull Hadoop Docker image
docker pull apache/hadoop:3.3.6

# Run container
docker run -it -p 9870:9870 -p 8088:8088 apache/hadoop:3.3.6 bash
```

### Method 3: Using Package Manager (Ubuntu)

```bash
# Add repository
sudo add-apt-repository ppa:hadoop/stable
sudo apt update

# Install
sudo apt install hadoop
```

---

## Single Node Setup

### Step 1: Configure Hadoop

#### 1.1 Edit `hadoop-env.sh`

```bash
# Open file
nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# Add/Update JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Adjust your path
```

#### 1.2 Edit `core-site.xml`

```bash
nano $HADOOP_HOME/etc/hadoop/core-site.xml
```

Add:
```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
    <property>
        <name>hadoop.tmp.dir</name>
        <value>/home/YOUR_USERNAME/hadoop_tmp</value>
    </property>
</configuration>
```

#### 1.3 Edit `hdfs-site.xml`

```bash
nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```

Add:
```xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///home/YOUR_USERNAME/hadoop_data/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///home/YOUR_USERNAME/hadoop_data/datanode</value>
    </property>
</configuration>
```

#### 1.4 Edit `mapred-site.xml`

```bash
nano $HADOOP_HOME/etc/hadoop/mapred-site.xml
```

Add:
```xml
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>
```

#### 1.5 Edit `yarn-site.xml`

```bash
nano $HADOOP_HOME/etc/hadoop/yarn-site.xml
```

Add:
```xml
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
        <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_HOME,PATH,LANG,TZ,HADOOP_MAPRED_HOME</value>
    </property>
</configuration>
```

### Step 2: Create Directories

```bash
# Create data directories
mkdir -p ~/hadoop_data/namenode
mkdir -p ~/hadoop_data/datanode
mkdir -p ~/hadoop_tmp
```

### Step 3: Format NameNode

```bash
# Format (only do this once!)
hdfs namenode -format
```

### Step 4: Start Hadoop

```bash
# Start HDFS
start-dfs.sh

# Start YARN
start-yarn.sh

# Verify processes
jps
# Should see: NameNode, DataNode, SecondaryNameNode, ResourceManager, NodeManager
```

### Step 5: Access Web UIs

- **HDFS NameNode**: http://localhost:9870
- **YARN ResourceManager**: http://localhost:8088
- **MapReduce JobHistory**: http://localhost:19888

---

## Multi-Node Cluster Setup

### Architecture

```
Master Node (NameNode + ResourceManager)
    ├── Worker Node 1 (DataNode + NodeManager)
    ├── Worker Node 2 (DataNode + NodeManager)
    └── Worker Node 3 (DataNode + NodeManager)
```

### Prerequisites

- Multiple machines on same network
- Passwordless SSH between all nodes
- Same Hadoop version on all nodes
- Synchronized clocks (NTP)

### Step 1: Configure Master Node

#### 1.1 Edit `/etc/hosts` on all nodes

```bash
sudo nano /etc/hosts

# Add:
192.168.1.100  master
192.168.1.101  worker1
192.168.1.102  worker2
192.168.1.103  worker3
```

#### 1.2 Setup passwordless SSH

```bash
# On master
ssh-keygen -t rsa -P ""

# Copy to all workers
ssh-copy-id worker1
ssh-copy-id worker2
ssh-copy-id worker3

# Test
ssh worker1
ssh worker2
ssh worker3
```

#### 1.3 Edit `core-site.xml`

```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://master:9000</value>
    </property>
</configuration>
```

#### 1.4 Edit `hdfs-site.xml`

```xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>3</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///home/hadoop/hadoop_data/namenode</value>
    </property>
</configuration>
```

#### 1.5 Edit `workers` file

```bash
nano $HADOOP_HOME/etc/hadoop/workers

# Add worker hostnames (remove localhost)
worker1
worker2
worker3
```

### Step 2: Configure Worker Nodes

#### 2.1 Copy configuration from master

```bash
# On master
scp -r $HADOOP_HOME/etc/hadoop/* worker1:$HADOOP_HOME/etc/hadoop/
scp -r $HADOOP_HOME/etc/hadoop/* worker2:$HADOOP_HOME/etc/hadoop/
scp -r $HADOOP_HOME/etc/hadoop/* worker3:$HADOOP_HOME/etc/hadoop/
```

#### 2.2 Edit `hdfs-site.xml` on each worker

```xml
<configuration>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///home/hadoop/hadoop_data/datanode</value>
    </property>
</configuration>
```

### Step 3: Start Cluster

```bash
# On master node

# Format NameNode (first time only)
hdfs namenode -format

# Start HDFS
start-dfs.sh

# Start YARN
start-yarn.sh

# Verify
hdfs dfsadmin -report
yarn node -list
```

---

## Verification

### Check HDFS

```bash
# Create directory
hdfs dfs -mkdir -p /user/$USER

# Upload file
echo "Hello Hadoop" > test.txt
hdfs dfs -put test.txt /user/$USER/

# List files
hdfs dfs -ls /user/$USER/

# Read file
hdfs dfs -cat /user/$USER/test.txt

# Check cluster health
hdfs dfsadmin -report
```

### Run MapReduce Example

```bash
# Create input directory
hdfs dfs -mkdir -p /user/$USER/wordcount/input

# Create sample file
echo "hello world hello hadoop" > sample.txt
hdfs dfs -put sample.txt /user/$USER/wordcount/input/

# Run word count
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar \
  wordcount /user/$USER/wordcount/input /user/$USER/wordcount/output

# View results
hdfs dfs -cat /user/$USER/wordcount/output/part-r-00000
```

### Check YARN

```bash
# List applications
yarn application -list

# Check node status
yarn node -list

# View application logs
yarn logs -applicationId <application_id>
```

---

## Common Commands

### HDFS Commands

```bash
# File operations
hdfs dfs -ls /                          # List files
hdfs dfs -mkdir /dir                    # Create directory
hdfs dfs -put local.txt /hdfs/path      # Upload file
hdfs dfs -get /hdfs/path local.txt      # Download file
hdfs dfs -cat /file.txt                 # Read file
hdfs dfs -rm /file.txt                  # Delete file
hdfs dfs -rm -r /dir                    # Delete directory
hdfs dfs -cp /src /dest                 # Copy file
hdfs dfs -mv /src /dest                 # Move file

# Admin commands
hdfs dfsadmin -report                   # Cluster report
hdfs dfsadmin -safemode leave           # Leave safe mode
hdfs fsck /                             # File system check
hdfs balancer                           # Balance data across nodes
```

### YARN Commands

```bash
# Application management
yarn application -list                  # List applications
yarn application -kill <app-id>         # Kill application
yarn logs -applicationId <app-id>       # View logs

# Node management
yarn node -list                         # List nodes
yarn node -status <node-id>             # Node status

# Queue management
yarn queue -status default              # Queue status
```

### Hadoop Daemon Commands

```bash
# Start/Stop all
start-all.sh                            # Start HDFS + YARN
stop-all.sh                             # Stop HDFS + YARN

# Start/Stop HDFS
start-dfs.sh                            # Start HDFS
stop-dfs.sh                             # Stop HDFS

# Start/Stop YARN
start-yarn.sh                           # Start YARN
stop-yarn.sh                            # Stop YARN

# Individual daemons
hadoop-daemon.sh start namenode
hadoop-daemon.sh start datanode
yarn-daemon.sh start resourcemanager
yarn-daemon.sh start nodemanager
```

---

## Troubleshooting

### Issue 1: NameNode not starting

**Symptoms**: NameNode process not in `jps` output

**Solutions**:
```bash
# Check logs
tail -f $HADOOP_HOME/logs/hadoop-*-namenode-*.log

# Common fix: Reformat NameNode (WARNING: deletes all data)
stop-dfs.sh
rm -rf ~/hadoop_data/namenode/*
rm -rf ~/hadoop_data/datanode/*
hdfs namenode -format
start-dfs.sh
```

### Issue 2: DataNode not connecting

**Symptoms**: DataNode not showing in web UI

**Solutions**:
```bash
# Check DataNode logs
tail -f $HADOOP_HOME/logs/hadoop-*-datanode-*.log

# Fix 1: Check clusterID matches
cat ~/hadoop_data/namenode/current/VERSION
cat ~/hadoop_data/datanode/current/VERSION
# If different, delete datanode data and restart

# Fix 2: Check network connectivity
telnet master 9000

# Fix 3: Check firewall
sudo ufw allow 9000
sudo ufw allow 9870
```

### Issue 3: Safe mode stuck

**Symptoms**: Cannot write to HDFS

**Solutions**:
```bash
# Check safe mode status
hdfs dfsadmin -safemode get

# Force leave safe mode
hdfs dfsadmin -safemode leave

# Wait for blocks to replicate
hdfs dfsadmin -safemode wait
```

### Issue 4: Out of memory

**Symptoms**: Jobs failing with OOM errors

**Solutions**:
```bash
# Edit hadoop-env.sh
nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# Increase heap size
export HADOOP_HEAPSIZE=4096  # 4GB

# Edit mapred-site.xml for MapReduce memory
<property>
    <name>mapreduce.map.memory.mb</name>
    <value>2048</value>
</property>
<property>
    <name>mapreduce.reduce.memory.mb</name>
    <value>4096</value>
</property>
```

### Issue 5: Permission denied

**Symptoms**: Cannot create files in HDFS

**Solutions**:
```bash
# Create user directory
hdfs dfs -mkdir -p /user/$USER

# Set permissions
hdfs dfs -chmod 755 /user/$USER

# Or disable permission checking (dev only!)
# Add to hdfs-site.xml:
<property>
    <name>dfs.permissions.enabled</name>
    <value>false</value>
</property>
```

### Issue 6: Port already in use

**Symptoms**: Cannot start services

**Solutions**:
```bash
# Find process using port
lsof -i :9000
lsof -i :9870

# Kill process
kill -9 <PID>

# Or change port in configuration files
```

---

## Performance Tuning

### HDFS Tuning

```xml
<!-- hdfs-site.xml -->
<property>
    <name>dfs.block.size</name>
    <value>268435456</value>  <!-- 256MB -->
</property>
<property>
    <name>dfs.replication</name>
    <value>3</value>
</property>
```

### MapReduce Tuning

```xml
<!-- mapred-site.xml -->
<property>
    <name>mapreduce.map.memory.mb</name>
    <value>2048</value>
</property>
<property>
    <name>mapreduce.reduce.memory.mb</name>
    <value>4096</value>
</property>
<property>
    <name>mapreduce.task.io.sort.mb</name>
    <value>512</value>
</property>
```

### YARN Tuning

```xml
<!-- yarn-site.xml -->
<property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>8192</value>
</property>
<property>
    <name>yarn.scheduler.maximum-allocation-mb</name>
    <value>8192</value>
</property>
<property>
    <name>yarn.nodemanager.resource.cpu-vcores</name>
    <value>4</value>
</property>
```

---

## Next Steps

1. **Verify Installation**: Run verification commands
2. **Try Examples**: Work through `02_mapreduce/` examples
3. **Install Ecosystem**: Setup Hive, Pig, HBase
4. **Build Projects**: Create real-world applications

---

## Additional Resources

- [Official Hadoop Documentation](https://hadoop.apache.org/docs/)
- [Hadoop Cluster Setup](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/ClusterSetup.html)
- [HDFS Commands Guide](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HDFSCommands.html)

---

**Setup Complete! Ready to learn Hadoop! 🐘**
