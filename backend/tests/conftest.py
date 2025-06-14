"""
FILENAME: conftest.py
DESCRIPTION/PURPOSE: Pytest configuration and fixtures for API testing
Author: JP + 2024-12-19

This module provides shared fixtures and configuration for testing the
Video Venture Launch backend API.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient

from api.main import app

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def sample_campaign_request():
    """Sample campaign request data for testing."""
    return {
        "business_description": "AI startup focused on marketing automation tools for small businesses",
        "objective": "Launch new product campaign to increase brand awareness",
        "target_audience": "Small business owners and marketing professionals",
        "campaign_type": "product",
        "creativity_level": 7,
        "business_website": "https://example.com",
        "about_page_url": "https://example.com/about",
        "product_service_url": "https://example.com/products",
        "uploaded_files": [],
        "template_data": None
    }

@pytest.fixture
def sample_url_analysis_request():
    """Sample URL analysis request data for testing."""
    return {
        "urls": ["https://example.com", "https://example.com/about"],
        "analysis_depth": "standard"
    }

@pytest.fixture
def sample_content_generation_request():
    """Sample content generation request data for testing."""
    return {
        "business_context": {
            "company_name": "Test Company",
            "industry": "Technology",
            "target_audience": "Small business owners",
            "value_propositions": ["Innovation", "Reliability"],
            "brand_voice": "Professional yet approachable",
            "competitive_advantages": ["Advanced technology", "Expert team"],
            "market_positioning": "Premium solution provider"
        },
        "campaign_objective": "Increase brand awareness",
        "creativity_level": 7,
        "post_count": 9,
        "include_hashtags": True
    }

@pytest.fixture
def sample_regeneration_request():
    """Sample post regeneration request data for testing."""
    return {
        "business_context": {
            "company_name": "Test Company",
            "industry": "Technology",
            "target_audience": "Small business owners",
            "value_propositions": ["Innovation", "Reliability"],
            "brand_voice": "Professional yet approachable",
            "competitive_advantages": ["Advanced technology", "Expert team"],
            "market_positioning": "Premium solution provider"
        },
        "post_type": "text_image",
        "current_posts": [
            {
                "id": "test_post_1",
                "type": "text_image",
                "content": "Test content",
                "hashtags": ["#test"],
                "platform_optimized": {},
                "engagement_score": 7.5,
                "selected": False
            }
        ],
        "regenerate_count": 3
    } 