# Video Venture Launch - Makefile
# Author: JP + 2024-12-19
# 3 Musketeers pattern for consistent development workflow
# Uses Docker, Docker Compose, and Make for environment consistency

.PHONY: help install install-frontend install-backend dev dev-frontend dev-backend test test-frontend test-backend test-ui test-api health-check launch runtime status-check build clean lint format docker-build docker-run docker-dev docker-test test-unit test-integration test-e2e test-coverage

# Environment Detection
DOCKER_AVAILABLE := $(shell command -v docker 2> /dev/null)
DOCKER_COMPOSE_AVAILABLE := $(shell command -v docker-compose 2> /dev/null)
NODE_AVAILABLE := $(shell command -v node 2> /dev/null)
BUN_AVAILABLE := $(shell command -v bun 2> /dev/null)
PYTHON_AVAILABLE := $(shell command -v python3 2> /dev/null)

# Default target
help: ## Show this help message
	@echo "Video Venture Launch - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: install-frontend install-backend ## Install all dependencies

install-frontend: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	@if command -v bun >/dev/null 2>&1; then \
		bun install; \
	elif command -v npm >/dev/null 2>&1; then \
		npm install; \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

install-backend: ## Install backend dependencies
	@echo "Installing backend dependencies..."
	@pip3 install -r backend/requirements.txt

# Development targets (3 Musketeers pattern)
dev: ## Start development environment (Docker-first, fallback to local)
	@echo "Starting development environment..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		echo "Using Docker Compose for development..."; \
		make docker-dev; \
	else \
		echo "Docker Compose not available, using local development..."; \
		make dev-local; \
	fi

dev-local: ## Start both frontend and backend locally
	@echo "Starting local development servers..."
	@make dev-backend-local &
	@make dev-frontend-local

dev-with-env: ## Start both frontend and backend with .env file loaded
	@echo "🚀 Starting Video Venture Launch with environment variables..."
	@if [ ! -f backend/.env ]; then \
		echo "⚠️  Creating backend/.env file..."; \
		echo "GEMINI_API_KEY=your_gemini_api_key_here" > backend/.env; \
		echo "📝 Please update backend/.env with your GEMINI_API_KEY"; \
	fi
	@echo "Loading environment variables from backend/.env..."
	@set -a && . backend/.env && set +a && \
	echo "Starting backend server with loaded environment..." && \
	cd backend && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
	@echo "Starting frontend server..."
	@if [ "$(BUN_AVAILABLE)" ]; then \
		bun run dev; \
	elif [ "$(NODE_AVAILABLE)" ]; then \
		npm run dev; \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

dev-frontend: ## Start frontend development server (Docker-first)
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		echo "Starting frontend with Docker Compose..."; \
		docker-compose up frontend; \
	else \
		echo "Docker Compose not available, starting locally..."; \
		make dev-frontend-local; \
	fi

dev-frontend-local: ## Start frontend development server locally
	@echo "Starting frontend development server locally..."
	@if [ "$(BUN_AVAILABLE)" ]; then \
		bun run dev; \
	elif [ "$(NODE_AVAILABLE)" ]; then \
		npm run dev; \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

dev-backend: ## Start backend development server (Docker-first)
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		echo "Starting backend with Docker Compose..."; \
		docker-compose up backend; \
	else \
		echo "Docker Compose not available, starting locally..."; \
		make dev-backend-local; \
	fi

dev-backend-local: ## Start backend development server locally
	@echo "🚀 Starting Video Venture Launch backend server..."
	@if [ ! -f backend/.env ]; then \
		echo "⚠️  Creating backend/.env file..."; \
		echo "GEMINI_API_KEY=your_gemini_api_key_here" > backend/.env; \
		echo "📝 Please update backend/.env with your GEMINI_API_KEY"; \
	fi
	@cd backend && python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Testing targets
test: test-frontend test-backend ## Run all tests

test-frontend: ## Run frontend tests
	@echo "Running frontend tests..."
	@if command -v bun >/dev/null 2>&1; then \
		bun test --run; \
	elif command -v npm >/dev/null 2>&1; then \
		npm test -- --run; \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

test-backend: ## Test backend ADK agent
	@echo "Testing backend ADK agent..."
	@if [ -z "$(GEMINI_API_KEY)" ]; then \
		echo "Error: GEMINI_API_KEY environment variable not set"; \
		echo "Usage: GEMINI_API_KEY=your_key make test-backend"; \
		exit 1; \
	fi
	@GEMINI_API_KEY=$(GEMINI_API_KEY) python3 -m google.adk.cli run backend.marketing_agent --query "Test campaign for a tech startup focused on AI solutions"

test-api: ## Run comprehensive API tests
	@echo "🧪 Running API Tests..."
	@echo "====================="
	@echo ""
	@echo "1. Running unit tests..."
	@make test-api-unit
	@echo ""
	@echo "2. Running integration tests..."
	@make test-api-integration
	@echo ""
	@echo "3. Running end-to-end tests..."
	@make test-api-e2e
	@echo ""
	@echo "✅ API testing complete!"

test-api-unit: ## Run API unit tests
	@echo "Running API unit tests..."
	@cd backend && python3 -m pytest tests/ -v -m "not integration and not e2e" --tb=short

test-api-integration: ## Run API integration tests
	@echo "Running API integration tests..."
	@cd backend && python3 -m pytest tests/ -v -m "integration" --tb=short

test-api-e2e: ## Run API end-to-end tests
	@echo "Running API end-to-end tests..."
	@cd backend && python3 -m pytest tests/ -v -m "e2e" --tb=short

test-api-coverage: ## Run API tests with coverage report
	@echo "Running API tests with coverage..."
	@cd backend && python3 -m pytest tests/ --cov=api --cov=agents --cov-report=term-missing --cov-report=html --cov-report=xml

test-api-regression: ## Run regression test suite
	@echo "🔄 Running Regression Tests..."
	@echo "============================="
	@echo ""
	@echo "Testing all API endpoints for regression..."
	@cd backend && python3 -m pytest tests/test_api_*.py -v --tb=short
	@echo ""
	@echo "✅ Regression testing complete!"

# Runtime and UI Testing targets
launch: ## Launch complete development environment and run health checks
	@echo "🚀 Launching Video Venture Launch development environment..."
	@echo "=========================================================="
	@make status
	@echo ""
	@echo "Starting development servers..."
	@make dev-frontend-local &
	@sleep 3
	@echo ""
	@echo "Running health checks..."
	@make health-check
	@echo ""
	@echo "✅ Launch complete! Access the application at:"
	@echo "   Frontend: http://localhost:8080"
	@echo "   Backend:  Not yet implemented (ADK agent available)"
	@echo ""
	@echo "Run 'make test-ui' to test UI pages"
	@echo "Run 'make test-api' to test API endpoints"

runtime: launch ## Alias for launch command

test-ui: ## Test all UI pages and user flows
	@echo "🧪 Testing UI Pages and User Flows..."
	@echo "====================================="
	@echo ""
	@echo "1. Running automated UI tests..."
	@make test-frontend
	@echo ""
	@echo "2. Testing UI page accessibility..."
	@make test-ui-pages
	@echo ""
	@echo "3. Testing user flows..."
	@make test-user-flows
	@echo ""
	@echo "✅ UI testing complete!"

test-ui-pages: ## Test individual UI pages are accessible
	@echo "Testing UI page accessibility..."
	@echo "Checking if development server is running..."
	@if ! curl -s http://localhost:8080 > /dev/null 2>&1; then \
		echo "❌ Development server not running. Start with 'make dev-frontend-local'"; \
		exit 1; \
	fi
	@echo "✅ Development server is running"
	@echo ""
	@echo "Testing UI pages:"
	@echo -n "  Dashboard (/).................. "
	@if curl -s http://localhost:8080/ | grep -q "<!DOCTYPE html"; then \
		echo "✅ OK"; \
	else \
		echo "❌ FAIL"; \
	fi
	@echo -n "  New Campaign (/new-campaign)... "
	@if curl -s http://localhost:8080/new-campaign | grep -q "<!DOCTYPE html"; then \
		echo "✅ OK"; \
	else \
		echo "❌ FAIL"; \
	fi
	@echo -n "  Ideation (/ideation)........... "
	@if curl -s http://localhost:8080/ideation | grep -q "<!DOCTYPE html"; then \
		echo "✅ OK"; \
	else \
		echo "❌ FAIL"; \
	fi
	@echo -n "  Proposals (/proposals)......... "
	@if curl -s http://localhost:8080/proposals | grep -q "<!DOCTYPE html"; then \
		echo "✅ OK"; \
	else \
		echo "❌ FAIL"; \
	fi

test-user-flows: ## Test critical user flows
	@echo "Testing critical user flows..."
	@echo "Running end-to-end test suite..."
	@if command -v bun >/dev/null 2>&1; then \
		bun test --run src/__tests__/HappyPath.test.tsx; \
	elif command -v npm >/dev/null 2>&1; then \
		npm test -- --run src/__tests__/HappyPath.test.tsx; \
	else \
		echo "❌ No test runner available"; \
		exit 1; \
	fi

test-api-old: ## Test API endpoints and backend services (legacy)
	@echo "🔌 Testing API Endpoints and Backend Services..."
	@echo "==============================================="
	@echo ""
	@echo "1. Testing backend ADK agent..."
	@if [ -n "$(GEMINI_API_KEY)" ]; then \
		make test-backend; \
	else \
		echo "⚠️  GEMINI_API_KEY not set - skipping ADK agent test"; \
		echo "   Set GEMINI_API_KEY to test: GEMINI_API_KEY=your_key make test-api"; \
	fi
	@echo ""
	@echo "2. Testing API status endpoints..."
	@make test-api-status
	@echo ""
	@echo "✅ API testing complete!"

test-api-status: ## Test API status and health endpoints
	@echo "Testing API status endpoints..."
	@echo "Note: Backend API server not yet implemented"
	@echo "Available tests:"
	@echo "  ✅ ADK Agent: Available (requires GEMINI_KEY)"
	@echo "  ❌ REST API: Not implemented"
	@echo "  ❌ Health endpoint: Not implemented"
	@echo "  ❌ Status endpoint: Not implemented"
	@echo ""
	@echo "Future API endpoints to implement:"
	@echo "  - GET  /api/health"
	@echo "  - GET  /api/status"
	@echo "  - POST /api/campaigns"
	@echo "  - POST /api/ideas/generate"
	@echo "  - POST /api/videos/generate"

health-check: ## Comprehensive health check of all services
	@echo "🏥 Running Health Checks..."
	@echo "=========================="
	@echo ""
	@echo "Environment Status:"
	@make status-check-quiet
	@echo ""
	@echo "Service Health:"
	@echo -n "  Frontend Server............ "
	@if curl -s http://localhost:8080 > /dev/null 2>&1; then \
		echo "✅ Running (http://localhost:8080)"; \
	else \
		echo "❌ Not running"; \
	fi
	@echo -n "  Backend API................ "
	@echo "❌ Not implemented"
	@echo -n "  ADK Agent.................. "
	@if [ "$(PYTHON_AVAILABLE)" ] && python3 -c "import google.adk" 2>/dev/null; then \
		if [ -n "$(GEMINI_API_KEY)" ]; then \
			echo "✅ Ready"; \
		else \
			echo "⚠️  Ready (GEMINI_API_KEY not set)"; \
		fi; \
	else \
		echo "❌ Not available"; \
	fi
	@echo ""
	@echo "Dependencies:"
	@echo -n "  Node.js/Bun................ "
	@if [ "$(NODE_AVAILABLE)" ] || [ "$(BUN_AVAILABLE)" ]; then \
		echo "✅ Available"; \
	else \
		echo "❌ Missing"; \
	fi
	@echo -n "  Python..................... "
	@if [ "$(PYTHON_AVAILABLE)" ]; then \
		echo "✅ Available"; \
	else \
		echo "❌ Missing"; \
	fi
	@echo -n "  Docker..................... "
	@if [ "$(DOCKER_AVAILABLE)" ]; then \
		echo "✅ Available"; \
	else \
		echo "❌ Missing"; \
	fi

status-check: health-check ## Alias for health-check

status-check-quiet: ## Quick status check without headers
	@if [ "$(NODE_AVAILABLE)" ] || [ "$(BUN_AVAILABLE)" ]; then \
		echo "  ✅ JavaScript runtime available"; \
	else \
		echo "  ❌ JavaScript runtime missing"; \
	fi
	@if [ "$(PYTHON_AVAILABLE)" ]; then \
		echo "  ✅ Python available"; \
	else \
		echo "  ❌ Python missing"; \
	fi
	@if [ "$(DOCKER_AVAILABLE)" ]; then \
		echo "  ✅ Docker available"; \
	else \
		echo "  ❌ Docker missing"; \
	fi

# Build targets
build: ## Build for production
	@echo "Building for production..."
	@if command -v bun >/dev/null 2>&1; then \
		bun run build; \
	elif command -v npm >/dev/null 2>&1; then \
		npm run build; \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

# Quality targets
lint: ## Run linting
	@echo "Running linter..."
	@if command -v bun >/dev/null 2>&1; then \
		bun run lint; \
	elif command -v npm >/dev/null 2>&1; then \
		npm run lint; \
	else \
		echo "Error: Neither bun nor npm found. Please install Node.js or Bun."; \
		exit 1; \
	fi

format: ## Format code
	@echo "Formatting code..."
	@echo "Note: Code formatting not yet configured. Add prettier/eslint configuration."

# Docker targets (3 Musketeers implementation)
docker-build: ## Build Docker containers
	@echo "Building Docker containers..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose build; \
	elif [ "$(DOCKER_AVAILABLE)" ]; then \
		echo "Building individual containers..."; \
		docker build -f Dockerfile.frontend -t video-venture-frontend .; \
		docker build -f Dockerfile.backend -t video-venture-backend ./backend; \
	else \
		echo "Error: Docker not available. Please install Docker."; \
		exit 1; \
	fi

docker-dev: ## Start development environment with Docker Compose
	@echo "Starting development environment with Docker Compose..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose up --build; \
	else \
		echo "Error: Docker Compose not available. Please install Docker Compose."; \
		exit 1; \
	fi

docker-test: ## Run tests in Docker containers
	@echo "Running tests in Docker containers..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose run --rm frontend npm test -- --run; \
		docker-compose run --rm backend python3 -m pytest; \
	else \
		echo "Error: Docker Compose not available. Please install Docker Compose."; \
		exit 1; \
	fi

docker-run: ## Run application in Docker (production mode)
	@echo "Running application in Docker (production mode)..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose -f docker-compose.prod.yml up; \
	else \
		echo "Error: Docker Compose not available. Please install Docker Compose."; \
		exit 1; \
	fi

docker-stop: ## Stop Docker containers
	@echo "Stopping Docker containers..."
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose down; \
	else \
		echo "Docker Compose not available."; \
	fi

docker-clean: ## Clean Docker containers and images
	@echo "Cleaning Docker containers and images..."
	@if [ "$(DOCKER_AVAILABLE)" ]; then \
		docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true; \
		docker system prune -f; \
	else \
		echo "Docker not available."; \
	fi

# Cleanup targets
clean: ## Clean build artifacts and dependencies
	@echo "Cleaning build artifacts..."
	@rm -rf dist/
	@rm -rf node_modules/
	@rm -rf .vite/
	@echo "Clean complete."

# Environment setup
setup-env: ## Setup development environment
	@echo "Setting up development environment..."
	@echo "1. Install Node.js or Bun for frontend development"
	@echo "2. Install Python 3.9+ for backend development"
	@echo "3. Set GEMINI_KEY environment variable for AI testing"
	@echo "4. Run 'make install' to install dependencies"

# Status check (3 Musketeers compatibility)
status: ## Check development environment status
	@echo "Development Environment Status (3 Musketeers):"
	@echo "=============================================="
	@echo -n "Docker: "
	@if [ "$(DOCKER_AVAILABLE)" ]; then \
		docker --version | head -1; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "Docker Compose: "
	@if [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		docker-compose --version | head -1; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "Node.js: "
	@if [ "$(NODE_AVAILABLE)" ]; then \
		node --version; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "Bun: "
	@if [ "$(BUN_AVAILABLE)" ]; then \
		bun --version; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "Python: "
	@if [ "$(PYTHON_AVAILABLE)" ]; then \
		python3 --version; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "Google ADK: "
	@if [ "$(PYTHON_AVAILABLE)" ] && python3 -c "import google.adk" 2>/dev/null; then \
		echo "✅ Installed"; \
	else \
		echo "❌ Not installed"; \
	fi
	@echo -n "GEMINI_KEY: "
	@if [ -n "$(GEMINI_KEY)" ]; then \
		echo "✅ Set"; \
	else \
		echo "❌ Not set"; \
	fi
	@echo ""
	@echo "3 Musketeers Readiness:"
	@if [ "$(DOCKER_AVAILABLE)" ] && [ "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		echo "✅ Ready for Docker-based development"; \
	else \
		echo "⚠️  Docker setup incomplete - will use local development"; \
	fi

doctor: ## Diagnose common development issues
	@echo "Diagnosing development environment..."
	@echo "===================================="
	@if [ ! "$(DOCKER_AVAILABLE)" ]; then \
		echo "❌ Docker not found. Install from: https://docs.docker.com/get-docker/"; \
	fi
	@if [ ! "$(DOCKER_COMPOSE_AVAILABLE)" ]; then \
		echo "❌ Docker Compose not found. Install from: https://docs.docker.com/compose/install/"; \
	fi
	@if [ ! "$(NODE_AVAILABLE)" ] && [ ! "$(BUN_AVAILABLE)" ]; then \
		echo "❌ No JavaScript runtime found. Install Node.js or Bun"; \
		echo "   Node.js: https://nodejs.org/"; \
		echo "   Bun: https://bun.sh/"; \
	fi
	@if [ ! "$(PYTHON_AVAILABLE)" ]; then \
		echo "❌ Python not found. Install Python 3.9+"; \
	fi
	@if [ "$(PYTHON_AVAILABLE)" ] && ! python3 -c "import google.adk" 2>/dev/null; then \
		echo "❌ Google ADK not installed. Run: pip install google-adk==1.2.1"; \
	fi
	@if [ -z "$(GEMINI_KEY)" ]; then \
		echo "❌ GEMINI_KEY not set. Get API key from Google AI Studio"; \
	fi
	@echo ""
	@echo "Quick fixes:"
	@echo "1. Install missing tools above"
	@echo "2. Run 'make install' to install dependencies"
	@echo "3. Set GEMINI_KEY environment variable"
	@echo "4. Run 'make dev' to start development"

# Testing
test-unit:
	@echo "Running unit tests..."
	pytest backend/tests/ -v -m "not integration and not e2e"

test-integration:
	@echo "Running integration tests..."
	pytest backend/tests/ -v -m "integration"

test-e2e:
	@echo "Running end-to-end tests..."
	pytest backend/tests/ -v -m "e2e"

test-coverage:
	@echo "Running tests with coverage..."
	pytest backend/tests/ --cov=backend --cov-report=term-missing --cov-report=html
