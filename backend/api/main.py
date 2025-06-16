"""
FILENAME: main.py
DESCRIPTION/PURPOSE: FastAPI application entry point for AI Marketing Campaign Post Generator backend
Author: JP + 2025-06-15

This module provides the main FastAPI application with ADK agent integration,
following Google ADK samples best practices for sequential agent workflows.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import InMemoryRunner
from google.adk.telemetry import tracer

from .routes import campaigns, content, analysis
from .models import CampaignRequest, CampaignResponse, ErrorResponse
from agents.marketing_orchestrator import create_marketing_orchestrator_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instance
marketing_agent: SequentialAgent = None
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for ADK agent initialization."""
    global marketing_agent
    
    logger.info("Initializing AI Marketing Campaign Post Generator backend...")
    
    # Validate environment
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning("GEMINI_API_KEY not set - AI functionality will be limited")
    
    # Initialize the marketing orchestrator agent
    try:
        marketing_agent = await create_marketing_orchestrator_agent()
        logger.info("Marketing orchestrator agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize marketing agent: {e}")
        raise
    
    yield
    
    logger.info("Shutting down AI Marketing Campaign Post Generator backend...")

# Create FastAPI application
app = FastAPI(
    title="AI Marketing Campaign Post Generator API",
    description="Agentic AI Marketing Campaign Manager - Backend API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vite dev server
        "http://localhost:8081",  # Alternative Vite port
        "https://Agentic-Marketing-Campaign-Generator.web.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security (allow test hosts)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "testserver", "*.web.app", "*.run.app"]
)

# Include API routes
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["campaigns"])
app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])

@app.get("/", response_model=dict)
async def root():
    """Root endpoint providing API information."""
    return {
        "name": "AI Marketing Campaign Post Generator API",
        "version": "1.0.0",
        "description": "Agentic AI Marketing Campaign Manager",
        "framework": "Google ADK",
        "author": "Jaroslav Pantsjoha",
        "docs": "/api/docs",
        "health": "/health"
    }

@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "agent_initialized": marketing_agent is not None,
        "gemini_key_configured": bool(os.getenv("GEMINI_API_KEY")),
        "services": {
            "session_service": "in_memory",
            "artifact_service": "in_memory"
        }
    }

@app.get("/api/v1/agent/status", response_model=dict)
async def agent_status():
    """Get the status of the marketing orchestrator agent."""
    if not marketing_agent:
        raise HTTPException(status_code=503, detail="Marketing agent not initialized")
    
    return {
        "agent_name": marketing_agent.name,
        "agent_type": type(marketing_agent).__name__,
        "sub_agents": [agent.name for agent in marketing_agent.sub_agents],
        "description": marketing_agent.description,
        "status": "ready"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper error response format."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with proper logging."""
    from fastapi.responses import JSONResponse
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 