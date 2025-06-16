"""
FILENAME: content.py
DESCRIPTION/PURPOSE: Content generation API routes for social media posts
Author: JP + 2025-06-15
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException

from ..models import (
    ContentGenerationRequest, ContentGenerationResponse,
    SocialPostRegenerationRequest, SocialPostRegenerationResponse,
    SocialMediaPost, PostType
)

# Import visual content generation
try:
    from agents.visual_content_agent import generate_visual_content_for_posts
    logger.info("Visual content agent available for API endpoints")
except ImportError as e:
    logger.warning(f"Visual content agent not available: {e}")
    generate_visual_content_for_posts = None

logger = logging.getLogger(__name__)
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
    """Regenerate specific social media posts."""
    
    try:
        logger.info(f"Regenerating {request.regenerate_count} {request.post_type} posts")
        
        # Mock regeneration (replace with real ADK agent call)
        new_posts = []
        for i in range(request.regenerate_count):
            post = SocialMediaPost(
                id=f"regenerated_{request.post_type}_{i+1}",
                type=request.post_type,
                content=f"Regenerated {request.post_type.replace('_', ' + ')} content with fresh perspective",
                hashtags=["#Regenerated", "#Fresh", "#Content"],
                platform_optimized={
                    "linkedin": f"Refreshed professional content",
                    "twitter": f"New engaging tweet",
                    "instagram": f"Updated visual content"
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
                "method": "mock_regeneration"
            },
            processing_time=1.0
        )
        
    except Exception as e:
        logger.error(f"Post regeneration failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Post regeneration failed: {str(e)}"
        )


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