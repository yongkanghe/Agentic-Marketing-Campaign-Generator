# Environment Configuration Guide

**Author:** JP + 2025-06-16

## Overview

This document outlines the comprehensive environment configuration for the AI Marketing Campaign Post Generator, including API keys, model selection, cost controls, and deployment settings.

## Environment Variables

### Google AI Configuration

#### Gemini API Configuration
```bash
# Required: Your Google AI API key
GEMINI_API_KEY=your_gemini_api_key_here

# Model Selection: Choose your preferred Gemini model
GEMINI_MODEL=gemini-2.5-flash
# Alternatives: gemini-1.5-pro, gemini-1.5-flash
```

#### Image Generation Configuration
```bash
# Image Model: Configure which Imagen model to use
IMAGE_MODEL=imagen-3.0-generate-002
# Alternatives: imagen-2.0-generate, imagen-3.0-fast

# Video Model: Configure which Veo model to use
VIDEO_MODEL=veo-2
# Alternatives: veo-1, video-generation-experimental
```

### Content Generation Limits & Cost Control

#### Post Generation Limits
```bash
# Text + URL Posts: Higher limit (text-only generation)
MAX_TEXT_URL_POSTS=10

# Text + Image Posts: Limited for cost control
MAX_TEXT_IMAGE_POSTS=4

# Text + Video Posts: Limited for cost control  
MAX_TEXT_VIDEO_POSTS=4
```

**Cost Management Strategy:**
- **Text + URL**: Higher limits (10 posts) as these only use Gemini text generation
- **Text + Image**: Limited to 4 posts to control Imagen API costs
- **Text + Video**: Limited to 4 posts to control Veo API costs

#### API Rate Limiting
```bash
# Daily Usage Limits
DAILY_GEMINI_REQUESTS=1000
DAILY_IMAGE_GENERATIONS=100
DAILY_VIDEO_GENERATIONS=50

# Rate Limiting (requests per minute)
GEMINI_RATE_LIMIT=100
IMAGE_GENERATION_RATE_LIMIT=20
VIDEO_GENERATION_RATE_LIMIT=10
```

### API Configuration

#### Backend API Settings
```bash
# Backend API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=15000

# Frontend Configuration  
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Agentic-Marketing-Campaign-Generator
VITE_APP_VERSION=1.0.0
```

### Database Configuration

#### SQLite (Development)
```bash
# Local SQLite Database
DATABASE_URL=sqlite:///./data/campaigns.db
DATABASE_BACKUP_INTERVAL=3600
```

#### PostgreSQL (Production)
```bash
# Production Database (Google Cloud SQL)
# DATABASE_URL=postgresql://user:password@host:port/database
```

### Development Configuration

#### Debug & Logging
```bash
DEBUG=true
LOG_LEVEL=INFO

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:8081
```

#### Security
```bash
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here
```

### Production Configuration (Google Cloud)

#### Google Cloud Platform Settings
```bash
# Google Cloud Project Configuration
# GOOGLE_CLOUD_PROJECT=your_project_id
# GOOGLE_CLOUD_REGION=us-central1
# CLOUD_RUN_SERVICE_NAME=ai-marketing-generator

# Production API URLs
# API_BASE_URL=https://your-domain.run.app
# VITE_API_BASE_URL=https://your-domain.run.app
```

### Monitoring & Analytics

#### Optional Services
```bash
# Google Analytics
# VITE_GA_TRACKING_ID=your_ga_tracking_id

# Error Tracking
# SENTRY_DSN=your_sentry_dsn
```

## Configuration Files

### Create .env File
```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env
```

### Environment Validation
The application validates required environment variables on startup:

1. **GEMINI_API_KEY**: Required for AI functionality
2. **Model configurations**: Use defaults if not specified
3. **Cost limits**: Use defaults if not specified

## Model Selection Guide

### Gemini Models
- **gemini-2.5-flash**: Latest preview with AFC support
- **gemini-1.5-pro**: Stable, high-quality responses
- **gemini-1.5-flash**: Faster, cost-effective option

### Imagen Models
- **imagen-3.0-generate-002**: Latest, highest quality (recommended)
- **imagen-2.0-generate**: Stable, lower cost option
- **imagen-3.0-fast**: Faster generation, slightly lower quality

### Veo Models
- **veo-2**: Latest video generation model (recommended)
- **veo-1**: Previous generation, stable
- **video-generation-experimental**: Experimental features

## Cost Management Best Practices

### 1. Monitor Usage
```bash
# Set up daily monitoring
DAILY_GEMINI_REQUESTS=1000
DAILY_IMAGE_GENERATIONS=100
DAILY_VIDEO_GENERATIONS=50
```

### 2. Adjust Limits Based on Budget
```bash
# Conservative settings
MAX_TEXT_IMAGE_POSTS=2
MAX_TEXT_VIDEO_POSTS=2

# Standard settings (recommended)
MAX_TEXT_IMAGE_POSTS=4
MAX_TEXT_VIDEO_POSTS=4

# Higher volume settings
MAX_TEXT_IMAGE_POSTS=6
MAX_TEXT_VIDEO_POSTS=6
```

### 3. Model Cost Comparison
- **Text Generation**: Lowest cost (Gemini only)
- **Image Generation**: Medium cost (Gemini + Imagen)
- **Video Generation**: Highest cost (Gemini + Veo)

## Environment-Specific Configurations

### Local Development
```bash
# .env.local
DEBUG=true
LOG_LEVEL=DEBUG
API_BASE_URL=http://localhost:8000
```

### Staging
```bash
# .env.staging
DEBUG=false
LOG_LEVEL=INFO
API_BASE_URL=https://staging-api.your-domain.com
```

### Production
```bash
# .env.production
DEBUG=false
LOG_LEVEL=WARNING
API_BASE_URL=https://api.your-domain.com
```

## Troubleshooting

### Common Issues

1. **Missing GEMINI_API_KEY**
   - Application runs in mock mode
   - Add valid API key to enable AI features

2. **Model Not Found Errors**
   - Check model names against Google AI documentation
   - Ensure API key has access to specified models

3. **Rate Limiting**
   - Adjust rate limit settings
   - Implement exponential backoff

4. **Cost Overruns**
   - Reduce post generation limits
   - Monitor daily usage limits

### Environment Validation Script
```bash
# Check environment configuration
make doctor

# Validate API connectivity
make health-check
```

## Security Considerations

### 1. API Key Management
- Never commit .env files to version control
- Use environment-specific API keys
- Rotate keys regularly

### 2. Production Security
- Use secrets management (Google Secret Manager)
- Enable API key restrictions
- Monitor API usage for anomalies

### 3. Access Control
- Implement proper CORS settings
- Use HTTPS in production
- Validate all user inputs

## Deployment Guide

### Local Deployment
```bash
# Install dependencies
make install

# Setup environment
cp .env.example .env
# Edit .env with your values

# Start application
make launch
```

### Google Cloud Deployment
```bash
# Set production environment variables
gcloud run services update ai-marketing-generator \
  --set-env-vars="GEMINI_API_KEY=$GEMINI_API_KEY" \
  --set-env-vars="IMAGE_MODEL=imagen-3.0-generate-002" \
  --set-env-vars="VIDEO_MODEL=veo-2"
```

## Configuration Updates

When updating environment configuration:

1. **Update .env.example** with new variables
2. **Update this documentation**
3. **Update application validation logic**
4. **Test in all environments**
5. **Update deployment scripts**

## Support

For configuration issues:
1. Check this documentation
2. Run `make doctor` for diagnostics
3. Review application logs
4. Consult Google AI API documentation 