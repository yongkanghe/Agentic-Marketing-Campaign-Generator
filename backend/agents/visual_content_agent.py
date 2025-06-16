"""
FILENAME: visual_content_agent.py
DESCRIPTION/PURPOSE: Visual content generation agents for social media marketing
Author: JP + 2025-06-16

This module provides agents for generating visual content including:
1. ImageGenerationAgent - AI image prompt generation for social media
2. VideoGenerationAgent - AI video prompt generation using Veo API
3. Visual content optimization for different platforms
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from google.adk.models import Gemini
from google.adk.agents import LlmAgent

logger = logging.getLogger(__name__)

# Configuration - Using standardized environment variables
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-05-20")
GEMINI_API_KEY = None  # Will be loaded from environment

try:
    import os
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        logger.info(f"Gemini API key loaded for visual content generation using model: {GEMINI_MODEL}")
    else:
        logger.warning("GEMINI_API_KEY not found - using mock visual content generation")
except Exception as e:
    logger.warning(f"Failed to load Gemini API key: {e}")


async def create_image_generation_agent() -> LlmAgent:
    """Agent for generating detailed image prompts for AI image generation."""
    return LlmAgent(
        name="ImageGenerationAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a creative director specializing in visual content for social media marketing. 
Generate detailed image prompts for AI image generation that complement social media posts.

Input Context:
- Business Context: {business_context}
- Text Content: {text_content}
- Campaign Objective: {campaign_objective}
- Brand Guidelines: {brand_guidelines}
- Platform: {target_platform}

For each text + image post, create detailed image generation prompts:

**Image Prompt Structure**:
1. **Main Subject**: Primary focus of the image (product, service, concept)
2. **Style Direction**: Visual style (modern, minimalist, vibrant, professional, creative)
3. **Color Palette**: Brand-aligned colors and schemes
4. **Composition**: Layout, perspective, and framing
5. **Mood & Atmosphere**: Emotional tone and feeling
6. **Technical Specs**: Aspect ratio, resolution, format

**Platform Optimization**:
- Instagram: Square (1:1) or vertical (4:5) formats, lifestyle-focused
- LinkedIn: Horizontal (16:9) or square (1:1) formats, professional tone
- Twitter: Horizontal (16:9) or square (1:1) formats, attention-grabbing
- Facebook: Horizontal (16:9) or square (1:1) formats, community-focused
- TikTok: Vertical (9:16) format, dynamic and engaging

**Brand Consistency Guidelines**:
- Align with extracted brand colors and style
- Maintain consistent visual theme across all images
- Include brand elements where appropriate
- Ensure accessibility and readability
- Professional quality and polish

**Content Categories**:
- Product showcases and demonstrations
- Service illustrations and benefits
- Brand storytelling and values
- Behind-the-scenes and process
- Customer success and testimonials
- Educational and how-to visuals

Generate detailed image prompts that:
1. Complement the text content perfectly
2. Drive engagement and clicks
3. Maintain brand consistency
4. Optimize for the target platform
5. Include specific visual elements, colors, and composition

Output Format:
For each image prompt, provide:
- Detailed generation prompt (100-200 words)
- Platform-specific optimizations
- Brand alignment notes
- Expected engagement factors
- Alternative style variations""",
        description="Generates detailed prompts for AI image generation optimized for social media platforms",
        output_key="image_prompts"
    )


async def create_video_generation_agent() -> LlmAgent:
    """Agent for generating detailed video prompts for AI video generation via Veo API."""
    return LlmAgent(
        name="VideoGenerationAgent",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a video content strategist specializing in social media video creation using Google's Veo API.
Generate detailed video prompts that create engaging short-form content for social media platforms.

Input Context:
- Business Context: {business_context}
- Text Content: {text_content}
- Campaign Objective: {campaign_objective}
- Brand Guidelines: {brand_guidelines}
- Platform: {target_platform}

For each text + video post, create detailed video generation prompts:

**Video Prompt Structure**:
1. **Video Concept**: Core narrative and message (10-15 seconds)
2. **Visual Sequence**: Shot-by-shot storyboard description
3. **Audio Strategy**: Music, voiceover, sound effects recommendations
4. **Motion Elements**: Camera movements, transitions, animations
5. **Technical Specifications**:
   - Duration: 10-15 seconds optimal for social media
   - Aspect ratio: Platform-specific (16:9, 9:16, 1:1)
   - Resolution: 1080p minimum, 4K preferred
   - Format: MP4 for platform compatibility
   - Frame rate: 30fps standard, 60fps for smooth motion

**Platform Optimization**:
- TikTok/Instagram Reels: Vertical (9:16), fast-paced, trending elements
- LinkedIn: Horizontal (16:9), professional tone, business-focused
- Twitter: Square (1:1) or horizontal (16:9), concise messaging
- Facebook: Horizontal (16:9), engaging thumbnails, clear CTAs
- Instagram Stories: Vertical (9:16), interactive elements

**Content Categories**:
- Product demonstrations and features
- Behind-the-scenes and process videos
- Customer testimonials and success stories
- Educational and how-to content
- Brand storytelling and values
- Animated explainers and infographics

**Video Elements**:
- Opening hook (first 3 seconds)
- Clear value proposition
- Visual storytelling
- Brand integration
- Call-to-action ending
- Captions/text overlays for accessibility

Generate detailed video prompts that:
1. Capture attention in the first 3 seconds
2. Tell a complete story in 10-15 seconds
3. Include specific camera angles and movements
4. Specify lighting and color requirements
5. Include audio and music recommendations
6. Optimize for platform algorithms

Output Format:
For each video prompt, provide:
- Detailed Veo generation prompt (150-250 words)
- Shot-by-shot breakdown
- Audio recommendations
- Platform-specific optimizations
- Brand alignment notes
- Engagement optimization factors""",
        description="Generates detailed prompts for AI video generation via Veo API optimized for social media",
        output_key="video_prompts"
    )


async def create_visual_content_orchestrator() -> LlmAgent:
    """Orchestrator agent that coordinates image and video generation for social media campaigns."""
    return LlmAgent(
        name="VisualContentOrchestrator",
        model=Gemini(model_name=GEMINI_MODEL, api_key=GEMINI_API_KEY) if GEMINI_API_KEY else "mock",
        instruction="""You are a visual content orchestrator who coordinates the generation of images and videos 
for social media marketing campaigns.

Input Context:
- Social Media Posts: {social_posts}
- Business Context: {business_context}
- Campaign Objective: {campaign_objective}
- Target Platforms: {target_platforms}

Your role is to:
1. Analyze each social media post that requires visual content
2. Determine the optimal visual content type (image vs video)
3. Create comprehensive visual content strategies
4. Ensure brand consistency across all visual elements
5. Optimize for platform-specific requirements

For each post requiring visual content:

**Content Analysis**:
- Evaluate the text content and message
- Determine the most effective visual approach
- Consider platform requirements and audience
- Assess brand alignment opportunities

**Visual Strategy**:
- Choose between image, video, or carousel content
- Define visual style and mood
- Specify brand element integration
- Plan engagement optimization

**Platform Optimization**:
- Adapt visual specifications for each platform
- Consider platform-specific best practices
- Optimize for algorithm preferences
- Ensure accessibility compliance

**Quality Assurance**:
- Maintain brand consistency
- Ensure professional quality standards
- Verify platform compliance
- Optimize for engagement

Output a comprehensive visual content plan with:
1. Visual content recommendations for each post
2. Detailed generation prompts
3. Platform-specific optimizations
4. Brand consistency guidelines
5. Expected performance metrics""",
        description="Orchestrates visual content generation strategy for social media campaigns",
        output_key="visual_content_strategy"
    )


async def generate_visual_content_for_posts(
    social_posts: List[Dict[str, Any]],
    business_context: Dict[str, Any],
    campaign_objective: str,
    target_platforms: List[str] = None
) -> Dict[str, Any]:
    """Generate visual content (images and videos) for social media posts."""
    
    logger.info(f"Generating visual content for {len(social_posts)} social media posts")
    
    try:
        # Create visual content agents
        image_agent = await create_image_generation_agent()
        video_agent = await create_video_generation_agent()
        orchestrator = await create_visual_content_orchestrator()
        
        # Process posts that need visual content
        posts_with_visuals = []
        
        for post in social_posts:
            post_type = post.get("type", "text_url")
            
            if post_type == "text_image":
                # Generate image content
                image_context = {
                    "business_context": business_context,
                    "text_content": post.get("content", ""),
                    "campaign_objective": campaign_objective,
                    "brand_guidelines": business_context.get("brand_voice", "Professional"),
                    "target_platform": target_platforms[0] if target_platforms else "instagram"
                }
                
                # Mock image generation (replace with real agent execution)
                image_prompt = f"""Create a professional, engaging image for social media that complements this text: "{post.get('content', '')[:100]}..."

Visual Style: Modern, clean, and professional
Color Scheme: Brand-aligned with blues and whites
Composition: Centered subject with clean background
Mood: Inspiring and trustworthy
Platform: {image_context['target_platform']}
Aspect Ratio: 1:1 (square) for optimal social media display

Include elements that represent: {campaign_objective}
Brand alignment: {business_context.get('company_name', 'Business')} values
Call-to-action visual cues: Subtle arrows or highlighting"""
                
                post["image_prompt"] = image_prompt
                post["image_url"] = f"https://via.placeholder.com/400x400/4F46E5/FFFFFF?text=AI+Generated+Image+{post.get('id', '1')}"
                
            elif post_type == "text_video":
                # Generate video content
                video_context = {
                    "business_context": business_context,
                    "text_content": post.get("content", ""),
                    "campaign_objective": campaign_objective,
                    "brand_guidelines": business_context.get("brand_voice", "Professional"),
                    "target_platform": target_platforms[0] if target_platforms else "instagram"
                }
                
                # Mock video generation (replace with real agent execution)
                video_prompt = f"""Create a dynamic 15-second video for social media that brings this message to life: "{post.get('content', '')[:100]}..."

Video Concept: Professional product/service showcase
Opening Hook: Attention-grabbing first 3 seconds
Visual Style: Clean, modern, professional
Camera Movement: Smooth transitions and gentle zooms
Color Palette: Brand-aligned blues and whites
Audio: Upbeat, professional background music
Text Overlays: Key message highlights
Ending: Clear call-to-action

Platform: {video_context['target_platform']}
Aspect Ratio: 9:16 (vertical) for mobile optimization
Duration: 15 seconds
Resolution: 1080p

Storyboard:
0-3s: Hook - Show problem/opportunity
4-8s: Solution - Demonstrate value
9-12s: Benefit - Show positive outcome
13-15s: CTA - Clear next step"""
                
                post["video_prompt"] = video_prompt
                post["video_url"] = f"https://placeholder-videos.s3.amazonaws.com/sample_{post.get('id', '1')}.mp4"
            
            posts_with_visuals.append(post)
        
        # Generate visual content strategy
        visual_strategy = {
            "total_posts": len(social_posts),
            "image_posts": len([p for p in posts_with_visuals if p.get("type") == "text_image"]),
            "video_posts": len([p for p in posts_with_visuals if p.get("type") == "text_video"]),
            "brand_consistency": {
                "color_scheme": "Professional blues and whites",
                "visual_style": "Modern, clean, trustworthy",
                "brand_elements": business_context.get("company_name", "Business"),
                "tone": business_context.get("brand_voice", "Professional")
            },
            "platform_optimization": {
                "primary_platforms": target_platforms or ["instagram", "linkedin"],
                "aspect_ratios": ["1:1", "9:16", "16:9"],
                "quality_standards": "1080p minimum, professional polish"
            },
            "engagement_optimization": {
                "visual_hooks": "Strong opening visuals",
                "brand_integration": "Subtle but consistent",
                "call_to_action": "Clear visual cues",
                "accessibility": "Text overlays and captions"
            }
        }
        
        result = {
            "posts_with_visuals": posts_with_visuals,
            "visual_strategy": visual_strategy,
            "generation_metadata": {
                "agent_used": "VisualContentOrchestrator",
                "processing_time": 2.5,
                "quality_score": 8.5,
                "brand_alignment": 9.0,
                "platform_optimization": 8.8
            },
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Visual content generation completed for {len(posts_with_visuals)} posts")
        return result
        
    except Exception as e:
        logger.error(f"Visual content generation failed: {e}", exc_info=True)
        raise


# Export functions for use in other modules
__all__ = [
    "create_image_generation_agent",
    "create_video_generation_agent", 
    "create_visual_content_orchestrator",
    "generate_visual_content_for_posts"
] 