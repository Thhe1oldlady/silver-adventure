# Silver Adventure - Deployment Guide

## Overview

This guide covers deployment options for the Silver Adventure application, from development to production environments.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Environment Configuration](#environment-configuration)
- [Docker Deployment](#docker-deployment)
- [Cloud Platform Deployment](#cloud-platform-deployment)
- [Production Considerations](#production-considerations)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Scaling](#scaling)
- [Security](#security)

## Deployment Options

### 1. Local Development
```bash
# Quick start for development
uvicorn src.silver_adventure.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Docker Container
```bash
# Build and run with Docker
docker build -t silver-adventure .
docker run -p 8000:8000 silver-adventure
```

### 3. Cloud Platforms
- **Heroku**: Easy deployment with git integration
- **AWS**: EC2, ECS, or Lambda deployment
- **Google Cloud**: App Engine or Cloud Run
- **Azure**: App Service or Container Instances
- **Railway**: Simple container deployment

### 4. Traditional Server
- **Linux VM**: Ubuntu/CentOS with systemd
- **Windows Server**: IIS or Windows Services
- **VPS**: Any virtual private server

## Environment Configuration

### Production Environment Variables
```env
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-production-key
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database
DATABASE_URL=postgresql://user:password@localhost/silver_adventure

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@your-domain.com

# Security
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=*

# Performance
MAX_REQUESTS=1000
TIMEOUT=30

# Features
ENABLE_EMAIL_SENDING=true
ENABLE_CHURN_PREDICTION=true
ENABLE_ANALYTICS=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/silver-adventure/app.log

# Monitoring
MONITORING_SERVICE_URL=https://your-monitoring-service.com
ANALYTICS_API_KEY=your-analytics-key
```

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY pyproject.toml .

# Install application
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/models

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.silver_adventure.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:password@db:5432/silver_adventure
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./models:/app/models
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=silver_adventure
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

### Build and Deploy
```bash
# Build image
docker build -t silver-adventure:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Scale application
docker-compose up -d --scale app=3
```

## Cloud Platform Deployment

### Heroku
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login and create app
heroku login
heroku create silver-adventure-app

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set SMTP_USERNAME=your-email@gmail.com
heroku config:set SMTP_PASSWORD=your-app-password

# Deploy
git push heroku main

# Scale
heroku ps:scale web=2
```

**Procfile**:
```
web: uvicorn src.silver_adventure.main:app --host 0.0.0.0 --port $PORT --workers 4
```

### AWS ECS
```yaml
# ecs-task-definition.json
{
  "family": "silver-adventure",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "silver-adventure",
      "image": "your-account.dkr.ecr.region.amazonaws.com/silver-adventure:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/silver-adventure",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/silver-adventure', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/silver-adventure']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: [
      'run', 'deploy', 'silver-adventure',
      '--image', 'gcr.io/$PROJECT_ID/silver-adventure',
      '--platform', 'managed',
      '--region', 'us-central1',
      '--allow-unauthenticated'
    ]
```

## Production Considerations

### 1. Database Configuration
```python
# Use PostgreSQL for production
DATABASE_URL=postgresql://user:password@host:5432/silver_adventure

# Connection pooling
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=30
SQLALCHEMY_POOL_TIMEOUT=30
```

### 2. Caching
```python
# Redis for caching
REDIS_URL=redis://localhost:6379/0
CACHE_DEFAULT_TIMEOUT=300
```

### 3. Load Balancing
```nginx
# nginx.conf
upstream app {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. SSL/TLS Configuration
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring and Maintenance

### 1. Health Checks
```python
# Built-in health check endpoint
GET /health

# Custom health checks
def custom_health_check():
    # Check database connectivity
    # Check external services
    # Check disk space
    # Check memory usage
    return {"status": "healthy"}
```

### 2. Logging
```python
# Structured logging
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log aggregation (ELK Stack, Splunk, etc.)
```

### 3. Metrics and Monitoring
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('active_users', 'Active users')
```

### 4. Alerting
```yaml
# AlertManager configuration
groups:
  - name: silver-adventure
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status="5xx"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High error rate detected
```

## Scaling

### 1. Horizontal Scaling
```bash
# Docker Compose
docker-compose up -d --scale app=5

# Kubernetes
kubectl scale deployment silver-adventure --replicas=5

# Cloud platforms
# AWS ECS, Google Cloud Run, Azure Container Instances
```

### 2. Vertical Scaling
```yaml
# Increase resources
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

### 3. Auto-scaling
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: silver-adventure-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: silver-adventure
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Security

### 1. Environment Variables
```bash
# Never commit secrets to version control
# Use environment variables or secret management
# Rotate secrets regularly
```

### 2. Network Security
```yaml
# Use HTTPS only
# Implement proper CORS policies
# Use security headers
# Implement rate limiting
```

### 3. Authentication
```python
# Implement proper authentication
# Use JWT tokens
# Implement role-based access control
```

### 4. Data Security
```python
# Encrypt sensitive data
# Use parameterized queries
# Implement proper validation
# Regular security audits
```

## Troubleshooting

### Common Issues

**1. Application Won't Start**
- Check environment variables
- Verify database connectivity
- Check port availability
- Review logs

**2. High Memory Usage**
- Monitor memory consumption
- Check for memory leaks
- Adjust worker count
- Optimize data processing

**3. Slow Performance**
- Enable caching
- Optimize database queries
- Use CDN for static assets
- Implement connection pooling

**4. Database Connection Issues**
- Check connection string
- Verify network connectivity
- Monitor connection pool
- Check database health

### Log Analysis
```bash
# View application logs
docker-compose logs -f app

# Search for errors
grep -i error /var/log/silver-adventure/app.log

# Monitor real-time logs
tail -f /var/log/silver-adventure/app.log
```

## Backup and Recovery

### 1. Database Backup
```bash
# PostgreSQL backup
pg_dump -h localhost -U user -d silver_adventure > backup.sql

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U user -d silver_adventure > /backups/silver_adventure_${DATE}.sql
```

### 2. Application Data Backup
```bash
# Backup models and data
tar -czf backup_${DATE}.tar.gz models/ data/ logs/
```

### 3. Recovery Procedures
```bash
# Restore database
psql -h localhost -U user -d silver_adventure < backup.sql

# Restore application data
tar -xzf backup.tar.gz
```

## Performance Optimization

### 1. Application Optimization
- Use async/await for I/O operations
- Implement caching strategies
- Optimize database queries
- Use connection pooling

### 2. Infrastructure Optimization
- Use CDN for static assets
- Implement load balancing
- Use appropriate instance sizes
- Monitor resource utilization

### 3. Database Optimization
- Create proper indexes
- Optimize query performance
- Use read replicas
- Implement query caching

## Conclusion

This deployment guide provides comprehensive instructions for deploying Silver Adventure in various environments. Choose the deployment method that best fits your requirements and infrastructure capabilities.

For additional support:
- Check the troubleshooting section
- Review application logs
- Consult cloud provider documentation
- Submit issues on GitHub