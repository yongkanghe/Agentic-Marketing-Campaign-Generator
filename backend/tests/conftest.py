"""Pytest configuration for Video Venture Launch tests.

Author: JP + 2024-03-13
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import AsyncMock, patch

from ..marketing_agent import MarketingCampaignContext, root_agent

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def mock_llm() -> AsyncGenerator[AsyncMock, None]:
    """Mock LLM responses for testing."""
    with patch("google.adk.agents.llm_agent.LlmAgent._call_llm") as mock:
        yield mock

@pytest.fixture
def sample_campaign_context() -> MarketingCampaignContext:
    """Create a sample campaign context for testing."""
    context = MarketingCampaignContext()
    context.business_description = "A sustainable fashion brand focused on eco-friendly materials"
    context.objective = "Increase brand awareness and drive online sales"
    context.target_audience = "Environmentally conscious millennials aged 25-35"
    return context

@pytest.fixture
async def configured_agent() -> AsyncGenerator[SequentialAgent, None]:
    """Create a configured agent instance for testing."""
    agent = await root_agent
    yield agent 