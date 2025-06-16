"""
FILENAME: conftest.py
DESCRIPTION/PURPOSE: Pytest configuration and fixtures for API testing
Author: JP + 2025-06-15

This module provides shared fixtures and configuration for testing the
Video Venture Launch backend API.
"""

import pytest
import asyncio
import sqlite3
import tempfile
import os
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
def db_connection():
    """Create a temporary database connection for testing."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    try:
        # Initialize the database with schema by reading and executing schema.sql
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Create connection with foreign key constraints enabled
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        
        # Execute schema in chunks
        cursor = conn.cursor()
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for statement in statements:
            try:
                cursor.execute(statement)
            except sqlite3.Error as e:
                # Continue with other statements
                pass
        
        conn.commit()
        
        # Insert default campaign templates for testing
        default_templates = [
            {
                'id': 'template-brand-awareness',
                'name': 'Brand Awareness Campaign',
                'description': 'Build brand recognition and awareness',
                'category': 'brand_awareness',  # Fixed: match schema constraint
                'template_data': '{"objectives": ["increase_awareness", "build_recognition"], "content_types": ["text_image", "video"]}',
                'default_settings': '{"creativity_level": 7, "post_count": 9}',
                'prompt_templates': '{"text": "Create engaging content for brand awareness", "image": "Generate brand-focused visuals"}',
                'is_public': True  # Fixed: use is_public instead of is_active
            },
            {
                'id': 'template-product-launch',
                'name': 'Product Launch Campaign',
                'description': 'Launch new products with impact',
                'category': 'product_launch',  # Fixed: match schema constraint
                'template_data': '{"objectives": ["product_launch", "generate_interest"], "content_types": ["text_image", "video"]}',
                'default_settings': '{"creativity_level": 8, "post_count": 12}',
                'prompt_templates': '{"text": "Create compelling product launch content", "image": "Generate product-focused visuals"}',
                'is_public': True  # Fixed: use is_public instead of is_active
            },
            {
                'id': 'template-event-promotion',
                'name': 'Event Promotion Campaign',
                'description': 'Promote events and drive attendance',
                'category': 'event_promotion',  # Fixed: match schema constraint
                'template_data': '{"objectives": ["event_promotion", "drive_attendance"], "content_types": ["text_image", "video"]}',
                'default_settings': '{"creativity_level": 6, "post_count": 6}',
                'prompt_templates': '{"text": "Create exciting event promotion content", "image": "Generate event-focused visuals"}',
                'is_public': True  # Fixed: use is_public instead of is_active
            }
        ]
        
        for template in default_templates:
            cursor.execute("""
                INSERT INTO campaign_templates (
                    id, name, description, category, template_data, default_settings,
                    prompt_templates, is_public, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                template['id'], template['name'], template['description'], template['category'],
                template['template_data'], template['default_settings'], template['prompt_templates'],
                template['is_public']
            ))
        
        conn.commit()
        
        yield conn
        
    finally:
        # Clean up
        if conn:
            conn.close()
        if os.path.exists(db_path):
            os.unlink(db_path)

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