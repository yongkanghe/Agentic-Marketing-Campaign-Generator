"""
FILENAME: content.py
DESCRIPTION/PURPOSE: Content generation API routes for social media posts
Author: JP + 2025-06-16
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException

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
        
        # Use real ADK agent execution if available
        if execute_campaign_workflow and business_context:
            logger.info("Using real ADK agent execution for content generation")
            
            # Execute the marketing campaign workflow with real business context
            workflow_result = await execute_campaign_workflow(
                business_description=business_context.get('business_description', ''),
                objective=business_context.get('objective', 'increase sales'),
                target_audience=business_context.get('target_audience', 'business professionals'),
                campaign_type=business_context.get('campaign_type', 'service'),
                creativity_level=creativity_level,
                business_website=business_context.get('business_website'),
                about_page_url=business_context.get('about_page_url'),
                product_service_url=business_context.get('product_service_url')
            )
            
            # Extract posts of the requested type from workflow result
            all_posts = workflow_result.get('social_posts', [])
            filtered_posts = [post for post in all_posts if post.get('type') == request.post_type.value]
            
            # Take the requested number of posts
            selected_posts = filtered_posts[:request.regenerate_count]
            
            # Transform to API response format
            new_posts = []
            for i, post in enumerate(selected_posts):
                api_post = SocialMediaPost(
                    id=post.get('id', f"real_generated_{request.post_type}_{i+1}"),
                    type=request.post_type,
                    content=post.get('content', f"AI-generated {request.post_type.replace('_', ' + ')} content"),
                    hashtags=post.get('hashtags', ["#AI", "#Marketing", "#Business"]),
                    platform_optimized=post.get('platform_optimized', {}),
                    engagement_score=post.get('engagement_score', 8.0 + (i * 0.1)),
                    selected=False
                )
                new_posts.append(api_post)
            
            # If we don't have enough posts, generate additional ones using enhanced mock
            while len(new_posts) < request.regenerate_count:
                i = len(new_posts)
                enhanced_post = SocialMediaPost(
                    id=f"enhanced_{request.post_type}_{i+1}",
                    type=request.post_type,
                    content=generate_enhanced_content(request.post_type, business_context, i),
                    hashtags=generate_contextual_hashtags(business_context),
                    platform_optimized={
                        "linkedin": f"Professional {request.post_type.replace('_', ' + ')} content for LinkedIn",
                        "twitter": f"Engaging {request.post_type.replace('_', ' + ')} content for Twitter",
                        "instagram": f"Visual {request.post_type.replace('_', ' + ')} content for Instagram"
                    },
                    engagement_score=8.0 + (i * 0.1),
                    selected=False
                )
                new_posts.append(enhanced_post)
            
            return SocialPostRegenerationResponse(
                new_posts=new_posts,
                regeneration_metadata={
                    "post_type": request.post_type,
                    "regenerate_count": len(new_posts),
                    "method": "real_adk_agent_execution",
                    "business_context_used": True,
                    "workflow_id": workflow_result.get('campaign_id'),
                    "agent_execution_order": workflow_result.get('workflow_metadata', {}).get('agent_execution_order', [])
                },
                processing_time=workflow_result.get('processing_time', 2.5)
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
    
    base_content = {
        PostType.text_url: [
            f"🚀 Exciting developments at {company_name}! We're transforming how businesses {objective} through our innovative {campaign_type} approach. Our latest solution addresses the core challenges we've identified in the market, delivering measurable results for companies just like yours. Ready to see what's possible? Check out our latest insights and discover how we can help accelerate your success.",
            f"💡 Innovation meets results at {company_name}. Our {campaign_type} solution is designed specifically for businesses looking to {objective} in today's competitive landscape. What sets us apart? We understand the unique challenges you face and have developed a proven approach that delivers real value. Learn more about our methodology and see how we can help transform your business outcomes.",
            f"🎯 Success stories are being written every day with {company_name}'s {campaign_type} solutions. Companies are achieving their goals to {objective} faster than ever before. Our approach combines industry expertise with innovative thinking to create solutions that work in the real world. Want to be our next success story? Discover how we can help you achieve your business objectives.",
            f"✨ Behind the scenes at {company_name}: Here's how we're helping businesses {objective} through strategic {campaign_type} solutions. Our team has worked tirelessly to understand market dynamics and create something truly valuable. The results speak for themselves - our clients are seeing significant improvements in their key business metrics. Ready to learn more?",
            f"🔥 Game-changing results start with the right {campaign_type} partner. At {company_name}, we're committed to helping businesses {objective} through proven strategies and innovative solutions. Our approach isn't just about delivering services - it's about creating lasting partnerships that drive sustainable growth. See how we can help transform your business trajectory."
        ],
        PostType.text_image: [
            f"🎨 Visual storytelling meets business results. This image captures the essence of how {company_name} helps businesses {objective} through innovative {campaign_type} solutions. Every element represents our commitment to excellence and our understanding of what it takes to succeed in today's market. This isn't just a visual - it's a representation of the transformation possible when you partner with the right team.",
            f"📸 A picture tells the story of transformation. Here's how {company_name} approaches {campaign_type} solutions for businesses looking to {objective}. This visual represents months of research, development, and real-world application. We believe that great results start with clear vision, and this image embodies our approach to creating meaningful business impact.",
            f"🌟 Innovation in action. This image showcases our approach to helping businesses {objective} through strategic {campaign_type} solutions. Every color, shape, and element has been chosen to communicate our core values: excellence, innovation, and results. This visual is just the beginning of what we can accomplish together.",
            f"💫 Design meets strategy in this powerful representation of {company_name}'s {campaign_type} approach. We help businesses {objective} by combining creative thinking with proven methodologies. This image tells our story of transformation, growth, and success - values that drive everything we do.",
            f"🎭 Creative excellence meets business acumen. This visual represents how {company_name} helps businesses {objective} through innovative {campaign_type} solutions. We believe that great design isn't just about aesthetics - it's about communication, connection, and creating experiences that drive real business results."
        ],
        PostType.text_video: [
            f"🎬 Motion tells the story of transformation. This video showcases how {company_name} helps businesses {objective} through dynamic {campaign_type} solutions. In just seconds, you'll see the power of our approach and understand why companies choose us as their strategic partner. This isn't just a video - it's a window into the future of your business success.",
            f"📹 Dynamic storytelling for dynamic results. Watch how {company_name} approaches {campaign_type} solutions for businesses looking to {objective}. This video captures the energy, innovation, and results-driven approach that defines our work. Every frame has been crafted to communicate our commitment to your success.",
            f"🎥 Action speaks louder than words. This video demonstrates our {campaign_type} approach to helping businesses {objective} in today's competitive landscape. From concept to execution, you'll see how we turn ideas into results and challenges into opportunities. Ready to see what's possible for your business?",
            f"🌟 Movement creates momentum. This video showcases the dynamic approach {company_name} takes to {campaign_type} solutions. We help businesses {objective} by combining strategic thinking with innovative execution. Watch how we transform challenges into opportunities and ideas into measurable results.",
            f"🚀 Velocity meets vision in this powerful video representation of {company_name}'s {campaign_type} approach. We help businesses {objective} by creating solutions that move at the speed of opportunity. This video captures the energy and innovation that drives our success and yours."
        ]
    }
    
    content_list = base_content.get(post_type, base_content[PostType.text_url])
    selected_content = content_list[index % len(content_list)]
    
    # Add theme-specific enhancements
    if 'innovation' in themes:
        selected_content = selected_content.replace('approach', 'cutting-edge approach')
    if 'quality' in themes:
        selected_content = selected_content.replace('solutions', 'premium solutions')
    if 'customer-focused' in themes:
        selected_content = selected_content.replace('business', 'customer-centric business')
    
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