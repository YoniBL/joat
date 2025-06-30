# 🚀 JOAT Deployment Guide

This guide will help you deploy your JOAT application as a live web app.

## 📋 Prerequisites

- Docker and Docker Compose installed
- API keys for the models you want to use
- A domain name (for production)
- SSL certificate (for production)

## 🏃‍♂️ Quick Start (Local Development)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd joat
```

### 2. Configure Environment

```bash
# Copy environment template
cp api/env.example .env

# Edit .env with your API keys
nano .env
```

### 3. Deploy with Docker

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 4. Access Your App

- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🌐 Production Deployment

### Option 1: Cloud Deployment (Recommended)

#### A. Deploy to Railway

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Deploy**:
   ```bash
   railway login
   railway init
   railway up
   ```

#### B. Deploy to Render

1. **Connect your GitHub repository**
2. **Create a new Web Service**
3. **Configure environment variables**
4. **Deploy**

#### C. Deploy to Fly.io

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy**:
   ```bash
   fly launch
   fly deploy
   ```

### Option 2: VPS Deployment

#### A. Set up your VPS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### B. Deploy Application

```bash
# Clone repository
git clone <your-repo-url>
cd joat

# Configure environment
cp api/env.example .env
nano .env

# Deploy
./deploy.sh
```

#### C. Set up Nginx (Optional)

```bash
# Install Nginx
sudo apt install nginx

# Configure Nginx
sudo nano /etc/nginx/sites-available/joat
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/joat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 3: Kubernetes Deployment

#### A. Create Kubernetes manifests

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: joat-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: joat
  template:
    metadata:
      labels:
        app: joat
    spec:
      containers:
      - name: joat
        image: your-registry/joat:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEEPSEEK_API_KEY
          valueFrom:
            secretKeyRef:
              name: joat-secrets
              key: deepseek-api-key
```

#### B. Deploy to Kubernetes

```bash
kubectl apply -f k8s/
```

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False  # Set to False in production

# CORS Settings
ALLOWED_ORIGINS=https://your-domain.com

# Model API Keys
DEEPSEEK_API_KEY=your_key_here
LLAMA3_API_KEY=your_key_here
WIZARDMATH_API_KEY=your_key_here
GEMMA_API_KEY=your_key_here
LLAMA3_CHAT_API_KEY=your_key_here
OPENLLAMA_API_KEY=your_key_here
LLAVA_NEXT_API_KEY=your_key_here

# Security
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🔒 Security Considerations

### 1. API Key Management

- Use environment variables or secrets management
- Never commit API keys to version control
- Rotate keys regularly

### 2. CORS Configuration

```python
# In production, specify exact origins
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 3. Rate Limiting

Consider adding rate limiting to your API:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/query")
@limiter.limit("10/minute")
async def process_query(request: QueryRequest):
    # Your code here
```

## 📊 Monitoring and Logging

### 1. Health Checks

The application includes health check endpoints:

```bash
curl http://your-domain.com/health
```

### 2. Logging

Configure logging in production:

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure file logging
file_handler = RotatingFileHandler('joat.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
```

### 3. Monitoring Services

Consider integrating with:
- **Sentry** for error tracking
- **New Relic** for performance monitoring
- **Datadog** for comprehensive monitoring

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy JOAT

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build and push Docker image
      run: |
        docker build -t your-registry/joat:${{ github.sha }} .
        docker push your-registry/joat:${{ github.sha }}
    
    - name: Deploy to production
      run: |
        # Your deployment commands here
```

## 🚨 Troubleshooting

### Common Issues

1. **Application won't start**
   ```bash
   docker-compose logs
   ```

2. **API keys not working**
   ```bash
   # Check environment variables
   docker-compose exec joat-app env | grep API_KEY
   ```

3. **CORS errors**
   - Verify `ALLOWED_ORIGINS` configuration
   - Check frontend URL matches allowed origins

4. **High memory usage**
   - Monitor container resources: `docker stats`
   - Consider scaling horizontally

### Performance Optimization

1. **Enable caching**
2. **Use CDN for static assets**
3. **Implement connection pooling**
4. **Monitor and optimize database queries**

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale to multiple instances
docker-compose up -d --scale joat-app=3
```

### Load Balancing

Use Nginx or HAProxy for load balancing:

```nginx
upstream joat_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}
```

## 🎉 Success!

Your JOAT application is now live! 

- **URL**: https://your-domain.com
- **API**: https://your-domain.com/docs
- **Health**: https://your-domain.com/health

Remember to:
- Monitor your application regularly
- Keep dependencies updated
- Backup your data
- Monitor API usage and costs 

python app.py
# or
python app_launcher.py 