"""
FILENAME: marketing_orchestrator.py
DESCRIPTION/PURPOSE: Main marketing orchestrator agent implementing ADK sequential workflow
Author: JP + 2025-06-15

This module implements the root sequential agent that orchestrates the complete
marketing campaign workflow, following Google ADK samples best practices.
"""

import os
import logging
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
# from google.adk.telemetry import tracer  # Commented out due to compatibility issues
from google.adk.models import Gemini

# Import business analysis agent for direct use
from .business_analysis_agent import URLAnalysisAgent

# Configure logging
logger = logging.getLogger(__name__)

# Import visual content generation
try:
    from .visual_content_agent import generate_visual_content_for_posts
    logger.info("Visual content agent imported successfully")
except ImportError as e:
    logger.warning(f"Visual content agent not available: {e}")
    generate_visual_content_for_posts = None

# Model configuration - Using standardized environment variables
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
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

Synthesize all information to create comprehensive business context with DETAILED VISUAL CONTEXT for image generation:

1. **Unified Business Profile**:
   - Company overview and positioning
   - Core value propositions
   - Competitive advantages
   - Market presence and reputation

2. **Target Audience Analysis**:
   - Primary and secondary segments
   - Demographics and psychographics (age, lifestyle, interests)
   - Pain points and motivations
   - Communication preferences
   - Decision-making factors

3. **Brand Guidelines**:
   - Voice and tone recommendations
   - Visual style direction
   - Messaging themes and keywords
   - Content style preferences
   - Brand personality traits

4. **DETAILED VISUAL CONTEXT** (Critical for Image Generation):
   - **Product/Service Visualization**: Specific visual elements that represent the business
     * For t-shirt printing: "people wearing custom t-shirts", "design printing process", "happy customers in branded apparel"
     * For restaurants: "food presentation", "dining atmosphere", "chef preparing dishes", "satisfied customers eating"
     * For fitness: "people exercising", "trainer-client interactions", "gym equipment", "fitness transformations"
     * For tech services: "professionals using technology", "modern office environments", "digital interfaces", "team collaboration"
   
   - **Industry-Specific Visual Elements**:
     * Colors, textures, environments that represent the industry
     * Typical customer scenarios and use cases
     * Product in action or service being delivered
     * Emotional context (joy, satisfaction, success, transformation)
   
   - **Target Demographic Visuals**:
     * Age groups, lifestyle indicators, fashion/style preferences
     * Settings where target audience would be found
     * Activities and interests of target demographic
     * Social and cultural context

5. **Campaign Strategy Foundation**:
   - Key messaging pillars
   - Content themes and topics
   - Channel recommendations
   - Engagement strategies
   - Success metrics and KPIs

6. **Creative Direction for Visual Content**:
   - Specific image concepts that would resonate with target audience
   - Visual storytelling themes
   - Photography style recommendations (lifestyle, product, portrait, etc.)
   - Color palette and aesthetic direction
   - Composition and framing suggestions

Output comprehensive business context that provides SPECIFIC, ACTIONABLE visual direction for image generation agents. Focus on concrete, visual elements rather than abstract concepts.""",
        description="Synthesizes all business intelligence into comprehensive campaign context with detailed visual direction",
        output_key="business_context"
    )

# --- Content Generation Agents ---

async def create_social_content_agent() -> LlmAgent:
    """Creates a proper ADK LlmAgent for social content generation."""
    
    def generate_social_posts(
        business_context: dict,
        objective: str,
        target_audience: str,
        campaign_type: str,
        creativity_level: int,
        post_count: int
    ) -> dict:
        """Generate social media posts based on business context."""
        
        # This tool function will be called by the LlmAgent
        # The actual AI generation will be handled by the agent's instruction
        return {
            "business_context": business_context,
            "objective": objective,
            "target_audience": target_audience,
            "campaign_type": campaign_type,
            "creativity_level": creativity_level,
            "post_count": post_count,
            "tool_called": True
        }
    
    return LlmAgent(
        name="SocialContentAgent",
        model="gemini-2.5-flash",
        description="Generates engaging social media posts based on business context and campaign objectives.",
        instruction="""
        You are a social media content generation expert. Your task is to create engaging, 
        platform-optimized social media posts based on the provided business context.
        
        IMMEDIATELY call the generate_social_posts tool with the provided parameters to create 
        a comprehensive set of social media posts. Use the post_count parameter to determine 
        exactly how many posts to generate in total, divided equally across the three content types.
        
        Return your response in the following JSON format:
        
        {
            "text_url_posts": [
                {
                    "id": "post_1",
                    "content": "Engaging post content here...",
                    "hashtags": ["#relevant", "#hashtags"],
                    "platform_optimized": {
                        "twitter": {"content": "Twitter-optimized version"},
                        "linkedin": {"content": "LinkedIn-optimized version"},
                        "facebook": {"content": "Facebook-optimized version"}
                    },
                    "engagement_score": 0.85,
                    "selected": true
                }
            ],
            "text_image_posts": [
                {
                    "id": "post_2", 
                    "content": "Visual post content...",
                    "image_prompt": "Detailed image generation prompt",
                    "hashtags": ["#visual", "#content"],
                    "platform_optimized": {
                        "instagram": {"content": "Instagram-optimized version"},
                        "facebook": {"content": "Facebook-optimized version"}
                    },
                    "engagement_score": 0.90,
                    "selected": true
                }
            ],
            "text_video_posts": [
                {
                    "id": "post_3",
                    "content": "Video post content...", 
                    "video_prompt": "Detailed video generation prompt",
                    "hashtags": ["#video", "#content"],
                    "platform_optimized": {
                        "tiktok": {"content": "TikTok-optimized version"},
                        "youtube": {"content": "YouTube-optimized version"}
                    },
                    "engagement_score": 0.95,
                    "selected": true
                }
            ]
        }
        
        Generate the requested number of posts divided equally across the three content types:
        - text_url_posts: posts with text content and external links
        - text_image_posts: posts with text content and image prompts
        - text_video_posts: posts with text content and video prompts
        
        CRITICAL: Use the exact post_count parameter from the tool call. Examples:
        - If post_count=9: generate 3 posts of each type (3+3+3=9)
        - If post_count=6: generate 2 posts of each type (2+2+2=6)
        - If post_count=12: generate 4 posts of each type (4+4+4=12)
        - If post_count doesn't divide evenly by 3, distribute extras across types
        
        Ensure variety in content and high engagement potential.
        Make the content authentic to the business context and aligned with the campaign objective.
        """,
        tools=[generate_social_posts],
        output_key="social_posts"
    )

async def create_hashtag_optimization_agent() -> LlmAgent:
    """Creates a proper ADK LlmAgent for hashtag optimization."""
    
    def optimize_hashtags(
        social_posts: dict,
        business_context: dict,
        target_platforms: List[str]
    ) -> dict:
        """Optimizes hashtags for social media posts."""
        
        # This function will be called by the LlmAgent
        return {
            "social_posts": social_posts,
            "business_context": business_context,
            "target_platforms": target_platforms
        }

    return LlmAgent(
        name="HashtagOptimizationAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a hashtag optimization expert. Your task is to enhance the hashtags in social media posts
        to maximize reach, engagement, and discoverability across different platforms.
        
        When the optimize_hashtags tool is called, analyze the provided social posts and business context
        to create optimized hashtag strategies. Return the enhanced posts in the same JSON format but with
        improved hashtags:
        
        For each post, optimize hashtags by:
        1. Adding trending hashtags relevant to the business/industry
        2. Including niche-specific hashtags for targeted reach
        3. Balancing popular vs. less competitive hashtags
        4. Ensuring platform-specific hashtag strategies
        5. Maintaining relevance to the post content
        
        Platform-specific hashtag guidelines:
        - Instagram: 20-30 hashtags, mix of popular and niche
        - Twitter: 1-2 hashtags, focus on trending topics
        - LinkedIn: 3-5 professional hashtags
        - Facebook: 1-2 hashtags, focus on community building
        - TikTok: 3-5 trending hashtags
        
        Return the posts with enhanced hashtag arrays and updated platform_optimized sections.
        Ensure all hashtags are relevant, properly formatted, and likely to increase engagement.
        """,
        description="Optimizes hashtags for social media posts to maximize reach and engagement",
        output_key="optimized_posts",
        tools=[optimize_hashtags]
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
    post_count: int = 9,
    business_website: Optional[str] = None,
    about_page_url: Optional[str] = None,
    product_service_url: Optional[str] = None,
    uploaded_files: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Executes the full campaign generation workflow using real AI agents.

    This function orchestrates business analysis and content generation.
    It will first attempt to get business context from URLs if provided.
    If no URLs are available, it will use the provided business_description
    for analysis.

    This workflow no longer uses mock data for initial content generation.
    """
    logger.info("Starting real AI campaign workflow...")

    # Ensure API key is available
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured. Cannot execute real AI workflow.")
        # In a real app, you'd return a proper error response
        return {"error": "AI services are not configured."}

    # Prepare the context for the ADK workflow
    workflow_context = {
        "business_description": business_description,
        "objective": objective,
        "target_audience": target_audience,
        "campaign_type": campaign_type,
        "creativity_level": creativity_level,
        "business_website": business_website,
        "about_page_url": about_page_url,
        "product_service_url": product_service_url,
        "uploaded_files": uploaded_files,
        "post_count": post_count,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        # STEP 1: Business Analysis
        business_analysis_result = {}
        urls_to_analyze = [url for url in [business_website, about_page_url, product_service_url] if url]

        if urls_to_analyze:
            logger.info(f"Performing URL-based analysis on: {urls_to_analyze}")
            url_agent = URLAnalysisAgent()
            # Note: The URLAnalysisAgent itself now uses real AI, so we call it directly.
            analysis_data = await url_agent.analyze_urls(urls=urls_to_analyze)
            business_analysis_result = analysis_data.get("business_analysis", {})
        elif business_description:
            logger.info("Performing description-based analysis.")
            business_analysis_result = await _extract_business_context_from_description(
                business_description=business_description,
                target_audience=target_audience,
                objective=objective,
                campaign_type=campaign_type
            )
        else:
            logger.warning("No URLs or business description provided for analysis.")
            return {"error": "Business information required for analysis."}
        
        if not business_analysis_result:
            logger.error("Business analysis failed to produce results.")
            return {"error": "Could not analyze business context."}

        # STEP 2: Content Generation
        logger.info("Proceeding to real content generation.")
        # Pass the result of the analysis to the content generation step
        generation_context = workflow_context.copy()
        generation_context["business_context"] = business_analysis_result

        content_generation_agent = await create_content_generation_agent()
        
        # Correct ADK Runner pattern for executing SequentialAgent
        from google.adk.runners import InMemoryRunner
        from google.genai import types
        
        runner = InMemoryRunner(
            app_name='marketing_campaign_generator',
            agent=content_generation_agent,
        )
        
        # Create a user message with the generation context
        user_message = f"""
        Generate social media content for the following campaign:
        Business Context: {generation_context.get('business_context', {})}
        Objective: {generation_context.get('objective', 'Generate engaging content')}
        Target Audience: {generation_context.get('target_audience', 'General audience')}
        Campaign Type: {generation_context.get('campaign_type', 'general')}
        Creativity Level: {generation_context.get('creativity_level', 5)}
        Post Count: {post_count}
        
        Please generate exactly {post_count} social media posts total, divided equally across the three content types:
        - text_url_posts: {post_count // 3} posts
        - text_image_posts: {post_count // 3} posts  
        - text_video_posts: {post_count // 3} posts
        
        If the post count doesn't divide evenly by 3, distribute the extra posts among the types.
        """
        
        content = types.Content(
            role='user', 
            parts=[types.Part.from_text(text=user_message)]
        )
        
        # Create a session for the runner
        session = await runner.session_service.create_session(
            app_name='marketing_campaign_generator', 
            user_id='system'
        )
        
        # Execute the agent through the runner
        adk_results = []
        async for event in runner.run_async(
            user_id='system',
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                if event.content.parts[0].text:
                    adk_results.append(event.content.parts[0].text)
        
        # Compile the results
        adk_result = {
            "generated_content": adk_results,
            "success": True
        }

        # STEP 3: Formatting and Final Output
        generated_content = _format_generated_content(
            content_data=adk_result,
            context=workflow_context,
            business_analysis=business_analysis_result
        )
        
        # Generate campaign ID
        import uuid
        campaign_id = f"campaign_{uuid.uuid4().hex[:8]}_{int(time.time())}"
        
        final_result = {
            "campaign_id": campaign_id,
            "summary": f"AI-generated campaign for {business_analysis_result.get('company_name', 'business')}",
            "business_analysis": business_analysis_result,
            "social_posts": generated_content,  # Use social_posts key for consistency
            "generated_content": generated_content,  # Keep for backward compatibility
            "created_at": workflow_context["timestamp"],
            "status": "ready",
            "metadata": {
                "timestamp": workflow_context["timestamp"],
                "real_ai_used": True,
                "workflow_type": "URL-based" if urls_to_analyze else "Description-based"
            }
        }

        logger.info("Successfully completed real AI campaign workflow.")
        return final_result

    except Exception as e:
        logger.error(f"An error occurred during the real AI workflow: {e}", exc_info=True)
        # Proper error handling as per remediation plan
        return {"error": f"An unexpected error occurred: {e}"}

async def _execute_real_adk_workflow(orchestrator: SequentialAgent, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    DEPRECATED: This function's logic has been integrated directly into
    the main execute_campaign_workflow function for a clearer, more direct flow.
    The core logic for business analysis and content generation is now
    handled sequentially in the main function.
    """
    logger.warning("DEPRECATED: _execute_real_adk_workflow is no longer in use.")
    # The logic from this function has been moved to execute_campaign_workflow
    # for a more streamlined process.
    return {"error": "This execution path is deprecated."}

async def _generate_real_social_content(business_analysis: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate real social media content using Gemini AI."""
    
    try:
        import google.genai as genai
        
        # Initialize Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        
        company_name = business_analysis.get('company_name', 'Your Company')
        industry = business_analysis.get('industry', 'Professional Services')
        objective = context['objective']
        target_audience = context['target_audience']
        campaign_type = context['campaign_type']
        creativity_level = context['creativity_level']
        
        # Create comprehensive prompt for social content generation
        content_prompt = f"""
        As a professional marketing content creator, generate 9 high-quality social media posts for {company_name}.

        Business Context:
        - Company: {company_name}
        - Industry: {industry}
        - Objective: {objective}
        - Target Audience: {target_audience}
        - Campaign Type: {campaign_type}
        - Creativity Level: {creativity_level}/10
        - Value Propositions: {', '.join(business_analysis.get('value_propositions', []))}
        - Brand Voice: {business_analysis.get('brand_voice', 'Professional')}

        Generate 3 posts for each format:
        1. Text + URL Posts (150-200 words each)
        2. Text + Image Posts (100-150 words each)
        3. Text + Video Posts (120-180 words each)

        Requirements:
        - Professional, engaging content that reflects the brand voice
        - Include relevant hashtags (4-6 per post)
        - Optimize for LinkedIn, Instagram, and Facebook
        - Focus on the campaign objective: {objective}
        - Make content specific to {company_name} and {industry}

        Format your response as JSON:
        {{
            "text_url_posts": [
                {{"content": "post content", "hashtags": ["#tag1", "#tag2"], "platform_focus": "linkedin"}},
                {{"content": "post content", "hashtags": ["#tag1", "#tag2"], "platform_focus": "facebook"}},
                {{"content": "post content", "hashtags": ["#tag1", "#tag2"], "platform_focus": "twitter"}}
            ],
            "text_image_posts": [
                {{"content": "post content", "hashtags": ["#tag1", "#tag2"], "image_prompt": "image description"}},
                {{"content": "post content", "hashtags": ["#tag1", "#tag2"], "image_prompt": "image description"}},
                {{"content": "post content", "hashtags": ["#tag1", "#tag2"], "image_prompt": "image description"}}
            ],
            "text_video_posts": [
                {{"content": "post content", "hashtags": ["#tag1", "#tag2"], "video_prompt": "video description"}},
                {{"content": "post content", "hashtags": ["#tag1", "#tag2"], "video_prompt": "video description"}},
                {{"content": "post content", "hashtags": ["#tag1", "#tag2"], "video_prompt": "video description"}}
            ]
        }}
        """
        
        # Generate content using Gemini
        response = client.models.generate_content(
            model=model,
            contents=content_prompt
        )
        
        # Parse the response
        import json
        import re
        
        response_text = response.text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            try:
                content_data = json.loads(json_match.group())
                return _format_generated_content(content_data, context, business_analysis)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Gemini JSON response")
        
        # Fallback to enhanced content generation
        return _generate_enhanced_content_fallback(business_analysis, context)
        
    except Exception as e:
        logger.error(f"Real content generation failed: {e}")
        return _generate_enhanced_content_fallback(business_analysis, context)

def _format_generated_content(content_data: Dict[str, Any], context: Dict[str, Any], business_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Formats the structured content from the LLM into the application's data models.
    
    ADK Enhancement: This function now correctly handles ADK agent responses and JSON string parsing.
    """
    logger.debug(f"Formatting generated content with creativity level {context.get('creativity_level')}")
    logger.debug(f"Content data structure: {list(content_data.keys()) if isinstance(content_data, dict) else type(content_data)}")
    
    formatted_posts = []
    
    # Handle ADK agent response format - check for generated_content list
    if "generated_content" in content_data and isinstance(content_data["generated_content"], list):
        # Parse the JSON strings from ADK agents
        for content_str in content_data["generated_content"]:
            if isinstance(content_str, str):
                try:
                    # Parse JSON content from agent
                    import json
                    import re
                    
                    # Extract JSON from markdown code blocks if present
                    json_match = re.search(r'```json\s*(.*?)\s*```', content_str, re.DOTALL)
                    if json_match:
                        content_str = json_match.group(1)
                    
                    parsed_content = json.loads(content_str)
                    
                    # Process each post type from the parsed content
                    for post_type in ['text_url_posts', 'text_image_posts', 'text_video_posts']:
                        if post_type in parsed_content:
                            posts = parsed_content[post_type]
                            if isinstance(posts, list):
                                for post in posts:
                                    formatted_post = _format_single_post(post, post_type, business_analysis)
                                    formatted_posts.append(formatted_post)
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON content from agent: {e}")
                    continue
    
    # Fallback: check for direct social_posts format
    social_posts_data = content_data.get("social_posts", [])
    if isinstance(social_posts_data, list) and len(formatted_posts) == 0:
        for i, post_data in enumerate(social_posts_data):
            if isinstance(post_data, dict):
                formatted_post = _format_single_post(post_data, "text_url", business_analysis)
                formatted_posts.append(formatted_post)
    
    logger.info(f"Successfully formatted {len(formatted_posts)} social media posts.")
    return formatted_posts

def _format_single_post(post_data: Dict[str, Any], post_type: str, business_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Format a single post from agent response."""
    post_id = f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(str(post_data))}"
    
    # Determine post type from source
    if post_type == 'text_url_posts' or post_type == 'text_url':
        type_value = "text_url"
    elif post_type == 'text_image_posts' or post_type == 'text_image':
        type_value = "text_image"
    elif post_type == 'text_video_posts' or post_type == 'text_video':
        type_value = "text_video"
    else:
        type_value = "text_url"
    
    # Safely parse platform_optimized content
    platform_optimized_raw = post_data.get("platform_optimized", {})
    platform_optimized_data = {}
    if isinstance(platform_optimized_raw, str):
        try:
            platform_optimized_data = json.loads(platform_optimized_raw)
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode platform_optimized JSON for post {post_id}")
            platform_optimized_data = {}
    elif isinstance(platform_optimized_raw, dict):
        platform_optimized_data = platform_optimized_raw
    
    return {
        "id": post_data.get("id", post_id),
        "type": type_value,
        "content": post_data.get("content", "No content generated."),
        "url": post_data.get("url"),
        "image_prompt": post_data.get("image_prompt"),
        "image_url": None,  # Will be set when visual content is generated
        "video_prompt": post_data.get("video_prompt"),
        "video_url": None,  # Will be set when visual content is generated
        "hashtags": post_data.get("hashtags", []),
        "platform_optimized": platform_optimized_data,
        "engagement_score": post_data.get("engagement_score", 0.8),
        "selected": post_data.get("selected", False),
        "business_context": business_analysis
    }



def _generate_enhanced_content_fallback(business_analysis: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    DEPRECATED: Fallback logic is now handled by raising exceptions and
    allowing the API layer to return a proper error message.
    """
    logger.warning("DEPRECATED: _generate_enhanced_content_fallback is no longer used.")
    return []

async def _extract_business_context_from_description(
    business_description: str,
    target_audience: str,
    objective: str,
    campaign_type: str
) -> Dict[str, Any]:
    """Extract detailed business context from business description using AI analysis."""
    
    try:
        if GEMINI_API_KEY:
            import google.genai as genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            
            analysis_prompt = f"""
            Analyze this business description and extract detailed business context for marketing campaign generation:
            
            Business Description: "{business_description}"
            Target Audience: "{target_audience}"
            Campaign Objective: "{objective}"
            Campaign Type: "{campaign_type}"
            
            Extract and provide:
            1. Company name (if mentioned, otherwise "Your Company")
            2. Industry classification (be specific - e.g., "Custom T-shirt Printing", "Italian Restaurant", "Fitness Training")
            3. Key products/services offered
            4. Target demographic details (age, interests, lifestyle)
            5. Brand voice and personality
            6. Visual elements that would represent this business
            7. Competitive advantages
            8. Market positioning
            
            Format as JSON:
            {{
                "company_name": "extracted or inferred company name",
                "industry": "specific industry classification",
                "business_description": "{business_description}",
                "target_audience": "{target_audience}",
                "products_services": ["list of key offerings"],
                "brand_voice": "professional/casual/creative/etc",
                "visual_elements": ["specific visual concepts that represent this business"],
                "competitive_advantages": ["key differentiators"],
                "market_positioning": "how this business positions itself",
                "demographic_details": {{
                    "age_range": "inferred age range",
                    "interests": ["relevant interests"],
                    "lifestyle": "lifestyle characteristics"
                }}
            }}
            """
            
            response = client.models.generate_content(
                model=model,
                contents=analysis_prompt
            )
            
            # Parse JSON response
            import json
            import re
            
            response_text = response.text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    business_context = json.loads(json_match.group())
                    logger.info(f"Extracted business context for {business_context.get('company_name', 'Unknown')} in {business_context.get('industry', 'Unknown')} industry")
                    return business_context
                except json.JSONDecodeError:
                    logger.warning("Failed to parse business context JSON")
        
        # Fallback: Enhanced manual extraction
        return _manual_business_context_extraction(business_description, target_audience, objective)
        
    except Exception as e:
        logger.error(f"Business context extraction failed: {e}")
        return _manual_business_context_extraction(business_description, target_audience, objective)

def _manual_business_context_extraction(
    business_description: str,
    target_audience: str,
    objective: str
) -> Dict[str, Any]:
    """Manual business context extraction with industry-specific logic."""
    
    description_lower = business_description.lower()
    
    # Industry detection
    if any(keyword in description_lower for keyword in ['t-shirt', 'tshirt', 'apparel', 'clothing', 'print', 'custom']):
        industry = "Custom T-shirt Printing"
        visual_elements = ["people wearing custom t-shirts", "printing process", "design showcase", "happy customers in branded apparel"]
        brand_voice = "creative and fun"
    elif any(keyword in description_lower for keyword in ['restaurant', 'food', 'dining', 'kitchen', 'chef', 'cuisine']):
        industry = "Restaurant & Food Service"
        visual_elements = ["food presentation", "dining atmosphere", "chef preparing dishes", "satisfied customers eating"]
        brand_voice = "warm and inviting"
    elif any(keyword in description_lower for keyword in ['fitness', 'gym', 'training', 'workout', 'health']):
        industry = "Fitness & Health"
        visual_elements = ["people exercising", "trainer-client interactions", "gym equipment", "fitness transformations"]
        brand_voice = "motivational and energetic"
    elif any(keyword in description_lower for keyword in ['tech', 'software', 'digital', 'app', 'platform']):
        industry = "Technology Services"
        visual_elements = ["professionals using technology", "modern office environments", "digital interfaces", "team collaboration"]
        brand_voice = "innovative and professional"
    else:
        industry = "Professional Services"
        visual_elements = ["professional business environment", "team collaboration", "client satisfaction", "service delivery"]
        brand_voice = "professional and trustworthy"
    
    return {
        "company_name": "Your Company",
        "industry": industry,
        "business_description": business_description,
        "target_audience": target_audience,
        "products_services": ["Core service offering", "Customer solutions"],
        "brand_voice": brand_voice,
        "visual_elements": visual_elements,
        "competitive_advantages": ["Quality service", "Customer focus", "Innovation"],
        "market_positioning": f"Trusted {industry.lower()} provider",
        "demographic_details": {
            "age_range": "25-45",
            "interests": ["quality", "value", "service"],
            "lifestyle": "active and engaged"
        }
    } 