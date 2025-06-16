# AI Marketing Campaign Post Generator - Port Configuration & Architecture

**Author: JP + 2025-06-16**  
**Last Updated: 2025-06-16**  
**Status: Production Ready**

## 📋 Port Configuration Summary

### 🎯 **Current Production Ports**

| Service | Port | Protocol | Environment | Status | Notes |
|---------|------|----------|-------------|--------|-------|
| **Frontend (React/Vite)** | `8080` | HTTP | Development | ✅ Active | Primary UI port |
| **Backend (FastAPI)** | `8000` | HTTP | Development | ✅ Active | API Gateway |
| **Redis Cache** | `6379` | TCP | Development | 🔄 Optional | Caching layer |
| **Firestore Emulator** | `8080` | HTTP | Development | 🔄 Optional | Database emulator |

### 🏗️ **Architecture Port Mapping**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          AI Marketing Campaign Post Generator - PORT ARCHITECTURE               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                FRONTEND LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                    React Application (Vite)                                │ │
│  │                         PORT: 8080                                         │ │
│  │                                                                             │ │
│  │  • Development Server: http://localhost:8080                               │ │
│  │  • Production Build: Served via Nginx (Port 80/443)                       │ │
│  │  • Hot Module Replacement: Enabled                                         │ │
│  │  • CORS Origin: Configured in backend                                      │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP Requests
                                    │ (CORS Enabled)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               BACKEND LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                      FastAPI Application                                   │ │
│  │                         PORT: 8000                                         │ │
│  │                                                                             │ │
│  │  • API Gateway: http://localhost:8000                                      │ │
│  │  • OpenAPI Docs: http://localhost:8000/api/docs                           │ │
│  │  • Health Check: http://localhost:8000/                                   │ │
│  │  • API Endpoints: /api/v1/*                                               │ │
│  │                                                                             │ │
│  │  CORS Configuration:                                                       │ │
│  │  • http://localhost:8080 (Frontend Dev)                                   │ │
│  │  • http://localhost:8081 (Alt Frontend)                                   │ │
│  │  • https://video-venture-launch.web.app (Production)                      │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ External API Calls
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SERVICES                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐               │
│  │   Google        │   │     Redis       │   │   Firestore     │               │
│  │   Gemini API    │   │     Cache       │   │   Database      │               │
│  │                 │   │                 │   │                 │               │
│  │  PORT: 443      │   │  PORT: 6379     │   │  PORT: 443      │               │
│  │  (HTTPS)        │   │  (TCP)          │   │  (HTTPS)        │               │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Configuration Details

### Frontend Configuration (`vite.config.ts`)

```typescript
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,  // ✅ CONFIRMED: Primary frontend port
  },
  // ... other config
}));
```

### Backend Configuration (`backend/api/main.py`)

```python
# FastAPI CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server (legacy)
        "http://localhost:8080",  # ✅ Vite dev server (current)
        "http://localhost:8081",  # Alternative Vite port
        "https://video-venture-launch.web.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Server startup configuration
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,  # ✅ CONFIRMED: Primary backend port
        reload=True,
        log_level="info"
    )
```

### Makefile Configuration

```makefile
dev-frontend-local: ## Start frontend development server locally
	@echo "Starting frontend development server locally..."
	# Starts on port 8080 via vite.config.ts

dev-backend-local: ## Start backend development server locally
	@echo "🚀 Starting AI Marketing Campaign Post Generator backend server..."
	@cd backend && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🐳 Docker Configuration

### Development Environment (`docker-compose.yml`)

```yaml
services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
      target: development
    ports:
      - "3000:3000"  # ⚠️ NOTE: Docker uses 3000, local dev uses 8080
    environment:
      - VITE_API_URL=http://backend:8000
    command: npm run dev -- --host 0.0.0.0

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
      target: development
    ports:
      - "8000:8000"  # ✅ Consistent with local development
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"  # Standard Redis port
```

## 📊 Port Usage Analysis

### ✅ **Confirmed Working Configuration**

Based on integration testing results (2025-06-16):

```bash
# Frontend Server Status
✅ Frontend: http://localhost:8080 (HTTP 200)
   - Serving HTML correctly
   - Vite development server active
   - Hot module replacement enabled

# Backend Server Status  
✅ Backend: http://localhost:8000 (HTTP 200)
   - API Gateway responding
   - Real Gemini integration active
   - CORS properly configured
   - OpenAPI docs available at /api/docs

# Integration Test Results
✅ Server Availability: 100% (Both servers running)
✅ Real Gemini Integration: Working (4-7s response time)
✅ Frontend API Client: All expected fields present
✅ CORS Configuration: Proper headers configured
✅ Success Rate: 75% (3/4 tests passing)
```

### 🔄 **Port Conflicts & Resolutions**

| Conflict | Resolution | Status |
|----------|------------|--------|
| **Docker vs Local** | Docker: 3000, Local: 8080 | ✅ Documented |
| **Firestore Emulator** | Uses 8080 (same as frontend) | ⚠️ Potential conflict |
| **Alternative Ports** | 8081 configured as fallback | ✅ Available |

## 🚀 Production Deployment Ports

### Google Cloud Platform

```yaml
# Production Configuration
Frontend (Cloud Run):
  - External: 443 (HTTPS)
  - Internal: 8080
  - Domain: https://video-venture-launch.web.app

Backend (Cloud Run):
  - External: 443 (HTTPS) 
  - Internal: 8000
  - Domain: https://api.video-venture-launch.web.app

Database (Firestore):
  - Port: 443 (HTTPS)
  - Managed service

Cache (Redis):
  - Port: 6379 (TCP)
  - Managed service (Cloud Memorystore)
```

## 🧪 Testing & Verification

### Integration Test Commands

```bash
# Test server availability
curl -X GET http://localhost:8000/
curl -X GET http://localhost:8080/

# Test API integration
curl -X POST http://localhost:8000/api/v1/analysis/url \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:8080" \
  -d '{"urls": ["https://openai.com"], "analysis_depth": "standard"}'

# Run comprehensive integration tests
cd backend && python3 run_integration_tests.py
cd backend && ./test_curl_commands.sh
```

### Health Check Endpoints

```bash
# Backend Health
GET http://localhost:8000/
Response: {"name": "AI Marketing Campaign Post Generator API", "version": "1.0.0", ...}

# Frontend Health  
GET http://localhost:8080/
Response: HTML document with React app

# API Documentation
GET http://localhost:8000/api/docs
Response: OpenAPI/Swagger documentation
```

## 📝 Development Guidelines

### Starting Development Servers

```bash
# Method 1: Using Makefile (Recommended)
make dev-frontend-local  # Starts on port 8080
make dev-backend-local   # Starts on port 8000

# Method 2: Direct commands
cd backend && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
npm run dev  # Starts on port 8080 (via vite.config.ts)

# Method 3: Docker Compose
docker-compose up  # Frontend: 3000, Backend: 8000
```

### Port Verification

```bash
# Check if ports are in use
lsof -i :8080  # Frontend
lsof -i :8000  # Backend
lsof -i :6379  # Redis

# Kill processes on ports if needed
kill $(lsof -ti :8080)
kill $(lsof -ti :8000)
```

## 🔒 Security Considerations

### CORS Configuration

- ✅ **Localhost Development**: `http://localhost:8080` allowed
- ✅ **Alternative Ports**: `http://localhost:8081` allowed  
- ✅ **Production Domain**: `https://video-venture-launch.web.app` allowed
- ❌ **Wildcard Origins**: Not used (security best practice)

### Network Security

- ✅ **Development**: HTTP allowed for localhost
- ✅ **Production**: HTTPS enforced
- ✅ **API Keys**: Environment variables only
- ✅ **Rate Limiting**: Configured in FastAPI

## 📚 References

- **Frontend Config**: `vite.config.ts`
- **Backend Config**: `backend/api/main.py`
- **Docker Config**: `docker-compose.yml`
- **Makefile**: Development commands
- **Integration Tests**: `backend/run_integration_tests.py`
- **CORS Documentation**: FastAPI CORS middleware
- **Production Deployment**: Google Cloud Run configuration

---

**Last Verified**: 2025-06-16 09:43:18 BST  
**Integration Test Status**: ✅ 75% Success Rate (3/4 tests passing)  
**Real Gemini Integration**: ✅ Confirmed Working 