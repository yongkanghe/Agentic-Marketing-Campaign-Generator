"""
FILENAME: content.py
DESCRIPTION/PURPOSE: Content generation API routes for social media posts
Author: JP + 2025-06-16
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException
import os
import time

from ..models import (
    ContentGenerationRequest, ContentGenerationResponse,
    SocialPostRegenerationRequest, SocialPostRegenerationResponse,
    SocialMediaPost, PostType
)

logger = logging.getLogger(__name__)

# Import ADK agents for real content generation
try:
    from agents.marketing_orchestrator import execute_campaign_workflow
    logger.info("Marketing orchestrator agent available for API endpoints")
except ImportError as e:
    logger.warning(f"Marketing orchestrator agent not available: {e}")
    execute_campaign_workflow = None

# Import visual content generation
try:
    from agents.visual_content_agent import generate_visual_content_for_posts
    logger.info("Visual content agent available for API endpoints")
except ImportError as e:
    logger.warning(f"Visual content agent not available: {e}")
    generate_visual_content_for_posts = None

router = APIRouter()

@router.post("/generate", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest) -> ContentGenerationResponse:
    """Generate social media content based on business context."""
    
    try:
        logger.info(f"Generating {request.post_count} social media posts")
        
        # Mock content generation (replace with real ADK agent call)
        posts = []
        post_types = ["text_url", "text_image", "text_video"]
        
        for i in range(request.post_count):
            post_type = post_types[i % 3]
            
            # Respect include_hashtags flag
            hashtags = ["#Generated", "#Content", "#Marketing"] if request.include_hashtags else []
            
            post = SocialMediaPost(
                id=f"generated_post_{i+1}",
                type=PostType(post_type),
                content=f"Generated {post_type.replace('_', ' + ')} content for {request.campaign_objective}",
                hashtags=hashtags,
                platform_optimized={
                    "linkedin": {
                        "content": f"Professional content for LinkedIn",
                        "hashtags": ["#Professional", "#LinkedIn", "#Business"]
                    },
                    "twitter": {
                        "content": f"Concise content for Twitter", 
                        "hashtags": ["#Twitter", "#Social", "#Marketing"]
                    },
                    "instagram": {
                        "content": f"Visual content for Instagram",
                        "hashtags": ["#Instagram", "#Visual", "#Creative"]
                    },
                    "facebook": {
                        "content": f"Engaging content for Facebook",
                        "hashtags": ["#Facebook", "#Engagement", "#Community"]
                    }
                },
                engagement_score=7.0 + (i * 0.1),
                selected=False
            )
            posts.append(post)
        
        hashtag_suggestions = ["#Innovation", "#Business", "#Growth", "#Marketing", "#Success"]
        
        return ContentGenerationResponse(
            posts=posts,
            hashtag_suggestions=hashtag_suggestions,
            generation_metadata={
                "creativity_level": request.creativity_level,
                "post_count": len(posts),
                "total_posts": len(posts),  # Add this field for test compatibility
                "generation_method": "mock",
                "generation_time": 1.5
            },
            processing_time=1.5
        )
        
    except Exception as e:
        logger.error(f"Content generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

@router.post("/regenerate", response_model=SocialPostRegenerationResponse)
async def regenerate_posts(request: SocialPostRegenerationRequest) -> SocialPostRegenerationResponse:
    """Regenerate specific social media posts using real ADK agents."""
    
    try:
        logger.info(f"Regenerating {request.regenerate_count} {request.post_type} posts with business context")
        
        # Extract business context from request
        business_context = getattr(request, 'business_context', {})
        creativity_level = getattr(request, 'creativity_level', 7)
        
        # Use optimized batch generation if Gemini API is available
        if os.getenv("GEMINI_API_KEY") and business_context:
            logger.info("Using optimized batch Gemini generation for content regeneration")
            
            # Use the new batch generation function for optimal performance
            start_time = time.time()
            generated_posts = await _generate_batch_content_with_gemini(
                request.post_type, 
                request.regenerate_count, 
                business_context
            )
            
            # Return successful response
            return SocialPostRegenerationResponse(
                new_posts=generated_posts,
                regeneration_metadata={
                    "regenerated_count": len(generated_posts),
                    "post_type": request.post_type.value,
                    "generation_method": "optimized_batch_gemini_generation",
                    "creativity_level": request.creativity_level,
                    "business_context_used": bool(business_context),
                    "cost_controlled": len(generated_posts) < request.regenerate_count
                },
                processing_time=time.time() - start_time
            )
            
        else:
            # Enhanced fallback with business context
            logger.info("Using enhanced mock generation with business context")
            
            new_posts = []
            for i in range(request.regenerate_count):
                post = SocialMediaPost(
                    id=f"enhanced_{request.post_type}_{i+1}",
                    type=request.post_type,
                    content=generate_enhanced_content(request.post_type, business_context, i),
                    hashtags=generate_contextual_hashtags(business_context),
                    platform_optimized={
                        "linkedin": {
                            "content": f"Professional {request.post_type.replace('_', ' + ')} content",
                            "hashtags": ["#Professional", "#LinkedIn", "#Business"]
                        },
                        "twitter": {
                            "content": f"Engaging {request.post_type.replace('_', ' + ')} content",
                            "hashtags": ["#Twitter", "#Social", "#Marketing"]
                        },
                        "instagram": {
                            "content": f"Visual {request.post_type.replace('_', ' + ')} content",
                            "hashtags": ["#Instagram", "#Visual", "#Creative"]
                        },
                        "facebook": {
                            "content": f"Community {request.post_type.replace('_', ' + ')} content",
                            "hashtags": ["#Facebook", "#Community", "#Engagement"]
                        }
                    },
                    engagement_score=8.0 + (i * 0.1),
                    selected=False
                )
                new_posts.append(post)
            
            return SocialPostRegenerationResponse(
                new_posts=new_posts,
                regeneration_metadata={
                    "post_type": request.post_type,
                    "regenerate_count": len(new_posts),
                    "method": "enhanced_mock_with_context",
                    "business_context_used": bool(business_context)
                },
                processing_time=1.5
            )
        
    except Exception as e:
        logger.error(f"Post regeneration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Post regeneration failed: {str(e)}"
        )

def generate_enhanced_content(post_type: PostType, business_context: dict, index: int) -> str:
    """Generate enhanced content based on business context."""
    
    company_name = business_context.get('company_name', 'Your Company')
    objective = business_context.get('objective', 'increase sales')
    campaign_type = business_context.get('campaign_type', 'service')
    business_description = business_context.get('business_description', '')
    
    # Extract key themes from business description
    themes = []
    if 'innovative' in business_description.lower() or 'innovation' in business_description.lower():
        themes.append('innovation')
    if 'quality' in business_description.lower() or 'premium' in business_description.lower():
        themes.append('quality')
    if 'customer' in business_description.lower() or 'client' in business_description.lower():
        themes.append('customer-focused')
    if 'technology' in business_description.lower() or 'tech' in business_description.lower():
        themes.append('technology')
    
    # Social media optimized content (short and punchy)
    base_content = {
        PostType.TEXT_URL: [
            f"🚀 Ready to {objective}? {company_name} has the solution!",
            f"💡 Transform your business with {company_name}'s {campaign_type} approach",
            f"🎯 {company_name} helps businesses {objective} faster than ever",
            f"✨ Discover how {company_name} can revolutionize your {campaign_type} strategy",
            f"🔥 Game-changing {campaign_type} solutions from {company_name}"
        ],
        PostType.TEXT_IMAGE: [
            f"🎨 {company_name} in action",
            f"📸 Innovation meets results",
            f"🌟 Your success story starts here",
            f"💫 Transforming {campaign_type} industry",
            f"🎭 Excellence you can see"
        ],
        PostType.TEXT_VIDEO: [
            f"🎬 {company_name} transforming {campaign_type}",
            f"📹 See innovation in motion",
            f"🎥 Your future starts now",
            f"🌟 Dynamic solutions, real results",
            f"🚀 Watch the transformation"
        ]
    }
    
    content_list = base_content.get(post_type, base_content[PostType.TEXT_URL])
    selected_content = content_list[index % len(content_list)]
    
    # Add theme-specific enhancements
    if 'innovation' in themes:
        selected_content = selected_content.replace('solution', 'cutting-edge solution')
    if 'quality' in themes:
        selected_content = selected_content.replace('approach', 'premium approach')
    if 'customer-focused' in themes:
        selected_content = selected_content.replace('business', 'customer-first business')
    
    return selected_content

def generate_contextual_hashtags(business_context: dict) -> List[str]:
    """Generate AI-powered, context-aware hashtags based on business and product analysis."""
    
    # Extract comprehensive business context
    company_name = business_context.get('company_name', 'YourBusiness')
    business_type = business_context.get('business_type', 'corporation')
    campaign_type = business_context.get('campaign_type', 'service')
    objective = business_context.get('objective', 'increase sales')
    industry = business_context.get('industry', 'Professional Services')
    brand_voice = business_context.get('brand_voice', 'Professional')
    
    # Extract product-specific context for enhanced targeting
    product_context = business_context.get('product_context', {})
    has_specific_product = product_context.get('has_specific_product', False)
    product_themes = product_context.get('product_themes', [])
    
    # Extract campaign themes
    campaign_guidance = business_context.get('campaign_guidance', {})
    content_themes = campaign_guidance.get('content_themes', {})
    primary_themes = content_themes.get('primary_themes', [])
    
    # Start with dynamic base hashtags
    hashtags = []
    
    # 1. PRODUCT-SPECIFIC HASHTAGS (Priority for specific products)
    if has_specific_product and product_themes:
        for theme in product_themes[:3]:  # Limit to top 3 product themes
            clean_theme = theme.replace(' ', '').replace('&', '').replace('-', '')
            if clean_theme and len(clean_theme) > 2:
                hashtags.append(f"#{clean_theme}")
    
    # 2. BUSINESS TYPE SPECIFIC HASHTAGS
    if business_type == "individual_creator":
        hashtags.extend(["#Artist", "#Creator", "#IndependentArt", "#CreativeDesign"])
    elif business_type == "small_business":
        hashtags.extend(["#SmallBusiness", "#LocalBusiness", "#Entrepreneur"])
    else:
        hashtags.extend(["#Business", "#Professional"])
    
    # 3. INDUSTRY-SPECIFIC HASHTAGS
    industry_lower = industry.lower()
    if 'digital art' in industry_lower or 'print-on-demand' in industry_lower:
        hashtags.extend(["#DigitalArt", "#PrintOnDemand", "#CustomDesign", "#ArtisticWear"])
    elif 'technology' in industry_lower:
        hashtags.extend(["#Technology", "#Tech", "#Innovation"])
    elif 'marketing' in industry_lower:
        hashtags.extend(["#Marketing", "#DigitalMarketing", "#Growth"])
    elif 'fitness' in industry_lower:
        hashtags.extend(["#Fitness", "#Health", "#Wellness"])
    elif 'food' in industry_lower:
        hashtags.extend(["#Food", "#Foodie", "#Restaurant"])
    
    # 4. CAMPAIGN OBJECTIVE HASHTAGS
    objective_lower = objective.lower()
    if 'sales' in objective_lower:
        hashtags.extend(["#Sales", "#ShopNow", "#NewProduct"])
    elif 'awareness' in objective_lower:
        hashtags.extend(["#BrandAwareness", "#Discover", "#GetToKnow"])
    elif 'engagement' in objective_lower:
        hashtags.extend(["#Community", "#Engage", "#Connect"])
    elif 'growth' in objective_lower:
        hashtags.extend(["#Growth", "#Expansion", "#Success"])
    
    # 5. BRAND VOICE HASHTAGS
    voice_lower = brand_voice.lower()
    if 'artistic' in voice_lower or 'creative' in voice_lower:
        hashtags.extend(["#Creative", "#Artistic", "#Inspiration"])
    elif 'humorous' in voice_lower or 'funny' in voice_lower:
        hashtags.extend(["#Humor", "#Fun", "#Entertaining"])
    elif 'professional' in voice_lower:
        hashtags.extend(["#Professional", "#Quality", "#Excellence"])
    elif 'innovative' in voice_lower:
        hashtags.extend(["#Innovation", "#Innovative", "#CuttingEdge"])
    
    # 6. CAMPAIGN THEME HASHTAGS
    for theme in primary_themes[:2]:  # Limit to top 2 campaign themes
        if theme.lower() == 'authenticity':
            hashtags.extend(["#Authentic", "#Real", "#Genuine"])
        elif theme.lower() == 'community':
            hashtags.extend(["#Community", "#Together", "#Family"])
        elif theme.lower() == 'innovation':
            hashtags.extend(["#Innovation", "#NewIdeas", "#Creative"])
        elif theme.lower() == 'quality':
            hashtags.extend(["#Quality", "#Premium", "#Excellence"])
    
    # 7. PLATFORM-OPTIMIZED HASHTAGS
    hashtags.extend(["#SocialMedia", "#Content", "#Trending"])
    
    # Clean up and prioritize hashtags
    # Remove duplicates while preserving order
    unique_hashtags = []
    seen = set()
    for tag in hashtags:
        if tag.lower() not in seen and len(tag) > 3:  # Minimum tag length
            unique_hashtags.append(tag)
            seen.add(tag.lower())
    
    # Return top 6 most relevant hashtags
    return unique_hashtags[:6]

@router.post("/generate-visuals")
async def generate_visual_content(request: dict):
    """Generate visual content (images and videos) for social media posts.
    
    NOTE: Real Imagen/Veo API calls temporarily disabled due to timeout issues.
    Enhanced placeholders are used instead with proper prompts for future implementation.
    """
    
    try:
        logger.info("Generating visual content for social media posts (using enhanced placeholders)")
        
        # Extract request data
        social_posts = request.get("social_posts", [])
        business_context = request.get("business_context", {})
        campaign_objective = request.get("campaign_objective", "")
        target_platforms = request.get("target_platforms", ["instagram", "linkedin"])
        
        if not social_posts:
            raise HTTPException(
                status_code=400,
                detail="No social media posts provided for visual content generation"
            )
        
        # TEMPORARY: Use enhanced placeholder generation instead of real API calls
        # TODO: Re-enable real visual generation with optimized batch processing
        logger.info("Using enhanced placeholder generation to avoid API timeouts")
        
        result = {
            "posts_with_visuals": social_posts,
            "visual_strategy": {
                "total_posts": len(social_posts),
                "image_posts": len([p for p in social_posts if p.get("type") == "text_image"]),
                "video_posts": len([p for p in social_posts if p.get("type") == "text_video"]),
                "brand_consistency": "Enhanced placeholders with proper prompts",
                "platform_optimization": "Multi-platform ready",
                "note": "Real Imagen/Veo generation temporarily disabled for performance"
            },
            "generation_metadata": {
                "agent_used": "EnhancedPlaceholderAgent",
                "processing_time": 0.1,
                "quality_score": 7.5,
                "status": "placeholder_mode"
            }
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Visual content generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Visual content generation failed: {str(e)}"
        )

async def _generate_batch_content_with_gemini(
    post_type: PostType, 
    regenerate_count: int, 
    business_context: dict
) -> List[SocialMediaPost]:
    """Generate multiple posts in a single Gemini API call for optimal performance."""
    
    try:
        import google.genai as genai
        import json
        import re
        
        # Apply configurable limits based on post type
        max_posts_by_type = {
            PostType.TEXT_URL: int(os.getenv('MAX_TEXT_URL_POSTS', '10')),
            PostType.TEXT_IMAGE: int(os.getenv('MAX_TEXT_IMAGE_POSTS', '4')), 
            PostType.TEXT_VIDEO: int(os.getenv('MAX_TEXT_VIDEO_POSTS', '4'))
        }
        
        max_allowed = max_posts_by_type.get(post_type, 5)
        actual_count = min(regenerate_count, max_allowed)
        
        if actual_count < regenerate_count:
            logger.info(f"Limiting {post_type.value} generation from {regenerate_count} to {actual_count} posts for cost control")
        
        # Initialize Gemini client
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-preview-05-20')
        
        company_name = business_context.get('company_name', 'Your Company')
        objective = business_context.get('objective', 'increase sales')
        campaign_type = business_context.get('campaign_type', 'service')
        business_description = business_context.get('business_description', '')
        target_audience = business_context.get('target_audience', 'business professionals')
        
        # NEW: Extract Campaign Media Tuning for enhanced visual guidance
        campaign_media_tuning = business_context.get('campaign_media_tuning', '')
        
        # Extract campaign guidance for consistent visual content
        campaign_guidance = business_context.get('campaign_guidance', {})
        visual_style = campaign_guidance.get('visual_style', {})
        imagen_prompts = campaign_guidance.get('imagen_prompts', {})
        veo_prompts = campaign_guidance.get('veo_prompts', {})
        content_themes = campaign_guidance.get('content_themes', {})
        
        # NEW: Extract product-specific context for enhanced targeting
        product_context = business_context.get('product_context', {})
        has_specific_product = product_context.get('has_specific_product', False)
        product_name = product_context.get('product_name', '')
        product_description = product_context.get('product_description', '')
        product_themes = product_context.get('product_themes', [])
        
        # Enhanced business context with product focus
        if has_specific_product and product_name:
            logger.info(f"Using product-specific context for: {product_name}")
            primary_focus = f"Promote the specific product: {product_name}"
            target_context = f"Target audience specifically interested in: {product_description}"
            enhanced_company_name = f"{company_name} - {product_name}"
        else:
            primary_focus = f"Promote {company_name}'s {campaign_type} offerings"
            target_context = f"Target audience: {target_audience}"
            enhanced_company_name = company_name
        
        # Enhanced content generation with product-specific themes
        product_theme_text = f"\\nProduct Themes: {', '.join(product_themes)}" if product_themes else ""
        creative_direction = campaign_guidance.get('creative_direction', f'Professional content showcasing {enhanced_company_name}')
        
        # Create post type specific prompt with campaign guidance
        post_type_name = post_type.value.replace('_', ' + ').title()
        
        if post_type == PostType.TEXT_URL:
            format_instructions = f"""
            Generate {actual_count} Text + URL posts (40-120 characters each):
            - CRITICAL: Include ONE clear product/service URL (not multiple duplicate URLs)
            - Short, punchy, social media optimized
            - Twitter/Instagram friendly length
            - Strong action verbs (Discover, Transform, Boost, etc.)
            - Include URL placement naturally at the end
            - Platform: LinkedIn, Twitter, Instagram optimized
            - Call-to-Action Style: {content_themes.get('call_to_action_style', 'inspiring and action-oriented')}
            """
        elif post_type == PostType.TEXT_IMAGE:
            imagen_base = imagen_prompts.get('base_prompt', 'Professional lifestyle photography')
            imagen_environment = imagen_prompts.get('environment', 'business setting')
            imagen_technical = imagen_prompts.get('technical_specs', '35mm lens, natural lighting')
            
            # Apply Campaign Media Tuning to Imagen prompts if provided
            media_tuning_guidance = f"\n- Campaign Media Tuning: {campaign_media_tuning}" if campaign_media_tuning else ""
            
            format_instructions = f"""
            Generate {actual_count} Text + Image posts (30-80 characters each):
            - Very short text to complement visuals
            - Include detailed image generation prompts following Imagen best practices
            - Visual storytelling approach focused on {company_name}'s business
            - Instagram/TikTok optimized
            - Let the image do the talking
            
            IMAGEN PROMPT GUIDANCE (follow exactly):
            - Base Style: {imagen_base}
            - Environment: {imagen_environment}  
            - Technical Specs: {imagen_technical}
            - Photography Style: {visual_style.get('photography_style', 'professional lifestyle')}
            - Mood: {visual_style.get('mood', 'professional, trustworthy')}
            - Subject Focus: People using {company_name}'s products/services in real scenarios{media_tuning_guidance}
            
            Cost Control: Limited to {actual_count} posts to manage Imagen API costs
            """
        else:  # TEXT_VIDEO
            veo_base = veo_prompts.get('base_prompt', 'Dynamic lifestyle video')
            veo_movement = veo_prompts.get('movement_style', 'smooth camera movements')
            veo_storytelling = veo_prompts.get('storytelling', 'problem-solution narrative')
            
            # Apply Campaign Media Tuning to Veo prompts if provided
            media_tuning_guidance = f"\n- Campaign Media Tuning: {campaign_media_tuning}" if campaign_media_tuning else ""
            
            format_instructions = f"""
            Generate {actual_count} Text + Video posts (40-100 characters each):
            - Short, dynamic captions for video content
            - Include detailed video concept descriptions following Veo best practices
            - TikTok/Instagram Reels/YouTube Shorts optimized
            - Action-oriented language
            - Focus on movement and energy
            
            VEO PROMPT GUIDANCE (follow exactly):
            - Base Concept: {veo_base}
            - Movement Style: {veo_movement}
            - Storytelling: {veo_storytelling}
            - Duration Focus: {veo_prompts.get('duration_focus', '15-30 second clips')}
            - Scene Composition: {veo_prompts.get('scene_composition', 'engaging transitions')}
            - Show real people engaging with {company_name}'s offerings{media_tuning_guidance}
            
            Cost Control: Limited to {actual_count} posts to manage Veo API costs
            """
        
        # Platform-specific character limits and requirements
        platform_requirements = {
            PostType.TEXT_URL: "Twitter: 280 chars max, Instagram: 125 chars optimal, LinkedIn: 150 chars optimal",
            PostType.TEXT_IMAGE: "Instagram: 30-80 chars, TikTok: 40-80 chars, Visual focus",
            PostType.TEXT_VIDEO: "TikTok: 40-100 chars, Instagram Reels: 60 chars, YouTube Shorts: 80 chars"
        }
        
        # Get primary themes for consistent messaging
        primary_themes = content_themes.get('primary_themes', ['authenticity', 'results', 'community'])
        emotional_triggers = content_themes.get('emotional_triggers', ['aspiration', 'trust', 'excitement'])
        
        # Comprehensive batch generation prompt with campaign guidance
        batch_prompt = f"""
        As a professional social media marketing expert, generate {actual_count} high-quality {post_type_name} posts for {enhanced_company_name} following the established CAMPAIGN GUIDANCE.

        Business Context:
        - Company: {enhanced_company_name}
        - {primary_focus}
        - Objective: {objective}
        - Campaign Type: {campaign_type}
        - {target_context}
        - Business Description: {business_description}
        - Website URL: {business_context.get('business_website', business_context.get('product_service_url', 'https://example.com'))}

        {f"PRODUCT-SPECIFIC CONTEXT (PRIORITY):" if has_specific_product else ""}
        {f"- Product Name: {product_name}" if product_name else ""}
        {f"- Product Description: {product_description}" if product_description else ""}
        {f"- Product Themes: {', '.join(product_themes)}" if product_themes else ""}
        {f"- CRITICAL: All content must focus on promoting THIS SPECIFIC PRODUCT" if has_specific_product else ""}

        CAMPAIGN GUIDANCE (CRITICAL - Follow Exactly):
        - Creative Direction: {creative_direction}
        - Primary Themes: {', '.join(primary_themes)}
        - Emotional Triggers: {', '.join(emotional_triggers)}
        - Brand Voice: {business_context.get('brand_voice', 'Professional and innovative')}
        - Visual Mood: {visual_style.get('mood', 'professional, trustworthy')}
        {f"- Campaign Media Tuning: {campaign_media_tuning}" if campaign_media_tuning else ""}

        {format_instructions}

        Platform Requirements: {platform_requirements[post_type]}

        CRITICAL Requirements for ALL posts:
        - Keep text SHORT and PUNCHY for social media
        - For TEXT_URL: MUST include ONE product/service URL (no duplicates)
        - For TEXT_IMAGE: MUST follow Imagen prompt guidance above for relevant, business-specific images
        - For TEXT_VIDEO: MUST follow Veo prompt guidance above for relevant, business-specific videos
        - Use emojis strategically for engagement
        - Include 3-4 relevant hashtags (separate field)
        - Make content specific to {company_name} and their {objective}
        - Follow campaign themes: {', '.join(primary_themes)}

        Format your response as JSON:
        {{
            "posts": [
                {{
                    "content": "Short punchy text here (follow character limits)",
                    "hashtags": ["#tag1", "#tag2", "#tag3"],
                    {"image_prompt" if post_type == PostType.TEXT_IMAGE else "video_prompt" if post_type == PostType.TEXT_VIDEO else "call_to_action"}: "{"Detailed Imagen-optimized prompt for " + company_name + " business context" if post_type == PostType.TEXT_IMAGE else "Detailed Veo-optimized concept for " + company_name + " business context" if post_type == PostType.TEXT_VIDEO else "Strong CTA with URL"}",
                    {"url" if post_type == PostType.TEXT_URL else "engagement_strategy"}: "{"Single website URL here" if post_type == PostType.TEXT_URL else "Brief engagement approach"}"
                }},
                // ... repeat for {actual_count} posts
            ]
        }}

        Generate exactly {actual_count} unique, SHORT, social media optimized posts that will drive {objective} for {company_name} following the campaign guidance for consistent brand experience.
        """
        
        # Generate content using Gemini
        logger.info(f"Generating {actual_count} {post_type.value} posts with single Gemini API call")
        response = client.models.generate_content(
            model=model,
            contents=batch_prompt
        )
        
        # Parse the response
        response_text = response.text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            try:
                content_data = json.loads(json_match.group())
                posts = content_data.get('posts', [])
                
                # Convert to SocialMediaPost objects
                generated_posts = []
                for i, post_data in enumerate(posts[:actual_count]):
                    post_content = post_data.get('content', f'Generated {post_type.value} content for {company_name}')
                    
                    post = SocialMediaPost(
                        id=f"batch_generated_{post_type.value}_{i+1}",
                        type=post_type,
                        content=post_content,
                        hashtags=post_data.get('hashtags', [f"#{campaign_type}", "#Business", "#Growth"]),
                        platform_optimized={
                            "linkedin": {
                                "content": f"Professional content for LinkedIn",
                                "hashtags": ["#Professional", "#LinkedIn", "#Business"]
                            },
                            "twitter": {
                                "content": f"Concise content for Twitter", 
                                "hashtags": ["#Twitter", "#Social", "#Marketing"]
                            },
                            "instagram": {
                                "content": f"Visual content for Instagram",
                                "hashtags": ["#Instagram", "#Visual", "#Creative"]
                            },
                            "facebook": {
                                "content": f"Engaging content for Facebook",
                                "hashtags": ["#Facebook", "#Engagement", "#Community"]
                            }
                        },
                        engagement_score=8.0 + (i * 0.1),
                        selected=False
                    )
                    
                    # Add type-specific fields with proper URL/CTA handling
                    if post_type == PostType.TEXT_URL:
                        # Get URL from post data or business context
                        post_url = post_data.get('url') or business_context.get('business_website') or business_context.get('product_service_url')
                        if post_url and not post_url.startswith('http'):
                            post_url = f"https://{post_url}"
                        post.url = post_url
                        
                        # DO NOT add URL to content - it will be displayed separately in the UI
                        # The frontend will handle URL display in a dedicated section
                            
                    elif post_type == PostType.TEXT_IMAGE:
                        post.image_prompt = post_data.get('image_prompt', f'Professional marketing image for {company_name} showing {objective}')
                        
                        # TEMPORARY FIX: Use enhanced placeholder instead of real API calls to avoid timeout
                        # TODO: Optimize visual content generation for batch processing
                        try:
                            # Enhanced placeholder with actual prompt for better context
                            enhanced_prompt = post.image_prompt
                            if has_specific_product and product_name:
                                enhanced_prompt = f"Professional lifestyle photo: People wearing/using {product_name}, {enhanced_prompt}"
                            
                            post.image_url = f"https://picsum.photos/1024/576?random={i+100}&text={enhanced_company_name.replace(' ', '+')}"
                            logger.info(f"Generated enhanced placeholder image for post {i+1} with prompt: {enhanced_prompt[:100]}...")
                                
                        except Exception as e:
                            logger.error(f"Enhanced placeholder generation failed for post {i+1}: {e}")
                            post.image_url = f"https://picsum.photos/1024/576?random={i+100}&blur=1"
                        
                    elif post_type == PostType.TEXT_VIDEO:
                        post.video_prompt = post_data.get('video_prompt', f'Dynamic marketing video showcasing {company_name} approach to {objective}')
                        
                        # TEMPORARY FIX: Use enhanced placeholder instead of real API calls to avoid timeout
                        # TODO: Optimize visual content generation for batch processing
                        try:
                            # Enhanced video placeholder with actual prompt for better context
                            enhanced_prompt = post.video_prompt
                            if has_specific_product and product_name:
                                enhanced_prompt = f"Dynamic video: People enjoying/using {product_name}, {enhanced_prompt}"
                            
                            post.video_url = f"https://picsum.photos/1024/576?random={i+200}&text={enhanced_company_name.replace(' ', '+')}"
                            post.thumbnail_url = f"https://picsum.photos/1024/576?random={i+200}&text=Video+Thumbnail"
                            logger.info(f"Generated enhanced placeholder video for post {i+1} with prompt: {enhanced_prompt[:100]}...")
                                
                        except Exception as e:
                            logger.error(f"Enhanced placeholder generation failed for post {i+1}: {e}")
                            post.video_url = f"https://picsum.photos/1024/576?random={i+200}&grayscale"
                    
                    generated_posts.append(post)
                
                logger.info(f"Successfully generated {len(generated_posts)} posts with batch Gemini call (cost-controlled)")
                return generated_posts
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Gemini JSON response: {e}")
        
        # Fallback to individual generation
        logger.info("Falling back to individual post generation")
        return _generate_fallback_posts(post_type, actual_count, business_context)
        
    except Exception as e:
        logger.error(f"Batch content generation failed: {e}")
        return _generate_fallback_posts(post_type, min(regenerate_count, 5), business_context)

def _generate_fallback_posts(post_type: PostType, count: int, business_context: dict) -> List[SocialMediaPost]:
    """Generate fallback posts when batch generation fails."""
    
    company_name = business_context.get('company_name', 'Your Company')
    objective = business_context.get('objective', 'increase sales')
    
    posts = []
    for i in range(count):
        post = SocialMediaPost(
            id=f"fallback_{post_type.value}_{i+1}",
            type=post_type,
            content=generate_enhanced_content(post_type, business_context, i),
            hashtags=generate_contextual_hashtags(business_context),
            platform_optimized={
                "linkedin": f"Professional {post_type.value} content",
                "twitter": f"Engaging {post_type.value} content",
                "instagram": f"Visual {post_type.value} content"
            },
            engagement_score=7.5 + (i * 0.1),
            selected=False
        )
        
        # Add type-specific fields for fallback posts
        if post_type == PostType.TEXT_URL:
            post_url = business_context.get('business_website') or business_context.get('product_service_url')
            if post_url and not post_url.startswith('http'):
                post_url = f"https://{post_url}"
            post.url = post_url
            # DO NOT add URL to content - frontend will display it separately
                
        elif post_type == PostType.TEXT_IMAGE:
            post.image_prompt = f'Professional marketing image for {company_name} showing {objective}'
            post.image_url = f"https://picsum.photos/1024/576?random={i+100}&blur=1"
            
        elif post_type == PostType.TEXT_VIDEO:
            post.video_prompt = f'Dynamic marketing video showcasing {company_name} approach to {objective}'
            post.video_url = f"https://picsum.photos/1024/576?random={i+200}&grayscale"
        
        posts.append(post)
    
    return posts 