# Apache Airflow Setup Guide

## Prerequisites

### System Requirements
- **Python**: 3.8, 3.9, 3.10, or 3.11
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Database**: PostgreSQL or MySQL (SQLite for development only)
- **OS**: Linux, macOS, or Windows (WSL recommended)

### Check Python Version
```bash
python --version
# or
python3 --version
```

---

## Installation Methods

### Option 1: Quick Start (Development)

```bash
# Create virtual environment
python -m venv airflow-env

# Activate virtual environment
# macOS/Linux:
source airflow-env/bin/activate
# Windows:
airflow-env\Scripts\activate

# Set Airflow home (optional, defaults to ~/airflow)
export AIRFLOW_HOME=~/airflow

# Install Airflow
AIRFLOW_VERSION=2.8.0
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Start webserver
airflow webserver --port 8080

# In another terminal, start scheduler
airflow scheduler
```

Access UI: http://localhost:8080 (username: admin, password: admin)

### Option 2: Docker Compose (Recommended for Production)

```bash
# Download docker-compose.yaml
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.8.0/docker-compose.yaml'

# Create required directories
mkdir -p ./dags ./logs ./plugins ./config

# Set Airflow UID
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Initialize database
docker-compose up airflow-init

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

Access UI: http://localhost:8080 (username: airflow, password: airflow)

### Option 3: From Requirements File

```bash
# Clone or navigate to project directory
cd "/Users/5149844/windsurf/personal learning/learning/apache-airflow"

# Create virtual environment
python -m venv airflow-env
source airflow-env/bin/activate

# Install from requirements.txt
pip install -r requirements.txt

# Initialize
airflow db init
```

---

## Configuration

### 1. Airflow Configuration File

Location: `$AIRFLOW_HOME/airflow.cfg`

**Key Settings:**

```ini
[core]
# DAGs folder
dags_folder = /path/to/dags

# Executor (SequentialExecutor, LocalExecutor, CeleryExecutor)
executor = LocalExecutor

# Parallelism
parallelism = 32
dag_concurrency = 16
max_active_runs_per_dag = 16

[webserver]
# Web server port
web_server_port = 8080

# Secret key for session
secret_key = your-secret-key

[database]
# Database connection
sql_alchemy_conn = postgresql+psycopg2://user:password@localhost/airflow

[smtp]
# Email configuration
smtp_host = smtp.gmail.com
smtp_starttls = True
smtp_ssl = False
smtp_user = your-email@gmail.com
smtp_password = your-password
smtp_port = 587
smtp_mail_from = your-email@gmail.com
```

### 2. Environment Variables

```bash
# Set in ~/.bashrc or ~/.zshrc
export AIRFLOW_HOME=~/airflow
export AIRFLOW__CORE__DAGS_FOLDER=/path/to/dags
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://user:pass@localhost/airflow
```

### 3. Database Setup (PostgreSQL)

```bash
# Install PostgreSQL
# macOS:
brew install postgresql

# Ubuntu:
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
brew services start postgresql  # macOS
sudo service postgresql start   # Ubuntu

# Create database and user
psql postgres
CREATE DATABASE airflow;
CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
\q

# Update airflow.cfg
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@localhost/airflow

# Initialize database
airflow db init
```

---

## Project Structure

```
airflow/
├── dags/                      # DAG files
│   ├── 01_basic_dag.py
│   ├── 02_task_dependencies.py
│   └── ...
├── plugins/                   # Custom plugins
│   ├── operators/
│   ├── sensors/
│   └── hooks/
├── logs/                      # Task logs
├── config/                    # Configuration files
├── airflow.cfg               # Main configuration
├── airflow.db                # SQLite database (dev)
└── webserver_config.py       # Web server config
```

---

## Running Airflow

### Development Mode

```bash
# Terminal 1: Start webserver
airflow webserver --port 8080

# Terminal 2: Start scheduler
airflow scheduler

# Optional Terminal 3: Start triggerer (for deferrable operators)
airflow triggerer
```

### Production Mode

```bash
# Use systemd or supervisor to manage services

# Example systemd service file: /etc/systemd/system/airflow-webserver.service
[Unit]
Description=Airflow webserver
After=network.target

[Service]
Type=simple
User=airflow
Group=airflow
Environment="AIRFLOW_HOME=/home/airflow/airflow"
ExecStart=/home/airflow/airflow-env/bin/airflow webserver
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Start services
sudo systemctl start airflow-webserver
sudo systemctl start airflow-scheduler
sudo systemctl enable airflow-webserver
sudo systemctl enable airflow-scheduler
```

---

## DAG Development Workflow

### 1. Create DAG File

```bash
# Navigate to dags folder
cd $AIRFLOW_HOME/dags

# Create new DAG
touch my_new_dag.py
```

### 2. Test DAG

```bash
# Check for syntax errors
python $AIRFLOW_HOME/dags/my_new_dag.py

# List DAGs
airflow dags list

# List tasks in DAG
airflow tasks list my_new_dag

# Test specific task
airflow tasks test my_new_dag task_id 2024-01-01

# Test entire DAG
airflow dags test my_new_dag 2024-01-01
```

### 3. Trigger DAG

```bash
# Trigger via CLI
airflow dags trigger my_new_dag

# Trigger with config
airflow dags trigger my_new_dag --conf '{"key": "value"}'

# Backfill
airflow dags backfill my_new_dag \
    --start-date 2024-01-01 \
    --end-date 2024-01-31
```

---

## Common Commands

### DAG Management

```bash
# List all DAGs
airflow dags list

# Show DAG structure
airflow dags show my_dag

# Pause DAG
airflow dags pause my_dag

# Unpause DAG
airflow dags unpause my_dag

# Delete DAG
airflow dags delete my_dag
```

### Task Management

```bash
# List tasks
airflow tasks list my_dag

# Test task
airflow tasks test my_dag task_id 2024-01-01

# Clear task state
airflow tasks clear my_dag --task-regex task_id

# Get task state
airflow tasks state my_dag task_id 2024-01-01
```

### User Management

```bash
# Create user
airflow users create \
    --username user \
    --firstname First \
    --lastname Last \
    --role Admin \
    --email user@example.com

# List users
airflow users list

# Delete user
airflow users delete --username user
```

### Connection Management

```bash
# Add connection
airflow connections add my_postgres \
    --conn-type postgres \
    --conn-host localhost \
    --conn-login airflow \
    --conn-password airflow \
    --conn-port 5432 \
    --conn-schema airflow

# List connections
airflow connections list

# Delete connection
airflow connections delete my_postgres
```

### Variable Management

```bash
# Set variable
airflow variables set my_var my_value

# Get variable
airflow variables get my_var

# List variables
airflow variables list

# Delete variable
airflow variables delete my_var

# Import from JSON
airflow variables import variables.json
```

### Pool Management

```bash
# Create pool
airflow pools set my_pool 5 "My pool description"

# List pools
airflow pools list

# Delete pool
airflow pools delete my_pool
```

---

## Troubleshooting

### Issue 1: DAG Not Appearing in UI

**Causes:**
- Syntax error in DAG file
- DAG file not in dags_folder
- Scheduler not running
- DAG parsing error

**Solutions:**
```bash
# Check for syntax errors
python /path/to/dag_file.py

# Check scheduler logs
tail -f $AIRFLOW_HOME/logs/scheduler/latest/*.log

# Verify dags_folder
airflow config get-value core dags_folder

# Restart scheduler
pkill -f "airflow scheduler"
airflow scheduler
```

### Issue 2: Tasks Stuck in Queued

**Causes:**
- No workers available
- Executor misconfigured
- Pool slots exhausted
- Database connection issues

**Solutions:**
```bash
# Check executor
airflow config get-value core executor

# Check pools
airflow pools list

# Increase pool slots
airflow pools set default_pool 128

# Check database connection
airflow db check
```

### Issue 3: Import Errors

**Causes:**
- Missing dependencies
- Python path issues
- Module not found

**Solutions:**
```bash
# Install missing packages
pip install package-name

# Check Python path
python -c "import sys; print(sys.path)"

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/modules"
```

### Issue 4: Database Migration Errors

**Solutions:**
```bash
# Check current version
airflow db check

# Upgrade database
airflow db upgrade

# Reset database (WARNING: deletes all data)
airflow db reset
```

### Issue 5: Web Server Not Starting

**Solutions:**
```bash
# Check port availability
lsof -i :8080

# Use different port
airflow webserver --port 8081

# Check logs
tail -f $AIRFLOW_HOME/logs/webserver/*.log

# Reset webserver
rm $AIRFLOW_HOME/airflow-webserver.pid
airflow webserver
```

---

## Best Practices

### Development

✅ Use virtual environments  
✅ Test DAGs before deploying  
✅ Use version control (Git)  
✅ Follow naming conventions  
✅ Document your DAGs  
✅ Use variables for configuration  
✅ Set appropriate timeouts  

### Production

✅ Use PostgreSQL or MySQL (not SQLite)  
✅ Use LocalExecutor or CeleryExecutor  
✅ Enable authentication and RBAC  
✅ Set up monitoring and alerting  
✅ Regular database backups  
✅ Use secrets backend for credentials  
✅ Implement proper logging  
✅ Set resource limits  

### Security

✅ Use RBAC for access control  
✅ Store credentials in Connections  
✅ Use secrets backend (AWS Secrets Manager, etc.)  
✅ Enable HTTPS for web server  
✅ Regular security updates  
✅ Limit network access  

---

## Upgrading Airflow

```bash
# Backup database
pg_dump airflow > airflow_backup.sql

# Stop services
pkill -f "airflow webserver"
pkill -f "airflow scheduler"

# Upgrade Airflow
pip install --upgrade apache-airflow==2.8.0

# Upgrade database
airflow db upgrade

# Start services
airflow webserver &
airflow scheduler &
```

---

## Resources

- **Official Docs**: https://airflow.apache.org/docs/
- **GitHub**: https://github.com/apache/airflow
- **Slack**: https://apache-airflow.slack.com/
- **Stack Overflow**: Tag `airflow`

---

## Quick Start Checklist

- [ ] Install Python 3.8+
- [ ] Create virtual environment
- [ ] Install Airflow
- [ ] Initialize database
- [ ] Create admin user
- [ ] Start webserver
- [ ] Start scheduler
- [ ] Access UI (http://localhost:8080)
- [ ] Create first DAG
- [ ] Test DAG
- [ ] Trigger DAG run

---

**You're ready to start building data pipelines with Apache Airflow!** 🚀
