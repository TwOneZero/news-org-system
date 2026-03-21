# Deployment and Operations Guide

This guide covers deploying and operating the news-org-system in production.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Running the System](#running-the-system)
- [MongoDB Configuration](#mongodb-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling Considerations](#scaling-considerations)
- [Backup and Recovery](#backup-and-recovery)
- [Production Checklist](#production-checklist)

---

## Environment Setup

### Prerequisites

- **Python**: 3.12 or higher
- **MongoDB**: 4.4 or higher
- **Operating System**: Linux, macOS, or Windows

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/news-org-system.git
cd news-org-system

# Install dependencies
pip install -e .

# Or with uv (faster)
uv pip install -e .
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=news_org
MONGO_COLLECTION=articles

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
```

**Required Variables**:
- `MONGO_URI`: MongoDB connection string
- `MONGO_DATABASE`: Database name

**Optional Variables**:
- `MONGO_COLLECTION`: Collection name (default: `articles`)
- `API_HOST`: API server host (default: `0.0.0.0`)
- `API_PORT`: API server port (default: `8000`)
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

---

## Running the System

### CLI Mode

Run collection commands via CLI:

```bash
# Collect from all sources
news-org collect --days-back 1 --limit 50

# Collect from specific source
news-org collect --source yonhap_economy --limit 100

# View statistics
news-org stats

# Run as daemon (hourly collection)
news-org daemon --interval 3600
```

**CLI Entry Point**: `news-org` (defined in `pyproject.toml`)

### API Mode

Run the REST API server:

```bash
# Using the installed command
news-org-api

# Or with Python module
python -m news_org_system.api.main

# Or with uvicorn directly
uvicorn news_org_system.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

**API Entry Point**: `news-org-api` (defined in `pyproject.toml`)

**Development Mode** (with auto-reload):
```bash
uvicorn news_org_system.api.main:app --reload
```

**Production Mode**:
```bash
uvicorn news_org_system.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

### Systemd Service (Linux)

Create `/etc/systemd/system/news-org-api.service`:

```ini
[Unit]
Description=News Organization System API
After=network.target mongodb.service

[Service]
Type=notify
User=newsorg
Group=newsorg
WorkingDirectory=/opt/news-org-system
Environment="PATH=/opt/news-org-system/venv/bin"
ExecStart=/opt/news-org-system/venv/bin/news-org-api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable news-org-api
sudo systemctl start news-org-api
sudo systemctl status news-org-api
```

### Docker Deployment

**Dockerfile** (if available):

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install -e .

# Copy application
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run API server
CMD ["news-org-api"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: news_org

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      MONGO_URI: mongodb://mongodb:27017
      MONGO_DATABASE: news_org
      API_HOST: 0.0.0.0
      API_PORT: 8000
    depends_on:
      - mongodb
    restart: always

volumes:
  mongodb_data:
```

Run with Docker Compose:
```bash
docker-compose up -d
```

---

## MongoDB Configuration

### Local MongoDB

**Install MongoDB**:

```bash
# macOS (Homebrew)
brew install mongodb-community
brew services start mongodb-community

# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb

# Windows
# Download from https://www.mongodb.com/try/download/community
```

**Create Database**:

```bash
# Connect to MongoDB
mongosh

# Create database (automatically created on first write)
use news_org

# Create collection (automatically created on first insert)
db.createCollection("articles")
```

### MongoDB Atlas (Cloud)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get connection string
4. Update environment variable:

```bash
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/news_org?retryWrites=true&w=majority
```

### Indexing

The system creates indexes automatically on first run. Manual index creation:

```python
from news_org_system.storage import MongoStore

store = MongoStore()
store._create_indexes()
```

**Indexes Created**:
- `url`: Unique index (for duplicate prevention)
- `source`: Index (for source filtering)
- `published_at`: Index (for date range queries)
- Compound index: `{source: 1, published_at: -1}`

### MongoDB Security

**Authentication**:
```bash
# Create admin user
mongosh
use admin
db.createUser({
  user: "admin",
  pwd: "strong_password",
  roles: ["userAdminAnyDatabase"]
})

# Create application user
use news_org
db.createUser({
  user: "newsorg",
  pwd: "strong_password",
  roles: ["readWrite"]
})
```

**Update connection string**:
```bash
MONGO_URI=mongodb://newsorg:strong_password@localhost:27017/news_org
```

**Enable Authentication**:
```bash
# Edit /etc/mongod.conf
security:
  authorization: enabled

# Restart MongoDB
sudo systemctl restart mongodb
```

---

## Monitoring and Logging

### Logging Configuration

**Default Logging**:
- Level: INFO
- Format: Timestamp, level, module, message
- Output: stdout

**Customize Logging**:

```python
import logging

# Set log level via environment
LOG_LEVEL=DEBUG

# Or in code
logging.getLogger("news_org_system").setLevel(logging.DEBUG)
```

### Log Levels

| Level | Description | Usage |
|-------|-------------|-------|
| DEBUG | Detailed debugging information | Development |
| INFO | General information about operations | Production |
| WARNING | Something unexpected but not critical | Production |
| ERROR | Error occurred, operation failed | Production |

### Monitoring Metrics

**Key Metrics to Monitor**:

1. **Collection Metrics**:
   - Articles fetched per source
   - Articles saved (new) vs skipped (duplicates)
   - Collection duration per source
   - Collection failures

2. **Storage Metrics**:
   - Total articles in database
   - Database size
   - Index usage
   - Query performance

3. **API Metrics**:
   - Request rate (requests per second)
   - Response times
   - Error rate (4xx, 5xx)
   - Active connections

### Monitoring Tools

**MongoDB Metrics**:
```bash
# MongoDB built-in stats
mongosh
use news_org
db.stats()
db.articles.stats()

# Index usage
db.articles.aggregate([{$indexStats: {}}])
```

**System Metrics**:
```bash
# CPU, memory, disk
top
htop
df -h

# MongoDB process
ps aux | grep mongod
```

**API Metrics** (future):
- Integrate Prometheus for metrics collection
- Use Grafana for dashboards

### Health Checks

**API Health Check**:
```bash
curl http://localhost:8000/health
```

**Database Health Check**:
```python
from news_org_system.storage import MongoStore

store = MongoStore()
try:
    store.db.command('ping')
    print("MongoDB is healthy")
except Exception as e:
    print(f"MongoDB error: {e}")
```

---

## Scaling Considerations

### Vertical Scaling (Scale Up)

**Increase Resources**:
- More CPU cores (for feed parsing)
- More RAM (for MongoDB cache)
- Faster storage (SSD for MongoDB)

**When to Scale Up**:
- Collection takes too long
- API response times are slow
- Database queries are slow

### Horizontal Scaling (Scale Out)

**Multiple API Workers**:
```bash
uvicorn news_org_system.api.main:app \
  --workers 4 \
  --host 0.0.0.0 \
  --port 8000
```

**Load Balancer** (nginx):
```nginx
upstream news_api {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://news_api;
    }
}
```

**MongoDB Replica Set**:
```javascript
// Initialize replica set
rs.initiate({
  _id: "rs0",
  members: [
    {_id: 0, host: "mongodb1:27017"},
    {_id: 1, host: "mongodb2:27017"},
    {_id: 2, host: "mongodb3:27017"}
  ]
})
```

**Update Connection String**:
```bash
MONGO_URI=mongodb://mongodb1:27017,mongodb2:27017,mongodb3:27017/?replicaSet=rs0
```

### Caching

**Future**: Add Redis caching layer for:
- Frequently accessed articles
- Feed parsing results
- Query results

---

## Backup and Recovery

### MongoDB Backup

**Create Backup**:
```bash
# mongodump (creates binary backup)
mongodump --db=news_org --out=/backups/mongo/$(date +%Y%m%d)

# Or with authentication
mongodump \
  --uri="mongodb://user:pass@localhost:27017/news_org" \
  --out=/backups/mongo/$(date +%Y%m%d)
```

**Automated Backup (cron)**:
```bash
# Daily backup at 2 AM
0 2 * * * /usr/bin/mongodump --db=news_org --out=/backups/mongo/$(date +\%Y\%m\%d)

# Keep last 7 days, delete older
0 3 * * * find /backups/mongo/ -type d -mtime +7 -exec rm -rf {} \;
```

### MongoDB Restore

**Restore from Backup**:
```bash
mongorestore --db=news_org /backups/mongo/20240321/news_org
```

### Export/Import (JSON)

**Export to JSON**:
```bash
mongoexport --db=news_org --collection=articles --out=articles.json
```

**Import from JSON**:
```bash
mongoimport --db=news_org --collection=articles --file=articles.json
```

### Disaster Recovery

**Recovery Steps**:

1. **Assess Damage**:
   ```bash
   # Check database integrity
   mongosh
   use news_org
   db.stats()
   db.articles.countDocuments({})
   ```

2. **Stop Application**:
   ```bash
   sudo systemctl stop news-org-api
   ```

3. **Restore from Backup**:
   ```bash
   mongorestore --db=news_org /backups/mongo/latest/news_org
   ```

4. **Verify Restore**:
   ```bash
   mongosh
   use news_org
   db.articles.countDocuments({})
   ```

5. **Restart Application**:
   ```bash
   sudo systemctl start news-org-api
   ```

---

## Production Checklist

### Pre-Deployment

- [ ] MongoDB installed and configured
- [ ] Environment variables set (`.env` file)
- [ ] Database indexes created
- [ ] MongoDB authentication enabled
- [ ] Firewall configured (allow port 8000, block MongoDB port)
- [ ] SSL/TLS configured (if using HTTPS)
- [ ] Log rotation configured
- [ ] Monitoring setup (logging, metrics)
- [ ] Backup strategy implemented
- [ ] Documentation updated

### Post-Deployment

- [ ] Health check passing (`/health` endpoint)
- [ ] Collection test run successfully
- [ ] API endpoints responding correctly
- [ ] Logs being written
- [ ] MongoDB backup scheduled
- [ ] Monitoring alerts configured
- [ ] Performance baseline measured

### Security Checklist

- [ ] Strong MongoDB password set
- [ ] MongoDB authentication enabled
- [ ] MongoDB not exposed to public internet
- [ ] API rate limiting configured (if public)
- [ ] CORS origins restricted
- [ ] HTTPS enabled (if public)
- [ ] Secrets not in code repository
- [ ] Regular security updates applied

### Performance Checklist

- [ ] MongoDB indexes created
- [ ] Query performance tested
- [ ] Collection performance monitored
- [ ] Sufficient resources (CPU, RAM, disk)
- [ ] Log level set to INFO (not DEBUG)
- [ ] Connection pooling configured
- [ ] Caching considered (if needed)

---

## Troubleshooting

### Common Issues

**1. MongoDB Connection Failed**
```bash
# Check MongoDB is running
sudo systemctl status mongodb

# Check connection string
echo $MONGO_URI

# Test connection
mongosh $MONGO_URI
```

**2. Collection Returns Zero Articles**
```bash
# Check if feed is accessible
curl https://example.com/rss.xml

# Check feed is in registry
news-org stats --source example_source

# Check logs
journalctl -u news-org-api -f
```

**3. API Not Responding**
```bash
# Check API is running
sudo systemctl status news-org-api

# Check port is listening
netstat -tlnp | grep 8000

# Check logs
journalctl -u news-org-api -n 100
```

**4. High Memory Usage**
```bash
# Check MongoDB memory
mongosh
db.serverStatus().mem

# Check API process memory
ps aux | grep news-org-api

# Restart services
sudo systemctl restart mongodb
sudo systemctl restart news-org-api
```

---

## Maintenance

### Regular Maintenance Tasks

**Daily**:
- Monitor logs for errors
- Check collection success rates
- Verify backup completion

**Weekly**:
- Review database size and growth
- Check index usage and performance
- Review error logs

**Monthly**:
- Test backup restore procedure
- Review and update dependencies
- Performance audit
