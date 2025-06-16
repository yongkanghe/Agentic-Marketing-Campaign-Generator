# Environment Configuration Guide

**Author:** JP + 2025-06-16

## Overview

The AI Marketing Campaign Post Generator uses intelligent environment-based API URL resolution to work seamlessly from local development to Google Cloud Platform production deployment.

## How It Works

The frontend automatically detects and configures the backend API URL based on the environment:

### 1. Development Environment
- **No configuration needed** 
- Auto-detects `http://localhost:8000` for local development
- Supports network development (e.g., `http://192.168.1.100:8000` for mobile testing)

### 2. Production Environment
- Uses `VITE_API_BASE_URL` environment variable
- Fallback to `/api` for same-origin deployments

## Environment Variable Configuration

### Local Development (MVP)
```bash
# No configuration needed - auto-detects backend
# Frontend: http://localhost:8080
# Backend:  http://localhost:8000 (auto-detected)
```

### Staging Environment
```bash
VITE_API_BASE_URL=https://staging-api.run.app
```

### Production Environment (GCP Cloud Run)
```bash
VITE_API_BASE_URL=https://ai-marketing-api-[hash]-uc.a.run.app
```

### Same-Origin Production Deployment
```bash
VITE_API_BASE_URL=/api
```

## Deployment Scenarios

### 1. Google Cloud Platform (Recommended)

**Cloud Run Deployment:**
```bash
# Frontend Cloud Run
VITE_API_BASE_URL=https://your-backend-service-[hash]-uc.a.run.app

# Same Cloud Run (frontend + backend)
VITE_API_BASE_URL=/api
```

### 2. Alternative Hosting

**Heroku:**
```bash
VITE_API_BASE_URL=https://your-app-name.herokuapp.com
```

**Custom Domain:**
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
```

## Benefits of This Approach

1. **Zero Configuration Development**: Developers can start immediately with `make dev`
2. **Environment Flexibility**: Same codebase works across all environments
3. **Production Ready**: Proper environment variable usage for cloud deployment
4. **Network Development**: Automatic support for mobile device testing
5. **Graceful Fallbacks**: Intelligent defaults for different scenarios

## Error Handling

- **No Mock Fallbacks**: Real API failures show proper error messages
- **Connection Issues**: Clear error messages guide users to troubleshoot
- **Environment Misconfig**: Console logging helps debug configuration issues

## Testing Configuration

Check current configuration in browser console (development mode):
```
🔗 API Base URL: http://localhost:8000
🌍 Environment: development
```

## Makefile Integration

The `make dev` command is optimized for this configuration:
- Starts backend on port 8000
- Starts frontend on port 8080 (or 8081 if occupied)
- Automatic environment detection and connection

## Best Practices

1. **Development**: Use `make dev` for consistent local environment
2. **Staging**: Set `VITE_API_BASE_URL` to staging backend
3. **Production**: Use Cloud Run with proper environment variables
4. **Monitoring**: Check browser console for API configuration confirmation
5. **Testing**: Use network IP for mobile device testing

## Troubleshooting

### API Connection Issues
1. Check browser console for API base URL
2. Verify backend is running on expected port
3. Check CORS configuration in backend
4. Validate environment variable setting

### Development Setup
```bash
# Start complete development environment
make dev

# Check health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:8080
```

This configuration ensures seamless transition from MVP development to production GCP deployment while maintaining best practices for environment management. 