"""
FILENAME: agent.py
DESCRIPTION/PURPOSE: ADK-compliant root agent for AI Marketing Campaign Post Generator
Author: JP + 2025-06-25

This module provides the root_agent following Google ADK samples best practices.
ADK CLI and web tools expect to find 'root_agent' in this module.
"""

import os
import logging
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.models import Gemini

from .marketing_orchestrator import create_marketing_orchestrator_agent

logger = logging.getLogger(__name__)

# Model configuration - Using standardized environment variables
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def create_root_agent() -> SequentialAgent:
    """Creates the root agent following ADK best practices."""
    return await create_marketing_orchestrator_agent()

# ADK CLI expects 'root_agent' to be available at module level
# For async initialization, we'll use a factory pattern
def get_root_agent() -> SequentialAgent:
    """
    Get the root agent for ADK CLI compatibility.
    Note: This is a synchronous wrapper for async agent creation.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we need to handle this differently
            logger.warning("Cannot create async agent in running event loop - using factory")
            # Return a placeholder that will be properly initialized by the FastAPI app
            return SequentialAgent(
                name="MarketingOrchestratorAgent",
                sub_agents=[],
                description="Marketing Campaign Post Generator - ADK Root Agent"
            )
        else:
            return loop.run_until_complete(create_root_agent())
    except RuntimeError:
        # No event loop running, create one
        return asyncio.run(create_root_agent())

# ADK CLI compatibility - root_agent must be available at module level
root_agent = get_root_agent() 