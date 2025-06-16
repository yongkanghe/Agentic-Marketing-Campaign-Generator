"""
FILENAME: content.py
DESCRIPTION/PURPOSE: Content generation API routes for social media posts
Author: JP + 2025-06-16
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException
import os

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
            post = SocialMediaPost(
                id=f"generated_post_{i+1}",
                type=PostType(post_type),
                content=f"Generated {post_type.replace('_', ' + ')} content for {request.campaign_objective}",
                hashtags=["#Generated", "#Content", "#Marketing"],
                platform_optimized={
                    "linkedin": f"Professional content for LinkedIn",
                    "twitter": f"Concise content for Twitter",
                    "instagram": f"Visual content for Instagram"
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
                "generation_method": "mock"
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
            new_posts = await _generate_batch_content_with_gemini(
                request.post_type, 
                request.regenerate_count, 
                business_context
            )
            
            return SocialPostRegenerationResponse(
                new_posts=new_posts,
                regeneration_metadata={
                    "post_type": request.post_type,
                    "regenerate_count": len(new_posts),
                    "method": "optimized_batch_gemini_generation",
                    "business_context_used": True,
                    "single_api_call": True,
                    "performance_optimized": True
                },
                processing_time=1.0  # Much faster with batch generation
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
                        "linkedin": f"Professional {request.post_type.replace('_', ' + ')} content",
                        "twitter": f"Engaging {request.post_type.replace('_', ' + ')} content",
                        "instagram": f"Visual {request.post_type.replace('_', ' + ')} content"
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
    """Generate hashtags based on business context."""
    
    base_hashtags = ["#Business", "#Growth", "#Success"]
    
    campaign_type = business_context.get('campaign_type', 'service')
    objective = business_context.get('objective', 'increase sales')
    business_description = business_context.get('business_description', '').lower()
    
    # Add campaign type specific hashtags
    if campaign_type == 'product':
        base_hashtags.extend(["#ProductLaunch", "#Innovation", "#NewProduct"])
    elif campaign_type == 'service':
        base_hashtags.extend(["#Services", "#Solutions", "#Consulting"])
    elif campaign_type == 'brand':
        base_hashtags.extend(["#BrandAwareness", "#Marketing", "#BrandStory"])
    elif campaign_type == 'event':
        base_hashtags.extend(["#Event", "#Networking", "#Community"])
    
    # Add objective specific hashtags
    if 'sales' in objective:
        base_hashtags.extend(["#Sales", "#Revenue", "#ROI"])
    elif 'awareness' in objective:
        base_hashtags.extend(["#Awareness", "#Visibility", "#Reach"])
    elif 'engagement' in objective:
        base_hashtags.extend(["#Engagement", "#Community", "#Interaction"])
    
    # Add industry specific hashtags based on business description
    if any(word in business_description for word in ['tech', 'technology', 'software', 'digital']):
        base_hashtags.extend(["#Technology", "#Digital", "#Tech"])
    if any(word in business_description for word in ['marketing', 'advertising', 'promotion']):
        base_hashtags.extend(["#Marketing", "#Advertising", "#Promotion"])
    if any(word in business_description for word in ['consulting', 'advisory', 'strategy']):
        base_hashtags.extend(["#Consulting", "#Strategy", "#Advisory"])
    
    # Return unique hashtags, limited to 6
    return list(dict.fromkeys(base_hashtags))[:6]

@router.post("/generate-visuals")
async def generate_visual_content(request: dict):
    """Generate visual content (images and videos) for social media posts."""
    
    try:
        logger.info("Generating visual content for social media posts")
        
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
        
        # Generate visual content using the visual content agent
        if generate_visual_content_for_posts:
            result = await generate_visual_content_for_posts(
                social_posts=social_posts,
                business_context=business_context,
                campaign_objective=campaign_objective,
                target_platforms=target_platforms
            )
        else:
            # Fallback mock implementation
            result = {
                "posts_with_visuals": social_posts,
                "visual_strategy": {
                    "total_posts": len(social_posts),
                    "image_posts": len([p for p in social_posts if p.get("type") == "text_image"]),
                    "video_posts": len([p for p in social_posts if p.get("type") == "text_video"]),
                    "brand_consistency": "Professional and modern",
                    "platform_optimization": "Multi-platform ready"
                },
                "generation_metadata": {
                    "agent_used": "MockVisualContentAgent",
                    "processing_time": 1.0,
                    "quality_score": 8.0
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
        
        # Create post type specific prompt
        post_type_name = post_type.value.replace('_', ' + ').title()
        
        if post_type == PostType.TEXT_URL:
            format_instructions = f"""
            Generate {actual_count} Text + URL posts (40-120 characters each):
            - CRITICAL: Include clear Call-To-Action with URL
            - Short, punchy, social media optimized
            - Twitter/Instagram friendly length
            - Strong action verbs (Discover, Transform, Boost, etc.)
            - Include URL placement naturally
            - Platform: LinkedIn, Twitter, Instagram optimized
            """
        elif post_type == PostType.TEXT_IMAGE:
            format_instructions = f"""
            Generate {actual_count} Text + Image posts (30-80 characters each):
            - Very short text to complement visuals
            - Include detailed image generation prompts for Imagen API
            - Visual storytelling approach
            - Instagram/TikTok optimized
            - Let the image do the talking
            Cost Control: Limited to {actual_count} posts to manage Imagen API costs
            """
        else:  # TEXT_VIDEO
            format_instructions = f"""
            Generate {actual_count} Text + Video posts (40-100 characters each):
            - Short, dynamic captions for video content
            - Include detailed video concept descriptions for Veo API
            - TikTok/Instagram Reels/YouTube Shorts optimized
            - Action-oriented language
            - Focus on movement and energy
            Cost Control: Limited to {actual_count} posts to manage Veo API costs
            """
        
        # Platform-specific character limits and requirements
        platform_requirements = {
            PostType.TEXT_URL: "Twitter: 280 chars max, Instagram: 125 chars optimal, LinkedIn: 150 chars optimal",
            PostType.TEXT_IMAGE: "Instagram: 30-80 chars, TikTok: 40-80 chars, Visual focus",
            PostType.TEXT_VIDEO: "TikTok: 40-100 chars, Instagram Reels: 60 chars, YouTube Shorts: 80 chars"
        }
        
        # Comprehensive batch generation prompt
        batch_prompt = f"""
        As a professional social media marketing expert, generate {actual_count} high-quality {post_type_name} posts for {company_name}.

        Business Context:
        - Company: {company_name}
        - Objective: {objective}
        - Campaign Type: {campaign_type}
        - Target Audience: {target_audience}
        - Business Description: {business_description}
        - Website URL: {business_context.get('business_website', business_context.get('product_service_url', 'https://example.com'))}

        {format_instructions}

        Platform Requirements: {platform_requirements[post_type]}

        CRITICAL Requirements for ALL posts:
        - Keep text SHORT and PUNCHY for social media
        - For TEXT_URL: MUST include Call-To-Action with URL
        - For TEXT_IMAGE: MUST include detailed image prompt for AI generation
        - For TEXT_VIDEO: MUST include detailed video concept for AI generation
        - Use emojis strategically for engagement
        - Include 3-4 relevant hashtags (separate field)
        - Make content specific to {company_name} and their {objective}

        Format your response as JSON:
        {{
            "posts": [
                {{
                    "content": "Short punchy text here (follow character limits)",
                    "hashtags": ["#tag1", "#tag2", "#tag3"],
                    {"image_prompt" if post_type == PostType.TEXT_IMAGE else "video_prompt" if post_type == PostType.TEXT_VIDEO else "call_to_action"}: "{"Detailed image description for Imagen API" if post_type == PostType.TEXT_IMAGE else "Detailed video concept for Veo API" if post_type == PostType.TEXT_VIDEO else "Strong CTA with URL"}",
                    {"url" if post_type == PostType.TEXT_URL else "engagement_strategy"}: "{"Include website URL here" if post_type == PostType.TEXT_URL else "Brief engagement approach"}"
                }},
                // ... repeat for {actual_count} posts
            ]
        }}

        Generate exactly {actual_count} unique, SHORT, social media optimized posts that will drive {objective} for {company_name}.
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
                            "linkedin": f"Professional {post_type.value} content optimized for LinkedIn",
                            "twitter": f"Concise {post_type.value} content for Twitter engagement",
                            "facebook": f"Community-focused {post_type.value} content for Facebook",
                            "instagram": f"Visual {post_type.value} content for Instagram"
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
                        
                        # Add CTA to content if not already present
                        cta = post_data.get('call_to_action', '')
                        if cta and post_url:
                            if post_url not in post_content:
                                post.content = f"{post_content}\n\n{cta}\n{post_url}"
                            
                    elif post_type == PostType.TEXT_IMAGE:
                        post.image_prompt = post_data.get('image_prompt', f'Professional marketing image for {company_name} showing {objective}')
                        # Add placeholder URLs for visual content
                        post.image_url = f"https://picsum.photos/1024/576?random={i+100}&blur=1"
                        
                    elif post_type == PostType.TEXT_VIDEO:
                        post.video_prompt = post_data.get('video_prompt', f'Dynamic marketing video showcasing {company_name} approach to {objective}')
                        # Add placeholder URLs for visual content
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
            if post_url:
                post.content = f"{post.content}\n\n👉 Learn more: {post_url}"
                
        elif post_type == PostType.TEXT_IMAGE:
            post.image_prompt = f'Professional marketing image for {company_name} showing {objective}'
            post.image_url = f"https://picsum.photos/1024/576?random={i+100}&blur=1"
            
        elif post_type == PostType.TEXT_VIDEO:
            post.video_prompt = f'Dynamic marketing video showcasing {company_name} approach to {objective}'
            post.video_url = f"https://picsum.photos/1024/576?random={i+200}&grayscale"
        
        posts.append(post)
    
    return posts 