# Hadoop Quick Reference

> **Quick commands and concepts cheatsheet**

---

## HDFS Commands

### File Operations
```bash
# List files
hdfs dfs -ls /
hdfs dfs -ls -R /user                    # Recursive

# Create directory
hdfs dfs -mkdir /dir
hdfs dfs -mkdir -p /path/to/dir          # Create parent dirs

# Upload/Download
hdfs dfs -put local.txt /hdfs/path       # Upload
hdfs dfs -get /hdfs/path local.txt       # Download
hdfs dfs -copyFromLocal local.txt /path  # Same as put
hdfs dfs -copyToLocal /path local.txt    # Same as get

# Read file
hdfs dfs -cat /file.txt
hdfs dfs -tail /file.txt                 # Last 1KB
hdfs dfs -head /file.txt                 # First 1KB

# Copy/Move
hdfs dfs -cp /src /dest                  # Copy
hdfs dfs -mv /src /dest                  # Move

# Delete
hdfs dfs -rm /file.txt
hdfs dfs -rm -r /dir                     # Recursive delete
hdfs dfs -rm -r -skipTrash /dir          # Skip trash

# File info
hdfs dfs -du /dir                        # Disk usage
hdfs dfs -df /                           # Disk free
hdfs dfs -stat %b /file                  # File size
hdfs dfs -count /dir                     # Count files/dirs

# Permissions
hdfs dfs -chmod 755 /file
hdfs dfs -chown user:group /file
hdfs dfs -chgrp group /file

# Merge files
hdfs dfs -getmerge /dir local.txt        # Merge to local
```

### Admin Commands
```bash
# Cluster report
hdfs dfsadmin -report

# Safe mode
hdfs dfsadmin -safemode get
hdfs dfsadmin -safemode enter
hdfs dfsadmin -safemode leave

# File system check
hdfs fsck /                              # Check all
hdfs fsck /path -files -blocks -locations

# Balance cluster
hdfs balancer

# Refresh nodes
hdfs dfsadmin -refreshNodes

# Decommission DataNode
hdfs dfsadmin -refreshNodes
```

---

## YARN Commands

### Application Management
```bash
# List applications
yarn application -list
yarn application -list -appStates RUNNING

# Kill application
yarn application -kill <application_id>

# Application status
yarn application -status <application_id>

# View logs
yarn logs -applicationId <application_id>
yarn logs -applicationId <app_id> -containerId <container_id>
```

### Node Management
```bash
# List nodes
yarn node -list
yarn node -list -all

# Node status
yarn node -status <node_id>
```

### Queue Management
```bash
# Queue status
yarn queue -status default

# List queues
yarn queue -list
```

---

## MapReduce Commands

### Run MapReduce Job
```bash
# Word count example
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar \
  wordcount /input /output

# Custom jar
hadoop jar myapp.jar com.example.MyJob /input /output

# With configuration
hadoop jar myapp.jar com.example.MyJob \
  -D mapreduce.job.reduces=10 \
  /input /output
```

### Job Management
```bash
# List jobs
mapred job -list

# Kill job
mapred job -kill <job_id>

# Job status
mapred job -status <job_id>

# Job history
mapred job -history <job_output_dir>
```

---

## Daemon Management

### Start/Stop Services
```bash
# All services
start-all.sh
stop-all.sh

# HDFS only
start-dfs.sh
stop-dfs.sh

# YARN only
start-yarn.sh
stop-yarn.sh

# Individual daemons
hadoop-daemon.sh start namenode
hadoop-daemon.sh stop namenode
hadoop-daemon.sh start datanode
hadoop-daemon.sh stop datanode
yarn-daemon.sh start resourcemanager
yarn-daemon.sh stop resourcemanager
yarn-daemon.sh start nodemanager
yarn-daemon.sh stop nodemanager
```

### Check Running Processes
```bash
jps                                      # Java processes
# Should see: NameNode, DataNode, ResourceManager, NodeManager
```

---

## Configuration Files

### Location
```bash
$HADOOP_HOME/etc/hadoop/
```

### Key Files
- `core-site.xml` - Core Hadoop settings
- `hdfs-site.xml` - HDFS settings
- `mapred-site.xml` - MapReduce settings
- `yarn-site.xml` - YARN settings
- `hadoop-env.sh` - Environment variables
- `workers` - List of worker nodes

---

## Web UIs

| Service | URL | Purpose |
|---------|-----|---------|
| NameNode | http://localhost:9870 | HDFS overview |
| ResourceManager | http://localhost:8088 | YARN applications |
| JobHistory | http://localhost:19888 | Job history |
| DataNode | http://localhost:9864 | DataNode info |
| NodeManager | http://localhost:8042 | NodeManager info |

---

## Core Concepts

### HDFS Architecture
```
NameNode (Master)
  ├── Manages metadata
  ├── Tracks block locations
  └── Handles client requests

DataNode (Workers)
  ├── Stores actual data blocks
  ├── Sends heartbeats to NameNode
  └── Replicates blocks
```

### Block Storage
- Default block size: 128MB
- Default replication: 3x
- Blocks distributed across DataNodes

### MapReduce Flow
```
Input → Split → Map → Shuffle & Sort → Reduce → Output
```

### YARN Components
```
ResourceManager (Master)
  ├── Manages cluster resources
  └── Schedules applications

NodeManager (Workers)
  ├── Manages node resources
  └── Runs containers

ApplicationMaster
  ├── Per-application coordinator
  └── Requests resources
```

---

## Common Patterns

### Word Count
```python
# Map
def mapper(line):
    for word in line.split():
        emit(word, 1)

# Reduce
def reducer(word, counts):
    emit(word, sum(counts))
```

### Join Pattern
```python
# Map
def mapper(record):
    key = record.join_key
    emit(key, record)

# Reduce
def reducer(key, records):
    # Join records with same key
    emit(key, joined_records)
```

### Aggregation
```python
# Map
def mapper(record):
    key = record.group_by_field
    value = record.aggregate_field
    emit(key, value)

# Reduce
def reducer(key, values):
    emit(key, aggregate(values))
```

---

## Performance Tips

### HDFS
- Use 128MB or 256MB blocks for large files
- Keep replication at 3 for production
- Enable compression (Snappy, LZO)
- Run balancer regularly

### MapReduce
- Use combiners for local aggregation
- Compress intermediate data
- Tune memory settings
- Use appropriate number of reducers

### YARN
- Allocate memory properly
- Monitor resource usage
- Use capacity scheduler
- Set queue limits

---

## Troubleshooting

### NameNode Issues
```bash
# Check logs
tail -f $HADOOP_HOME/logs/hadoop-*-namenode-*.log

# Reformat (WARNING: deletes data)
hdfs namenode -format
```

### DataNode Issues
```bash
# Check logs
tail -f $HADOOP_HOME/logs/hadoop-*-datanode-*.log

# Verify connectivity
telnet namenode-host 9000
```

### Safe Mode
```bash
# Check status
hdfs dfsadmin -safemode get

# Leave safe mode
hdfs dfsadmin -safemode leave
```

### Job Failures
```bash
# Check application logs
yarn logs -applicationId <app_id>

# Check ResourceManager UI
http://localhost:8088
```

---

## Environment Variables

```bash
export HADOOP_HOME=/path/to/hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export JAVA_HOME=/path/to/java
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
```

---

## File Formats

| Format | Compression | Splittable | Use Case |
|--------|-------------|------------|----------|
| Text | No | Yes | Simple data |
| SequenceFile | Yes | Yes | Binary key-value |
| Avro | Yes | Yes | Schema evolution |
| Parquet | Yes | Yes | Columnar analytics |
| ORC | Yes | Yes | Hive optimized |

---

## Compression Codecs

| Codec | Speed | Compression | Splittable |
|-------|-------|-------------|------------|
| Gzip | Slow | High | No |
| Bzip2 | Very Slow | Very High | Yes |
| Snappy | Fast | Medium | No |
| LZO | Fast | Medium | Yes* |

*Requires indexing

---

## Memory Configuration

### MapReduce
```xml
<property>
    <name>mapreduce.map.memory.mb</name>
    <value>2048</value>
</property>
<property>
    <name>mapreduce.reduce.memory.mb</name>
    <value>4096</value>
</property>
```

### YARN
```xml
<property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>8192</value>
</property>
<property>
    <name>yarn.scheduler.maximum-allocation-mb</name>
    <value>8192</value>
</property>
```

---

## Useful Aliases

```bash
# Add to ~/.bashrc
alias hls='hdfs dfs -ls'
alias hcat='hdfs dfs -cat'
alias hput='hdfs dfs -put'
alias hget='hdfs dfs -get'
alias hrm='hdfs dfs -rm -r'
alias hdu='hdfs dfs -du -h'
alias hreport='hdfs dfsadmin -report'
alias yarnlist='yarn application -list'
alias yarnlogs='yarn logs -applicationId'
```

---

## Quick Setup Checklist

- [ ] Install Java 8/11
- [ ] Setup SSH passwordless login
- [ ] Download and extract Hadoop
- [ ] Set environment variables
- [ ] Configure core-site.xml
- [ ] Configure hdfs-site.xml
- [ ] Configure mapred-site.xml
- [ ] Configure yarn-site.xml
- [ ] Format NameNode
- [ ] Start HDFS and YARN
- [ ] Verify with jps
- [ ] Access web UIs

---

## Common Error Codes

| Error | Meaning | Solution |
|-------|---------|----------|
| Connection refused | Service not running | Start Hadoop services |
| Safe mode | HDFS in safe mode | Leave safe mode |
| Permission denied | Insufficient permissions | Check file permissions |
| Out of memory | Insufficient heap | Increase heap size |
| Port in use | Port already bound | Kill process or change port |

---

**Keep this handy while working with Hadoop! 🐘**
