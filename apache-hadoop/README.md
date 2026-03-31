# Apache Hadoop Learning Repository

> **Comprehensive guide to learning Apache Hadoop ecosystem - from basics to advanced distributed computing**

A structured learning repository for understanding Hadoop, HDFS, MapReduce, YARN, and the entire Hadoop ecosystem.

---

## 📚 Table of Contents

1. [What is Apache Hadoop?](#what-is-apache-hadoop)
2. [Repository Structure](#repository-structure)
3. [Core Components](#core-components)
4. [Hadoop Ecosystem](#hadoop-ecosystem)
5. [Quick Start](#quick-start)
6. [Learning Path](#learning-path)
7. [Examples](#examples)
8. [Resources](#resources)

---

## What is Apache Hadoop?

**Apache Hadoop** is an open-source framework for distributed storage and processing of large datasets across clusters of computers.

### Key Features

- **Scalability**: Scale from single server to thousands of machines
- **Fault Tolerance**: Automatic handling of hardware failures
- **Cost-Effective**: Run on commodity hardware
- **Flexibility**: Process structured and unstructured data
- **Distributed**: Data and processing distributed across cluster

### Hadoop vs Traditional Systems

| Aspect | Traditional | Hadoop |
|--------|-------------|--------|
| **Storage** | Centralized | Distributed (HDFS) |
| **Processing** | Vertical scaling | Horizontal scaling |
| **Cost** | Expensive hardware | Commodity hardware |
| **Fault Tolerance** | Hardware redundancy | Software redundancy |
| **Data Types** | Structured | Any format |

---

## Repository Structure

```
apache-hadoop/
│
├── README.md                          # This file
├── SETUP.md                           # Installation & setup guide
├── QUICK_REFERENCE.md                # Commands & concepts cheatsheet
├── requirements.txt                   # Python dependencies
├── .gitignore                        # Git ignore patterns
│
├── 01_hdfs/                          # Hadoop Distributed File System
│   ├── README.md                     # HDFS concepts
│   ├── hdfs_basics.py               # Basic HDFS operations
│   ├── hdfs_advanced.py             # Advanced HDFS patterns
│   └── examples/
│       ├── file_operations.py       # Read/write operations
│       ├── directory_management.py  # Directory operations
│       └── replication_demo.py      # Replication concepts
│
├── 02_mapreduce/                     # MapReduce Programming
│   ├── README.md                     # MapReduce concepts
│   ├── word_count.py                # Classic word count
│   ├── custom_mapper_reducer.py     # Custom M/R jobs
│   ├── combiner_example.py          # Combiner usage
│   └── examples/
│       ├── log_analysis.py          # Log processing
│       ├── data_aggregation.py      # Aggregation patterns
│       └── join_operations.py       # Join patterns
│
├── 03_yarn/                          # YARN Resource Management
│   ├── README.md                     # YARN concepts
│   ├── yarn_basics.py               # YARN fundamentals
│   └── examples/
│       ├── resource_allocation.py   # Resource management
│       └── application_master.py    # Application patterns
│
├── 04_hive/                          # Apache Hive (SQL on Hadoop)
│   ├── README.md                     # Hive concepts
│   ├── hive_basics.sql              # Basic queries
│   ├── hive_advanced.sql            # Advanced queries
│   ├── partitioning.sql             # Partitioning strategies
│   └── examples/
│       ├── etl_pipeline.sql         # ETL patterns
│       ├── optimization.sql         # Query optimization
│       └── udf_examples.py          # User-defined functions
│
├── 05_pig/                           # Apache Pig (Data Flow)
│   ├── README.md                     # Pig concepts
│   ├── pig_basics.pig               # Basic Pig Latin
│   ├── pig_advanced.pig             # Advanced patterns
│   └── examples/
│       ├── data_transformation.pig  # Transform data
│       └── aggregations.pig         # Aggregation patterns
│
├── 06_hbase/                         # Apache HBase (NoSQL)
│   ├── README.md                     # HBase concepts
│   ├── hbase_basics.py              # Basic operations
│   ├── hbase_advanced.py            # Advanced patterns
│   └── examples/
│       ├── crud_operations.py       # Create, Read, Update, Delete
│       ├── schema_design.py         # Schema patterns
│       └── bulk_loading.py          # Bulk load data
│
├── 07_spark_on_hadoop/               # Apache Spark with Hadoop
│   ├── README.md                     # Spark + Hadoop
│   ├── spark_hdfs.py                # Spark reading HDFS
│   └── examples/
│       ├── spark_vs_mapreduce.py    # Comparison
│       └── optimization.py          # Performance tuning
│
├── 08_ecosystem/                     # Hadoop Ecosystem Tools
│   ├── README.md                     # Ecosystem overview
│   ├── sqoop/                       # Data import/export
│   ├── flume/                       # Log collection
│   ├── oozie/                       # Workflow scheduler
│   └── zookeeper/                   # Coordination service
│
├── 09_administration/                # Hadoop Administration
│   ├── README.md                     # Admin guide
│   ├── cluster_setup.md             # Cluster configuration
│   ├── monitoring.md                # Monitoring & metrics
│   ├── troubleshooting.md           # Common issues
│   └── examples/
│       ├── health_check.py          # Cluster health
│       └── performance_tuning.md    # Optimization
│
├── 10_real_world_projects/           # Complete Projects
│   ├── README.md                     # Projects overview
│   ├── log_analytics/               # Log analysis pipeline
│   ├── etl_pipeline/                # ETL with Hadoop
│   ├── data_warehouse/              # Data warehouse
│   └── streaming_integration/       # Kafka + Hadoop
│
└── docs/                             # Additional Documentation
    ├── architecture.md              # Hadoop architecture
    ├── best_practices.md            # Best practices
    ├── performance.md               # Performance guide
    └── migration_guide.md           # Migration strategies
```

---

## Core Components

### 1. HDFS (Hadoop Distributed File System)

**Purpose**: Distributed storage system

**Key Concepts**:
- **NameNode**: Master node managing metadata
- **DataNode**: Worker nodes storing actual data
- **Blocks**: Data split into blocks (default 128MB)
- **Replication**: Data replicated across nodes (default 3x)

**Use Cases**:
- Store large datasets
- Batch processing
- Data lake storage

### 2. MapReduce

**Purpose**: Distributed data processing framework

**Key Concepts**:
- **Map**: Process and transform data
- **Reduce**: Aggregate and summarize results
- **Shuffle & Sort**: Intermediate data organization
- **Combiner**: Local aggregation optimization

**Use Cases**:
- Batch data processing
- Log analysis
- Data transformation

### 3. YARN (Yet Another Resource Negotiator)

**Purpose**: Resource management and job scheduling

**Key Concepts**:
- **ResourceManager**: Cluster resource manager
- **NodeManager**: Per-node resource manager
- **ApplicationMaster**: Per-application coordinator
- **Container**: Resource allocation unit

**Use Cases**:
- Multi-tenant clusters
- Resource allocation
- Job scheduling

---

## Hadoop Ecosystem

### Data Storage
- **HDFS**: Distributed file system
- **HBase**: NoSQL database on HDFS
- **Kudu**: Columnar storage

### Data Processing
- **MapReduce**: Batch processing
- **Spark**: Fast in-memory processing
- **Tez**: Optimized execution engine

### Data Analysis
- **Hive**: SQL on Hadoop
- **Pig**: Data flow language
- **Impala**: Real-time SQL queries

### Data Ingestion
- **Sqoop**: RDBMS ↔ Hadoop
- **Flume**: Log collection
- **Kafka**: Stream ingestion

### Workflow & Coordination
- **Oozie**: Workflow scheduler
- **ZooKeeper**: Coordination service
- **Airflow**: Modern orchestration

### Security & Governance
- **Ranger**: Security management
- **Atlas**: Metadata & governance
- **Knox**: Gateway service

---

## Quick Start

### Prerequisites

- Java 8 or 11
- Python 3.7+
- Linux/Mac (or WSL on Windows)
- 8GB+ RAM recommended

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd apache-hadoop

# Install Python dependencies
pip install -r requirements.txt

# Follow detailed setup
cat SETUP.md
```

### First Example - Word Count

```bash
# 1. Start Hadoop (see SETUP.md)
start-dfs.sh
start-yarn.sh

# 2. Create HDFS directory
hdfs dfs -mkdir -p /user/$USER/input

# 3. Upload sample file
echo "hello world hello hadoop" > sample.txt
hdfs dfs -put sample.txt /user/$USER/input/

# 4. Run MapReduce word count
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar \
  wordcount /user/$USER/input /user/$USER/output

# 5. View results
hdfs dfs -cat /user/$USER/output/part-r-00000
```

---

## Learning Path

### 🟢 Week 1-2: Foundations

**Objectives**:
- Understand distributed computing concepts
- Learn HDFS architecture
- Basic HDFS operations

**Topics**:
- Hadoop overview
- HDFS architecture
- NameNode & DataNode
- Block storage & replication
- HDFS commands

**Practice**:
- Install Hadoop
- HDFS file operations
- Monitor cluster health

**Resources**: `01_hdfs/`

---

### 🟡 Week 3-4: MapReduce

**Objectives**:
- Understand MapReduce paradigm
- Write custom MapReduce jobs
- Optimize MapReduce performance

**Topics**:
- Map and Reduce functions
- Shuffle and Sort
- Combiners and Partitioners
- Input/Output formats
- Job configuration

**Practice**:
- Word count variations
- Log analysis
- Data aggregation

**Resources**: `02_mapreduce/`

---

### 🟡 Week 5-6: YARN & Ecosystem

**Objectives**:
- Understand YARN architecture
- Learn Hive for SQL queries
- Explore Pig for data flow

**Topics**:
- YARN components
- Resource allocation
- Hive tables & queries
- Pig Latin scripts
- HBase basics

**Practice**:
- YARN application monitoring
- Hive ETL pipelines
- Pig transformations

**Resources**: `03_yarn/`, `04_hive/`, `05_pig/`

---

### 🔴 Week 7-8: Advanced & Production

**Objectives**:
- Production cluster setup
- Performance optimization
- Integration with modern tools

**Topics**:
- Cluster administration
- Security & governance
- Spark on Hadoop
- Monitoring & troubleshooting
- Best practices

**Practice**:
- Multi-node cluster
- Performance tuning
- Real-world projects

**Resources**: `09_administration/`, `10_real_world_projects/`

---

## Examples

### Example 1: HDFS File Operations

```python
# 01_hdfs/hdfs_basics.py
from hdfs import InsecureClient

# Connect to HDFS
client = InsecureClient('http://localhost:9870', user='hadoop')

# Create directory
client.makedirs('/user/hadoop/data')

# Upload file
client.upload('/user/hadoop/data/sample.txt', 'local_file.txt')

# Read file
with client.read('/user/hadoop/data/sample.txt') as reader:
    content = reader.read()
    print(content)

# List files
files = client.list('/user/hadoop/data')
print(files)
```

### Example 2: MapReduce Word Count

```python
# 02_mapreduce/word_count.py
from mrjob.job import MRJob
from mrjob.step import MRStep

class WordCount(MRJob):
    
    def mapper(self, _, line):
        """Map: emit each word with count 1"""
        for word in line.split():
            yield word.lower(), 1
    
    def combiner(self, word, counts):
        """Combiner: local aggregation"""
        yield word, sum(counts)
    
    def reducer(self, word, counts):
        """Reducer: final aggregation"""
        yield word, sum(counts)

if __name__ == '__main__':
    WordCount.run()
```

### Example 3: Hive Query

```sql
-- 04_hive/hive_basics.sql

-- Create table
CREATE TABLE IF NOT EXISTS users (
    user_id INT,
    username STRING,
    email STRING,
    created_date DATE
)
PARTITIONED BY (year INT, month INT)
STORED AS PARQUET;

-- Load data
LOAD DATA INPATH '/user/hadoop/data/users.csv'
INTO TABLE users
PARTITION (year=2024, month=1);

-- Query data
SELECT 
    year,
    month,
    COUNT(*) as user_count
FROM users
GROUP BY year, month
ORDER BY year DESC, month DESC;
```

### Example 4: HBase Operations

```python
# 06_hbase/hbase_basics.py
import happybase

# Connect to HBase
connection = happybase.Connection('localhost')

# Create table
connection.create_table(
    'users',
    {'cf': dict()}  # column family
)

# Get table
table = connection.table('users')

# Put data
table.put(b'user1', {b'cf:name': b'John', b'cf:age': b'30'})

# Get data
row = table.row(b'user1')
print(row)

# Scan table
for key, data in table.scan():
    print(key, data)
```

---

## Core Concepts

### HDFS Architecture

```
┌─────────────────────────────────────────┐
│           NameNode (Master)              │
│  - Manages metadata                      │
│  - Tracks block locations                │
│  - Handles client requests               │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
┌───────▼─────┐ ┌──▼────────┐ ┌▼──────────┐
│  DataNode 1 │ │ DataNode 2│ │DataNode 3 │
│  - Stores   │ │ - Stores  │ │- Stores   │
│    blocks   │ │   blocks  │ │  blocks   │
│  - Sends    │ │ - Sends   │ │- Sends    │
│    heartbeat│ │   heartbeat│ │  heartbeat│
└─────────────┘ └───────────┘ └───────────┘
```

### MapReduce Flow

```
Input Data
    │
    ▼
┌─────────┐
│  Split  │  Split data into chunks
└─────────┘
    │
    ▼
┌─────────┐
│   Map   │  Process each chunk
└─────────┘
    │
    ▼
┌─────────┐
│ Shuffle │  Group by key
│  & Sort │
└─────────┘
    │
    ▼
┌─────────┐
│ Reduce  │  Aggregate results
└─────────┘
    │
    ▼
Output Data
```

### YARN Architecture

```
┌──────────────────────────────────────┐
│      ResourceManager (Master)         │
│  - Manages cluster resources          │
│  - Schedules applications             │
└──────────────────────────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼────┐  ┌──▼─────┐  ┌──▼─────┐
│NodeMgr1│  │NodeMgr2│  │NodeMgr3│
│        │  │        │  │        │
│┌──────┐│  │┌──────┐│  │┌──────┐│
││AppMstr││  ││Cont. ││  ││Cont. ││
│└──────┘│  │└──────┘│  │└──────┘│
└────────┘  └────────┘  └────────┘
```

---

## Best Practices

### HDFS Best Practices

1. **Block Size**: Use 128MB or 256MB for large files
2. **Replication**: Keep default 3x for production
3. **NameNode**: Monitor memory usage
4. **Balancer**: Run regularly to balance data
5. **Compression**: Use Snappy or LZO

### MapReduce Best Practices

1. **Combiners**: Use for local aggregation
2. **Partitioners**: Balance reducer load
3. **Compression**: Compress intermediate data
4. **Memory**: Tune JVM heap sizes
5. **Speculative Execution**: Enable for slow tasks

### Hive Best Practices

1. **Partitioning**: Partition by date/region
2. **Bucketing**: Use for large tables
3. **File Format**: Use ORC or Parquet
4. **Statistics**: Collect table statistics
5. **Vectorization**: Enable for performance

---

## Common Use Cases

### 1. Log Analysis
- Collect logs with Flume
- Store in HDFS
- Process with MapReduce/Hive
- Visualize with BI tools

### 2. ETL Pipelines
- Extract from RDBMS (Sqoop)
- Transform with Hive/Pig
- Load to data warehouse
- Schedule with Oozie

### 3. Data Lake
- Store raw data in HDFS
- Catalog with Hive metastore
- Query with Hive/Spark
- Govern with Atlas

### 4. Batch Processing
- Ingest data daily
- Process with MapReduce
- Aggregate results
- Export to downstream systems

---

## Resources

### Official Documentation
- [Apache Hadoop Docs](https://hadoop.apache.org/docs/)
- [HDFS Architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
- [MapReduce Tutorial](https://hadoop.apache.org/docs/stable/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)

### Books
- "Hadoop: The Definitive Guide" - Tom White
- "Hadoop in Practice" - Alex Holmes
- "Programming Pig" - Alan Gates

### Online Courses
- Cloudera Hadoop Training
- Hortonworks Tutorials
- Udemy Hadoop Courses

### Community
- Apache Hadoop Mailing Lists
- Stack Overflow
- Hadoop User Groups

---

## Troubleshooting

### Common Issues

**NameNode not starting**:
```bash
# Check logs
tail -f $HADOOP_HOME/logs/hadoop-*-namenode-*.log

# Format NameNode (WARNING: deletes data)
hdfs namenode -format
```

**DataNode not connecting**:
```bash
# Check DataNode logs
tail -f $HADOOP_HOME/logs/hadoop-*-datanode-*.log

# Verify network connectivity
telnet namenode-host 9000
```

**Job failing**:
```bash
# Check application logs
yarn logs -applicationId <app-id>

# Check ResourceManager UI
http://localhost:8088
```

---

## Next Steps

1. **Setup Hadoop**: Follow [SETUP.md](SETUP.md)
2. **Learn HDFS**: Start with `01_hdfs/`
3. **Try MapReduce**: Work through `02_mapreduce/`
4. **Explore Ecosystem**: Check `04_hive/`, `05_pig/`
5. **Build Projects**: Create in `10_real_world_projects/`

---

## Contributing

Feel free to add:
- New examples
- Best practices
- Real-world use cases
- Performance tips

---

## License

This is a learning repository. Use freely for educational purposes.

---

**Happy Learning! 🐘**

*Hadoop - Enabling Big Data Processing Since 2006*
