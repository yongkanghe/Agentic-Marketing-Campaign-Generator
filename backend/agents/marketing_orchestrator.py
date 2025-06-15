"""
FILENAME: marketing_orchestrator.py
DESCRIPTION/PURPOSE: Main marketing orchestrator agent implementing ADK sequential workflow
Author: JP + 2025-06-15

This module implements the root sequential agent that orchestrates the complete
marketing campaign workflow, following Google ADK samples best practices.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
# from google.adk.telemetry import tracer  # Commented out due to compatibility issues
from google.adk.models import Gemini

# Configure logging
logger = logging.getLogger(__name__)

# Model configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not configured - using mock responses")

# --- Business Analysis Agents ---

async def create_url_analysis_agent() -> LlmAgent:
    """Creates the URL analysis agent for web content extraction."""
    return LlmAgent(
        name="URLAnalysisAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are an expert web content analyzer specializing in business intelligence extraction.

Given business URLs (website, about page, product/service pages), extract comprehensive business information:

Input Context:
- Business Website: {business_website}
- About Page: {about_page_url}
- Product/Service Page: {product_service_url}

For each URL, analyze and extract:

1. **Company Overview**:
   - Company name and tagline
   - Mission, vision, and values
   - Year founded and company size
   - Geographic presence and markets served

2. **Products/Services Analysis**:
   - Core offerings and features
   - Pricing models and packages
   - Target use cases and applications
   - Competitive advantages and differentiators

3. **Target Audience Insights**:
   - Primary customer segments
   - Demographics and psychographics
   - Pain points and challenges addressed
   - Customer success stories and testimonials

4. **Brand Analysis**:
   - Brand voice and tone
   - Visual identity and design language
   - Key messaging themes
   - Content style and communication approach

5. **Market Positioning**:
   - Industry sector and niche
   - Competitive landscape
   - Unique value propositions
   - Market differentiation strategy

Output a comprehensive business analysis in JSON format with confidence scores for each insight.""",
        description="Analyzes business URLs to extract comprehensive company and market intelligence",
        output_key="url_analysis"
    )

async def create_file_analysis_agent() -> LlmAgent:
    """Creates the file analysis agent for multimodal content processing."""
    return LlmAgent(
        name="FileAnalysisAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a multimodal content analyst specializing in extracting business insights from various file types.

Input: Uploaded files including images, documents, and campaign assets

For **Images** (products, logos, marketing materials):
1. **Visual Brand Analysis**:
   - Color palette and brand colors
   - Typography and font styles
   - Logo design and brand elements
   - Visual style and aesthetic direction

2. **Product Analysis**:
   - Product features and characteristics
   - Use contexts and environments
   - Target demographic indicators
   - Quality and positioning signals

3. **Marketing Material Analysis**:
   - Design trends and preferences
   - Messaging themes and tone
   - Target audience visual cues
   - Campaign style and approach

For **Documents** (specs, brochures, presentations):
1. **Content Intelligence**:
   - Key value propositions
   - Technical specifications
   - Market positioning statements
   - Competitive advantages

2. **Audience Insights**:
   - Language complexity and tone
   - Technical depth and expertise level
   - Decision-maker targeting
   - Communication preferences

For **Campaign Assets** (previous marketing materials):
1. **Performance Indicators**:
   - Successful messaging themes
   - Effective visual elements
   - Audience engagement patterns
   - Brand consistency elements

2. **Strategic Insights**:
   - Campaign evolution and trends
   - Seasonal or temporal patterns
   - Channel-specific adaptations
   - Content performance indicators

Output comprehensive file analysis with actionable insights for campaign strategy.""",
        description="Analyzes uploaded files using multimodal AI for business and brand insights",
        output_key="file_analysis"
    )

async def create_business_context_agent() -> LlmAgent:
    """Creates the business context synthesis agent."""
    return LlmAgent(
        name="BusinessContextAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a strategic business analyst who synthesizes multiple data sources into comprehensive business context for marketing campaigns.

Input Sources:
- URL Analysis: {url_analysis}
- File Analysis: {file_analysis}
- User Input: {user_input}
- Campaign Type: {campaign_type}
- Campaign Objective: {objective}
- Target Audience: {target_audience}
- Creativity Level: {creativity_level}

Synthesize all information to create comprehensive business context:

1. **Unified Business Profile**:
   - Company overview and positioning
   - Core value propositions
   - Competitive advantages
   - Market presence and reputation

2. **Target Audience Analysis**:
   - Primary and secondary segments
   - Demographics and psychographics
   - Pain points and motivations
   - Communication preferences
   - Decision-making factors

3. **Brand Guidelines**:
   - Voice and tone recommendations
   - Visual style direction
   - Messaging themes and keywords
   - Content style preferences
   - Brand personality traits

4. **Campaign Strategy Foundation**:
   - Key messaging pillars
   - Content themes and topics
   - Channel recommendations
   - Engagement strategies
   - Success metrics and KPIs

5. **Creative Direction**:
   - Visual style recommendations
   - Content format preferences
   - Tone and personality guidelines
   - Innovation vs. consistency balance
   - Risk tolerance and boundaries

Output a comprehensive business context that serves as the foundation for all subsequent content generation and campaign activities.""",
        description="Synthesizes all business intelligence into comprehensive campaign context",
        output_key="business_context"
    )

# --- Content Generation Agents ---

async def create_social_content_agent() -> LlmAgent:
    """Creates the social media content generation agent."""
    return LlmAgent(
        name="SocialContentAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are an expert social media content creator specializing in multi-format campaign content.

Input Context:
- Business Context: {business_context}
- Campaign Objective: {objective}
- Creativity Level: {creativity_level}
- Post Count: {post_count}

Generate diverse social media content across three formats:

**1. Text + URL Posts (3 posts)**:
- Engaging copy with product/service URLs
- Clear value propositions
- Strong calls-to-action
- Link preview optimization
- Platform-specific adaptations

**2. Text + Image Posts (3 posts)**:
- Compelling visual concepts
- Detailed image generation prompts
- Text overlay recommendations
- Brand-consistent visual style
- Engagement-optimized composition

**3. Text + Video Posts (3 posts)**:
- Dynamic video concepts
- Detailed Veo generation prompts
- Storyboard descriptions
- Audio and music suggestions
- Platform format specifications

For each post, provide:
- Primary content text (optimized for engagement)
- Platform variations (LinkedIn, Twitter/X, Instagram, Facebook, TikTok)
- Hashtag recommendations (trending and niche)
- Engagement prediction score (1-10)
- Best posting time recommendations
- Call-to-action variations

Ensure content variety, brand consistency, and platform optimization while maintaining the specified creativity level.""",
        description="Generates diverse social media content across text+URL, text+image, and text+video formats",
        output_key="social_content"
    )

async def create_hashtag_optimization_agent() -> LlmAgent:
    """Creates the hashtag optimization and trend analysis agent."""
    return LlmAgent(
        name="HashtagOptimizationAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a social media hashtag strategist and trend analyst.

Input Context:
- Business Context: {business_context}
- Generated Content: {social_content}
- Campaign Objective: {objective}

Analyze and optimize hashtags for maximum reach and engagement:

1. **Hashtag Categories**:
   - Brand hashtags (company-specific)
   - Industry hashtags (sector-relevant)
   - Trending hashtags (current popularity)
   - Niche hashtags (targeted communities)
   - Location hashtags (geographic relevance)

2. **Platform Optimization**:
   - LinkedIn: Professional and industry-focused
   - Twitter/X: Trending and conversational
   - Instagram: Visual and lifestyle-oriented
   - Facebook: Community and engagement-focused
   - TikTok: Viral and entertainment-focused

3. **Hashtag Strategy**:
   - High-volume vs. niche balance
   - Competition analysis
   - Engagement potential scoring
   - Trend lifecycle assessment
   - Cross-platform adaptation

4. **Performance Optimization**:
   - Hashtag mix recommendations (3-5 per post)
   - A/B testing suggestions
   - Seasonal and temporal considerations
   - Audience behavior alignment
   - Conversion potential assessment

Output optimized hashtag strategies for each post with performance predictions and platform-specific recommendations.""",
        description="Optimizes hashtags and analyzes social media trends for maximum engagement",
        output_key="hashtag_optimization"
    )

# --- Sequential Agent Orchestration ---

async def create_business_analysis_agent() -> SequentialAgent:
    """Creates the business analysis sequential agent."""
    url_agent = await create_url_analysis_agent()
    file_agent = await create_file_analysis_agent()
    context_agent = await create_business_context_agent()
    
    return SequentialAgent(
        name="BusinessAnalysisAgent",
        sub_agents=[url_agent, file_agent, context_agent],
        description="Comprehensive business analysis and context extraction workflow"
    )

async def create_content_generation_agent() -> SequentialAgent:
    """Creates the content generation sequential agent."""
    social_agent = await create_social_content_agent()
    hashtag_agent = await create_hashtag_optimization_agent()
    
    return SequentialAgent(
        name="ContentGenerationAgent",
        sub_agents=[social_agent, hashtag_agent],
        description="Multi-format social media content generation and optimization workflow"
    )

# --- Root Marketing Orchestrator ---

async def create_marketing_orchestrator_agent() -> SequentialAgent:
    """Creates the root marketing orchestrator agent."""
    logger.info("Initializing Marketing Orchestrator Agent...")
    
    # Create sub-agents
    business_agent = await create_business_analysis_agent()
    content_agent = await create_content_generation_agent()
    
    # Create root orchestrator
    orchestrator = SequentialAgent(
        name="MarketingOrchestratorAgent",
        sub_agents=[business_agent, content_agent],
        description="Master orchestrator for complete marketing campaign workflow that coordinates business analysis and content generation"
    )
    
    logger.info(f"Marketing Orchestrator Agent initialized with {len(orchestrator.sub_agents)} sub-agents")
    return orchestrator

# --- Utility Functions ---

async def execute_campaign_workflow(
    business_description: str,
    objective: str,
    target_audience: str,
    campaign_type: str,
    creativity_level: int,
    business_website: Optional[str] = None,
    about_page_url: Optional[str] = None,
    product_service_url: Optional[str] = None,
    uploaded_files: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Execute the complete marketing campaign workflow."""
    
    logger.info("Starting marketing campaign workflow execution...")
    
    try:
        # Get the orchestrator agent
        orchestrator = await create_marketing_orchestrator_agent()
        
        # Prepare workflow context
        workflow_context = {
            "business_description": business_description,
            "objective": objective,
            "target_audience": target_audience,
            "campaign_type": campaign_type,
            "creativity_level": creativity_level,
            "business_website": business_website,
            "about_page_url": about_page_url,
            "product_service_url": product_service_url,
            "uploaded_files": uploaded_files or [],
            "post_count": 9,  # 3 per format type
            "workflow_id": f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "timestamp": datetime.now().isoformat()
        }
        
        # Execute workflow (this would integrate with ADK runners in production)
        if GEMINI_API_KEY:
            # TODO: Integrate with ADK runners for actual execution
            logger.info("Would execute ADK workflow with real Gemini integration")
            result = await _mock_workflow_execution(workflow_context)
        else:
            logger.info("Executing mock workflow (GEMINI_API_KEY not configured)")
            result = await _mock_workflow_execution(workflow_context)
        
        logger.info("Marketing campaign workflow completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Marketing campaign workflow failed: {e}", exc_info=True)
        raise

async def _mock_workflow_execution(context: Dict[str, Any]) -> Dict[str, Any]:
    """Mock workflow execution for development/testing."""
    
    # Mock business analysis
    business_analysis = {
        "company_name": "Sample Company",
        "industry": "Technology",
        "target_audience": context["target_audience"],
        "value_propositions": [
            "Innovative solutions",
            "Customer-centric approach",
            "Proven track record"
        ],
        "brand_voice": "Professional yet approachable",
        "competitive_advantages": [
            "Advanced technology",
            "Expert team",
            "Comprehensive support"
        ],
        "market_positioning": "Premium solution provider"
    }
    
    # Mock social media posts
    social_posts = []
    post_types = ["text_url", "text_image", "text_video"]
    
    for i, post_type in enumerate(post_types * 3):  # 3 of each type
        post_id = f"post_{i+1}_{post_type}"
        
        post = {
            "id": post_id,
            "type": post_type,
            "content": f"Engaging {post_type.replace('_', ' + ')} content for {context['objective']}. Discover how our innovative solutions can transform your business! #Innovation #Business #Growth",
            "hashtags": ["#Innovation", "#Business", "#Growth", "#Technology", "#Success"],
            "platform_optimized": {
                "linkedin": f"Professional {post_type} content optimized for LinkedIn",
                "twitter": f"Concise {post_type} content for Twitter engagement",
                "instagram": f"Visual {post_type} content for Instagram stories",
                "facebook": f"Community-focused {post_type} content for Facebook",
                "tiktok": f"Trending {post_type} content for TikTok discovery"
            },
            "engagement_score": 7.5 + (i * 0.1),  # Mock engagement scores
            "selected": False
        }
        
        # Add type-specific fields
        if post_type == "text_url":
            post["url"] = context.get("business_website", "https://example.com")
        elif post_type == "text_image":
            post["image_prompt"] = f"Professional business image showing {context['objective']} with modern, clean design"
        elif post_type == "text_video":
            post["video_prompt"] = f"Dynamic video showcasing {context['objective']} with engaging visuals and professional presentation"
        
        social_posts.append(post)
    
    return {
        "campaign_id": context["workflow_id"],
        "summary": f"Comprehensive marketing campaign for {context['objective']} targeting {context['target_audience']}. The campaign leverages innovative content strategies to maximize engagement and drive business results.",
        "business_analysis": business_analysis,
        "social_posts": social_posts,
        "created_at": datetime.now().isoformat(),
        "status": "completed",
        "processing_time": 2.5,  # Mock processing time
        "workflow_metadata": {
            "creativity_level": context["creativity_level"],
            "campaign_type": context["campaign_type"],
            "total_posts": len(social_posts),
            "agent_execution_order": [
                "URLAnalysisAgent",
                "FileAnalysisAgent", 
                "BusinessContextAgent",
                "SocialContentAgent",
                "HashtagOptimizationAgent"
            ]
        }
    } 