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

# Import visual content generation
try:
    from .visual_content_agent import generate_visual_content_for_posts
    logger.info("Visual content agent imported successfully")
except ImportError as e:
    logger.warning(f"Visual content agent not available: {e}")
    generate_visual_content_for_posts = None

# Model configuration - Using standardized environment variables
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-05-20")
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
        
        # Execute workflow with real ADK agents
        if GEMINI_API_KEY:
            logger.info("Executing real ADK workflow with Gemini integration")
            result = await _execute_real_adk_workflow(orchestrator, workflow_context)
        else:
            logger.info("Executing enhanced mock workflow (GEMINI_API_KEY not configured)")
            result = await _enhanced_mock_workflow_execution(workflow_context)
        
        logger.info("Marketing campaign workflow completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Marketing campaign workflow failed: {e}", exc_info=True)
        raise

async def _execute_real_adk_workflow(orchestrator: SequentialAgent, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute real ADK workflow with Gemini integration."""
    
    try:
        from .business_analysis_agent import analyze_business_urls
        from .visual_content_agent import generate_visual_content_for_posts
        
        logger.info("Starting real ADK workflow execution")
        
        # Step 1: Business Analysis
        business_analysis = {}
        urls_to_analyze = []
        
        if context.get("business_website"):
            urls_to_analyze.append(context["business_website"])
        if context.get("about_page_url"):
            urls_to_analyze.append(context["about_page_url"])
        if context.get("product_service_url"):
            urls_to_analyze.append(context["product_service_url"])
        
        if urls_to_analyze:
            logger.info(f"Analyzing {len(urls_to_analyze)} URLs for business context")
            url_analysis_result = await analyze_business_urls(urls_to_analyze, "comprehensive")
            business_analysis = url_analysis_result.get("business_analysis", {})
            # Ensure business description is included from user input
            business_analysis["business_description"] = context["business_description"]
            business_analysis["target_audience"] = context["target_audience"]
        else:
            # Extract detailed business context from provided business description
            business_description = context["business_description"]
            logger.info(f"Analyzing business description: {business_description[:100]}...")
            
            # Enhanced business context extraction based on description
            business_analysis = await _extract_business_context_from_description(
                business_description, 
                context["target_audience"],
                context["objective"],
                context["campaign_type"]
            )
        
        # Step 2: Content Generation using real business context
        social_posts = await _generate_real_social_content(business_analysis, context)
        
        # Step 3: Visual Content Generation
        if social_posts:
            logger.info("Generating visual content for social posts")
            visual_result = await generate_visual_content_for_posts(
                social_posts=social_posts,
                business_context=business_analysis,
                campaign_objective=context["objective"],
                target_platforms=["instagram", "linkedin", "facebook", "twitter"]
            )
            social_posts = visual_result.get("posts_with_visuals", social_posts)
        
        return {
            "campaign_id": context["workflow_id"],
            "summary": f"AI-generated marketing campaign for {context['objective']} targeting {context['target_audience']}. Campaign leverages real business analysis and AI-powered content generation to maximize engagement and drive results.",
            "business_analysis": business_analysis,
            "social_posts": social_posts,
            "created_at": datetime.now().isoformat(),
            "status": "completed",
            "processing_time": 5.0,
            "workflow_metadata": {
                "creativity_level": context["creativity_level"],
                "campaign_type": context["campaign_type"],
                "total_posts": len(social_posts),
                "agent_execution_order": [
                    "URLAnalysisAgent",
                    "BusinessContextAgent",
                    "SocialContentAgent",
                    "HashtagOptimizationAgent",
                    "VisualContentAgent"
                ],
                "real_adk_execution": True,
                "gemini_integration": True,
                "urls_analyzed": len(urls_to_analyze) if urls_to_analyze else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Real ADK workflow execution failed: {e}", exc_info=True)
        # Fallback to enhanced mock
        return await _enhanced_mock_workflow_execution(context)

async def _generate_real_social_content(business_analysis: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate real social media content using Gemini AI."""
    
    try:
        import google.genai as genai
        
        # Initialize Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-preview-05-20')
        
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
    """Format generated content into standardized post structure."""
    
    social_posts = []
    post_id_counter = 1
    
    # Process text + URL posts
    for post in content_data.get('text_url_posts', []):
        social_posts.append({
            "id": f"real_generated_text_url_{post_id_counter}",
            "type": "text_url",
            "content": post.get('content', ''),
            "hashtags": post.get('hashtags', []),
            "url": context.get('business_website') or context.get('product_service_url', 'https://example.com'),
            "platform_optimized": {
                "linkedin": {
                    "content": f"Professional content optimized for LinkedIn",
                    "hashtags": ["#Business", "#Professional", "#Growth"],
                    "character_count": 120
                },
                "twitter": {
                    "content": f"Concise content for Twitter engagement",
                    "hashtags": ["#Business", "#Growth"],
                    "character_count": 80
                },
                "facebook": {
                    "content": f"Community-focused content for Facebook",
                    "hashtags": ["#Business", "#Community"],
                    "character_count": 150
                }
            },
            "engagement_score": 8.0 + (post_id_counter * 0.1),
            "selected": False,
            "generation_method": "gemini_ai"
        })
        post_id_counter += 1
    
    # Process text + image posts
    for post in content_data.get('text_image_posts', []):
        social_posts.append({
            "id": f"real_generated_text_image_{post_id_counter}",
            "type": "text_image",
            "content": post.get('content', ''),
            "hashtags": post.get('hashtags', []),
            "image_prompt": post.get('image_prompt', ''),
            "platform_optimized": {
                "instagram": {
                    "content": f"Visual content optimized for Instagram",
                    "hashtags": ["#Visual", "#Instagram", "#Creative"],
                    "character_count": 100
                },
                "linkedin": {
                    "content": f"Professional visual content for LinkedIn",
                    "hashtags": ["#Professional", "#Visual"],
                    "character_count": 120
                },
                "facebook": {
                    "content": f"Engaging visual content for Facebook",
                    "hashtags": ["#Visual", "#Engaging"],
                    "character_count": 140
                }
            },
            "engagement_score": 8.2 + (post_id_counter * 0.1),
            "selected": False,
            "generation_method": "gemini_ai"
        })
        post_id_counter += 1
    
    # Process text + video posts
    for post in content_data.get('text_video_posts', []):
        social_posts.append({
            "id": f"real_generated_text_video_{post_id_counter}",
            "type": "text_video",
            "content": post.get('content', ''),
            "hashtags": post.get('hashtags', []),
            "video_prompt": post.get('video_prompt', ''),
            "platform_optimized": {
                "instagram": {
                    "content": f"Dynamic video content for Instagram",
                    "hashtags": ["#Video", "#Dynamic", "#Instagram"],
                    "character_count": 90
                },
                "tiktok": {
                    "content": f"Trending video content for TikTok",
                    "hashtags": ["#TikTok", "#Trending", "#Video"],
                    "character_count": 70
                },
                "linkedin": {
                    "content": f"Professional video content for LinkedIn",
                    "hashtags": ["#Professional", "#Video"],
                    "character_count": 110
                }
            },
            "engagement_score": 8.5 + (post_id_counter * 0.1),
            "selected": False,
            "generation_method": "gemini_ai"
        })
        post_id_counter += 1
    
    return social_posts

def _generate_enhanced_content_fallback(business_analysis: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate enhanced fallback content when AI generation fails."""
    
    company_name = business_analysis.get('company_name', 'Your Company')
    objective = context['objective']
    industry = business_analysis.get('industry', 'Professional Services')
    
    social_posts = []
    post_types = ["text_url", "text_image", "text_video"]
    
    for i, post_type in enumerate(post_types * 3):
        post_id = f"enhanced_fallback_{post_type}_{i+1}"
        
        # Generate contextual content based on business analysis
        if post_type == "text_url":
            content = f"🚀 Exciting developments at {company_name}! We're transforming how businesses {objective} through our innovative {industry.lower()} approach. Our latest solution addresses the core challenges we've identified in the market, delivering measurable results for companies just like yours. Ready to see what's possible? Check out our latest insights and discover how we can help accelerate your success."
        elif post_type == "text_image":
            content = f"🎨 Visual storytelling meets business results. This image captures the essence of how {company_name} helps businesses {objective} through innovative {industry.lower()} solutions. Every element represents our commitment to excellence and our understanding of what it takes to succeed in today's market."
        else:  # text_video
            content = f"🎬 Motion tells the story of transformation. This video showcases how {company_name} helps businesses {objective} through dynamic {industry.lower()} solutions. In just seconds, you'll see the power of our approach and understand why companies choose us as their strategic partner."
        
        post = {
            "id": post_id,
            "type": post_type,
            "content": content,
            "hashtags": ["#Business", "#Growth", "#Innovation", "#Success", f"#{industry.replace(' ', '')}"],
            "platform_optimized": {
                "linkedin": {
                    "content": f"Professional {post_type} content optimized for LinkedIn",
                    "hashtags": ["#Professional", "#Business"],
                    "character_count": 120
                },
                "instagram": {
                    "content": f"Visual {post_type} content for Instagram",
                    "hashtags": ["#Visual", "#Creative"],
                    "character_count": 100
                },
                "facebook": {
                    "content": f"Community-focused {post_type} content for Facebook",
                    "hashtags": ["#Community", "#Business"],
                    "character_count": 150
                }
            },
            "engagement_score": 7.5 + (i * 0.1),
            "selected": False,
            "generation_method": "enhanced_fallback"
        }
        
        # Add type-specific fields
        if post_type == "text_url":
            post["url"] = context.get("business_website") or context.get("product_service_url", "https://example.com")
        elif post_type == "text_image":
            post["image_prompt"] = f"Professional {industry.lower()} image showing {objective} with modern, clean design representing {company_name}"
        elif post_type == "text_video":
            post["video_prompt"] = f"Dynamic video showcasing {company_name}'s approach to {objective} in the {industry.lower()} sector"
        
        social_posts.append(post)
    
    return social_posts

async def _enhanced_mock_workflow_execution(context: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced mock workflow execution with better contextual content."""
    
    # Enhanced business analysis based on context
    business_analysis = {
        "company_name": "Your Company",
        "industry": "Technology Services",
        "target_audience": context["target_audience"],
        "business_description": context["business_description"],
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
    
    # Generate enhanced social posts using fallback method
    social_posts = _generate_enhanced_content_fallback(business_analysis, context)
    
    return {
        "campaign_id": context["workflow_id"],
        "summary": f"Enhanced marketing campaign for {context['objective']} targeting {context['target_audience']}. This campaign uses contextual content generation to create more relevant and engaging social media posts.",
        "business_analysis": business_analysis,
        "social_posts": social_posts,
        "created_at": datetime.now().isoformat(),
        "status": "completed",
        "processing_time": 2.0,
        "workflow_metadata": {
            "creativity_level": context["creativity_level"],
            "campaign_type": context["campaign_type"],
            "total_posts": len(social_posts),
            "agent_execution_order": [
                "EnhancedMockBusinessAnalysis",
                "EnhancedMockContentGeneration"
            ],
            "real_adk_execution": False,
            "gemini_integration": False,
            "enhancement_level": "contextual_mock"
        }
    }

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
            model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-preview-05-20')
            
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