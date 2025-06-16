"""Test suite for AI Marketing Campaign Post Generator Marketing Agent.

Author: JP + 2024-03-13
"""

import pytest
import asyncio
from typing import Dict, List
from unittest.mock import Mock, patch, AsyncMock

from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.run_config import RunConfig, StreamingMode

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from marketing_agent import (
    MarketingCampaignContext,
    create_summary_agent,
    create_idea_agent,
    create_social_agent,
    create_video_agent,
    create_root_agent,
    get_root_agent,
)

# Test Data
SAMPLE_CAMPAIGN = {
    "business_description": "A sustainable fashion brand focused on eco-friendly materials",
    "objective": "Increase brand awareness and drive online sales",
    "target_audience": "Environmentally conscious millennials aged 25-35",
}

EXPECTED_SUMMARY = """Key Business Value Propositions:
- Sustainable fashion brand
- Eco-friendly materials
- Focus on environmental consciousness

Target Audience Insights:
- Millennials (25-35)
- Environmentally conscious
- Online shoppers

Campaign Objectives:
- Increase brand awareness
- Drive online sales

Brand Voice Recommendations:
- Authentic and transparent
- Educational and informative
- Passionate about sustainability"""

EXPECTED_IDEAS = """Idea 1:
- Concept: "Eco-Chic Revolution"
- Messaging: Sustainable fashion can be stylish
- Channels: Instagram, TikTok, YouTube
- Impact: Increased brand awareness
- Implementation: Influencer partnerships

Idea 2:
- Concept: "Behind the Seams"
- Messaging: Transparency in production
- Channels: LinkedIn, Blog, YouTube
- Impact: Build trust and credibility
- Implementation: Video series"""

EXPECTED_SOCIAL = """Idea 1 Social Content:
- Main Post: "Sustainable fashion that doesn't compromise on style. Join the #EcoChicRevolution"
- Twitter: "Style meets sustainability. #EcoChicRevolution"
- LinkedIn: "How we're revolutionizing sustainable fashion"
- Instagram: "Behind the scenes of eco-friendly fashion"
- Hashtags: #SustainableFashion #EcoChic #GreenStyle
- CTA: "Shop our collection" """

EXPECTED_VIDEO = """Idea 1 Video Prompt:
- Concept: "Journey of sustainable fashion"
- Visual Style: Clean, modern, nature-inspired
- Audio: Upbeat, eco-conscious background music
- Text: "Sustainable Fashion for a Better Tomorrow"
- Format: 60-second vertical video"""

# Unit Tests
@pytest.mark.asyncio
async def test_create_summary_agent():
    """Test summary agent creation and configuration."""
    agent = await create_summary_agent()
    assert isinstance(agent, LlmAgent)
    assert agent.name == "SummaryAgent"
    assert agent.model == "gemini-2.0-pro"
    assert "business_description" in agent.instruction
    assert "objective" in agent.instruction
    assert "target_audience" in agent.instruction

@pytest.mark.asyncio
async def test_create_idea_agent():
    """Test idea generation agent creation and configuration."""
    agent = await create_idea_agent()
    assert isinstance(agent, LlmAgent)
    assert agent.name == "IdeaAgent"
    assert agent.model == "gemini-2.0-pro"
    assert "summary" in agent.instruction
    assert "Core concept" in agent.instruction

@pytest.mark.asyncio
async def test_create_social_agent():
    """Test social media content agent creation and configuration."""
    agent = await create_social_agent()
    assert isinstance(agent, LlmAgent)
    assert agent.name == "SocialPostAgent"
    assert agent.model == "gemini-2.0-pro"
    assert "ideas" in agent.instruction
    assert "platform-specific" in agent.instruction

@pytest.mark.asyncio
async def test_create_video_agent():
    """Test video content generation agent creation and configuration."""
    agent = await create_video_agent()
    assert isinstance(agent, LlmAgent)
    assert agent.name == "VideoAgent"
    assert agent.model == "gemini-2.0-pro"
    assert "campaign ideas" in agent.instruction
    assert "Veo API" in agent.instruction

@pytest.mark.asyncio
async def test_create_root_agent():
    """Test root sequential agent creation and configuration."""
    agent = await create_root_agent()
    assert isinstance(agent, SequentialAgent)
    assert agent.name == "VideoVentureLaunchAgent"
    assert len(agent.sub_agents) == 4
    assert all(isinstance(sub_agent, LlmAgent) for sub_agent in agent.sub_agents)

# Integration Tests
@pytest.mark.asyncio
async def test_agent_workflow():
    """Test the complete agent workflow with mocked responses."""
    context = MarketingCampaignContext()
    context.business_description = SAMPLE_CAMPAIGN["business_description"]
    context.objective = SAMPLE_CAMPAIGN["objective"]
    context.target_audience = SAMPLE_CAMPAIGN["target_audience"]

    # Mock the LLM responses
    with patch("google.adk.agents.llm_agent.LlmAgent._call_llm") as mock_call:
        mock_call.side_effect = [
            EXPECTED_SUMMARY,
            EXPECTED_IDEAS,
            EXPECTED_SOCIAL,
            EXPECTED_VIDEO,
        ]

        # Execute the workflow
        root_agent = await get_root_agent()
        result = await root_agent.run(context)

        # Verify the results
        assert result.summary == EXPECTED_SUMMARY
        assert result.ideas == EXPECTED_IDEAS
        assert result.social_posts == EXPECTED_SOCIAL
        assert result.video_prompts == EXPECTED_VIDEO

# Error Handling Tests
@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in the agent workflow."""
    context = MarketingCampaignContext()
    
    # Test with invalid input
    with pytest.raises(ValueError):
        context.business_description = ""  # Empty business description
        root_agent = await get_root_agent()
        await root_agent.run(context)

    # Test with API error
    with patch("google.adk.agents.llm_agent.LlmAgent._call_llm") as mock_call:
        mock_call.side_effect = Exception("API Error")
        with pytest.raises(Exception):
            root_agent = await get_root_agent()
            await root_agent.run(context)

# Performance Tests
@pytest.mark.asyncio
async def test_agent_performance():
    """Test agent performance with multiple concurrent requests."""
    async def run_agent():
        context = MarketingCampaignContext()
        context.business_description = SAMPLE_CAMPAIGN["business_description"]
        context.objective = SAMPLE_CAMPAIGN["objective"]
        context.target_audience = SAMPLE_CAMPAIGN["target_audience"]
        root_agent = await get_root_agent()
        return await root_agent.run(context)

    # Run multiple concurrent requests
    tasks = [run_agent() for _ in range(5)]
    results = await asyncio.gather(*tasks)

    # Verify all requests completed successfully
    assert len(results) == 5
    assert all(isinstance(result, MarketingCampaignContext) for result in results)

# End-to-End Tests
@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test the complete end-to-end workflow with real API calls."""
    context = MarketingCampaignContext()
    context.business_description = SAMPLE_CAMPAIGN["business_description"]
    context.objective = SAMPLE_CAMPAIGN["objective"]
    context.target_audience = SAMPLE_CAMPAIGN["target_audience"]

    # Execute the workflow with real API calls
    root_agent = await get_root_agent()
    result = await root_agent.run(context)

    # Verify the structure of the results
    assert hasattr(result, "summary")
    assert hasattr(result, "ideas")
    assert hasattr(result, "social_posts")
    assert hasattr(result, "video_prompts")

    # Verify the content quality
    assert len(result.summary) > 0
    assert len(result.ideas) > 0
    assert len(result.social_posts) > 0
    assert len(result.video_prompts) > 0

    # Verify the format of the results
    assert "Key Business Value Propositions" in result.summary
    assert "Idea" in result.ideas
    assert "Social Content" in result.social_posts
    assert "Video Prompt" in result.video_prompts 