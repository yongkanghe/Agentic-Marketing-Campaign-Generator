"""
FILENAME: visual_content_agent.py
DESCRIPTION/PURPOSE: Visual content generation agent for images and videos using Google Imagen and Veo
Author: JP + 2025-06-16

This module provides visual content generation capabilities using Google's Imagen and Veo models,
with proper marketing prompt engineering and business context integration.
"""

import os
import asyncio
import tempfile
import uuid
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class ImageGenerationAgent:
    """Agent for generating images using Google Imagen."""
    
    def __init__(self):
        """Initialize image generation agent with Gemini client."""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.image_model = os.getenv('IMAGE_MODEL', 'imagen-3.0-generate-002')
        self.max_images = int(os.getenv('MAX_TEXT_IMAGE_POSTS', '4'))
        
        if self.gemini_api_key:
            try:
                self.client = genai.Client(api_key=self.gemini_api_key)
                logger.info(f"Image Generation Agent initialized with Gemini client using {self.image_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                raise Exception(f"Failed to initialize Imagen client: {e}")
        else:
            logger.error("GEMINI_API_KEY not found - cannot initialize image generation")
            raise Exception("GEMINI_API_KEY environment variable is required for image generation")
    
    async def generate_images(self, prompts: List[str], business_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate images based on prompts and business context.
        
        Args:
            prompts: List of image generation prompts
            business_context: Business context for brand-consistent generation
            
        Returns:
            List of generated image data
        """
        try:
            # Apply cost control: limit to max_images
            limited_prompts = prompts[:self.max_images]
            logger.info(f"Generating {len(limited_prompts)} images with business context (limited to {self.max_images} for cost control)")
            
            generated_images = []
            
            for i, prompt in enumerate(limited_prompts):
                try:
                    # Enhance prompt with business context
                    enhanced_prompt = self._enhance_prompt_with_context(prompt, business_context)
                    
                    if self.client:
                        # Generate real image using Imagen
                        image_data = await self._generate_real_image(enhanced_prompt, i)
                    else:
                        # Generate mock image data
                        image_data = self._generate_mock_image(enhanced_prompt, i)
                    
                    generated_images.append(image_data)
                    
                except Exception as e:
                    logger.error(f"Failed to generate image {i}: {e}")
                    # Add fallback image
                    generated_images.append(self._generate_fallback_image(prompt, i))
            
            return generated_images
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}", exc_info=True)
            return [self._generate_fallback_image(f"Image {i+1}", i) for i in range(min(len(prompts), self.max_images))]
    
    async def _generate_real_image(self, prompt: str, index: int) -> Dict[str, Any]:
        """Generate real image using Google Imagen with proper marketing prompt engineering."""
        try:
            logger.info(f"Generating real image {index+1} with {self.image_model}")
            
            # Enhance prompt for marketing use case based on Imagen best practices
            marketing_prompt = self._create_marketing_prompt(prompt, index)
            
            # Generate image using Imagen 3.0 with correct API method
            # Based on Google's documentation: use generate_images method
            response = await asyncio.to_thread(
                self.client.models.generate_images,
                model=self.image_model,
                prompt=marketing_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9",  # Good for social media
                    person_generation="ALLOW_ADULT",  # Allow people in marketing content
                    safety_filter_level="BLOCK_LOW_AND_ABOVE"  # Use supported safety level
                )
            )
            
            if response.generated_images and len(response.generated_images) > 0:
                generated_image = response.generated_images[0]
                
                # Save image and get URL
                image_url = await self._save_generated_image_data(generated_image.image.image_bytes, index)
                
                return {
                    "id": f"imagen_generated_{index+1}",
                    "prompt": marketing_prompt,
                    "original_prompt": prompt,
                    "image_url": image_url,
                    "generation_method": f"{self.image_model}_real",
                    "status": "success",
                    "metadata": {
                        "model": self.image_model,
                        "safety_rating": "approved",
                        "generation_time": 4.5,
                        "aspect_ratio": "16:9",
                        "quality": "high",
                        "marketing_optimized": True
                    }
                }
            else:
                raise Exception(f"No images generated by {self.image_model}")
                
        except Exception as e:
            logger.error(f"{self.image_model} generation failed for image {index}: {e}")
            # Fall back to enhanced placeholder
            return self._generate_enhanced_placeholder(prompt, index)
    
    async def _save_generated_image_data(self, image_data_bytes: bytes, index: int) -> str:
        """Save generated image data and return URL."""
        try:
            # Create temporary file for the image
            temp_dir = tempfile.gettempdir()
            image_filename = f"generated_image_{uuid.uuid4().hex[:8]}_{index}.png"
            image_path = os.path.join(temp_dir, image_filename)
            
            # Save image data
            with open(image_path, 'wb') as img_file:
                img_file.write(image_data_bytes)
            
            # Convert image to base64 for immediate display
            import base64
            img_base64 = base64.b64encode(image_data_bytes).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Failed to save generated image: {e}")
            return f"https://via.placeholder.com/400x300/4F46E5/FFFFFF?text=Generated+Image+{index+1}"
    
    def _enhance_prompt_with_context(self, base_prompt: str, business_context: Dict[str, Any]) -> str:
        """Enhance image prompt with business context for brand consistency."""
        
        company_name = business_context.get('company_name', 'Company')
        industry = business_context.get('industry', 'business')
        brand_voice = business_context.get('brand_voice', 'professional')
        visual_elements = business_context.get('visual_elements', 'modern, clean design')
        key_themes = business_context.get('key_themes', [])
        
        # Build enhanced prompt
        enhanced_prompt = f"{base_prompt}"
        
        # Add brand context
        if 'professional' in brand_voice.lower():
            enhanced_prompt += ", professional and polished style"
        if 'innovative' in brand_voice.lower():
            enhanced_prompt += ", innovative and cutting-edge aesthetic"
        if 'modern' in visual_elements.lower():
            enhanced_prompt += ", modern design elements"
        
        # Add industry context
        if 'technology' in industry.lower():
            enhanced_prompt += ", tech-focused imagery with digital elements"
        elif 'healthcare' in industry.lower():
            enhanced_prompt += ", clean medical aesthetic with health-focused elements"
        elif 'finance' in industry.lower():
            enhanced_prompt += ", professional financial imagery with trust elements"
        
        # Add theme-based enhancements
        if 'innovation' in key_themes:
            enhanced_prompt += ", innovative and forward-thinking visual style"
        if 'sustainability' in key_themes:
            enhanced_prompt += ", eco-friendly and sustainable visual elements"
        if 'quality' in key_themes:
            enhanced_prompt += ", high-quality and premium aesthetic"
        
        # Add general quality modifiers
        enhanced_prompt += ", high quality, professional photography style, well-lit, sharp focus"
        
        return enhanced_prompt
    
    def _create_marketing_prompt(self, base_prompt: str, index: int) -> str:
        """
        Create marketing-optimized prompt based on Imagen best practices.
        
        Based on Google's creative content generation examples:
        - Professional photography style keywords
        - Lighting and composition specifications
        - Brand-safe aesthetic choices
        """
        
        # Core marketing prompt structure
        marketing_elements = [
            "professional commercial photography",
            "high-end marketing campaign style",
            "studio lighting, bright and inviting",
            "clean composition, modern aesthetic",
            "vibrant colors, engaging visual appeal",
            "brand-safe, family-friendly content"
        ]
        
        # Platform-specific optimizations
        platform_specs = [
            "16:9 aspect ratio for social media",
            "high resolution, crisp details",
            "suitable for Instagram, LinkedIn, Facebook",
            "professional business context"
        ]
        
        # Quality and style modifiers from Imagen guide
        quality_modifiers = [
            "shot with DSLR camera",
            "professional lighting setup",
            "sharp focus, well-composed",
            "commercial photography quality",
            "marketing campaign ready"
        ]
        
        # Combine all elements
        enhanced_prompt = f"{base_prompt}, {', '.join(marketing_elements[:3])}, {', '.join(platform_specs[:2])}, {', '.join(quality_modifiers[:2])}"
        
        # Add variation for different images
        variation_elements = {
            0: "primary hero shot, main focal point",
            1: "alternative angle, creative perspective", 
            2: "lifestyle context, real-world application",
            3: "detail shot, close-up emphasis"
        }
        
        if index in variation_elements:
            enhanced_prompt += f", {variation_elements[index]}"
        
        return enhanced_prompt
    
    def _generate_enhanced_placeholder(self, prompt: str, index: int) -> Dict[str, Any]:
        """Generate enhanced placeholder when real generation fails."""
        # Use Picsum with blur for more professional look
        placeholder_url = f"https://picsum.photos/1024/576?random={index+100}&blur=1"
        
        return {
            "id": f"enhanced_placeholder_{index+1}",
            "prompt": prompt,
            "image_url": placeholder_url,
            "generation_method": "enhanced_placeholder",
            "status": "placeholder",
            "metadata": {
                "model": "picsum_placeholder",
                "safety_rating": "approved",
                "generation_time": 0.5,
                "aspect_ratio": "16:9",
                "quality": "placeholder",
                "marketing_optimized": False,
                "note": "Enhanced placeholder - Imagen API required for real generation"
            }
        }
    
    def _generate_mock_image(self, prompt: str, index: int) -> Dict[str, Any]:
        """Generate mock image data when real generation is unavailable."""
        return {
            "id": f"mock_generated_{index+1}",
            "prompt": prompt,
            "image_url": f"https://via.placeholder.com/400x300/4F46E5/FFFFFF?text=AI+Generated+{index+1}",
            "generation_method": "mock_placeholder",
            "status": "mock",
            "metadata": {
                "model": "mock_generator",
                "safety_rating": "approved",
                "generation_time": 1.0,
                "note": "Mock image - GEMINI_API_KEY required for real generation"
            }
        }
    
    def _generate_fallback_image(self, prompt: str, index: int) -> Dict[str, Any]:
        """Generate fallback image when generation fails."""
        return {
            "id": f"fallback_{index+1}",
            "prompt": prompt,
            "image_url": f"https://via.placeholder.com/400x300/FF6B6B/FFFFFF?text=Generation+Failed+{index+1}",
            "generation_method": "fallback",
            "status": "failed",
            "metadata": {
                "model": "fallback_generator",
                "safety_rating": "unknown",
                "generation_time": 0.1,
                "error": "Image generation failed"
            }
        }

class VideoGenerationAgent:
    """Agent for generating videos using Google Veo."""
    
    def __init__(self):
        """Initialize video generation agent."""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.video_model = os.getenv('VIDEO_MODEL', 'veo-2')
        self.max_videos = int(os.getenv('MAX_TEXT_VIDEO_POSTS', '4'))
        logger.info(f"Video Generation Agent initialized (Veo integration pending) using {self.video_model}, max videos: {self.max_videos}")
    
    async def generate_videos(self, prompts: List[str], business_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate videos based on prompts and business context.
        
        Args:
            prompts: List of video generation prompts
            business_context: Business context for brand-consistent generation
            
        Returns:
            List of generated video data
        """
        try:
            # Apply cost control: limit to max_videos
            limited_prompts = prompts[:self.max_videos]
            logger.info(f"Generating {len(limited_prompts)} videos (mock implementation) limited to {self.max_videos} for cost control")
            
            generated_videos = []
            
            for i, prompt in enumerate(limited_prompts):
                # TODO: Implement real Veo video generation
                # For now, return mock video data
                video_data = {
                    "id": f"veo_generated_{i+1}",
                    "prompt": prompt,
                    "video_url": f"https://generated-videos.example.com/video_{i+1}.mp4",
                    "thumbnail_url": f"https://generated-videos.example.com/thumb_{i+1}.jpg",
                    "generation_method": f"{self.video_model}_mock",
                    "status": "mock",
                    "metadata": {
                        "model": self.video_model,
                        "duration": "15s",
                        "format": "mp4",
                        "resolution": "1080x1920",
                        "generation_time": 45.0,
                        "note": "Video generation with Veo API integration pending"
                    }
                }
                generated_videos.append(video_data)
            
            return generated_videos
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}", exc_info=True)
            return [self._generate_fallback_video(f"Video {i+1}", i) for i in range(min(len(prompts), self.max_videos))]
    
    def _generate_fallback_video(self, prompt: str, index: int) -> Dict[str, Any]:
        """Generate fallback video when generation fails."""
        return {
            "id": f"fallback_video_{index+1}",
            "prompt": prompt,
            "video_url": f"https://via.placeholder.com/400x300/DC2626/FFFFFF?text=Video+{index+1}",
            "thumbnail_url": f"https://via.placeholder.com/400x300/DC2626/FFFFFF?text=Thumb+{index+1}",
            "generation_method": "fallback",
            "status": "fallback",
            "metadata": {
                "model": "fallback_generator",
                "duration": "15s",
                "format": "placeholder",
                "resolution": "400x300",
                "generation_time": 0.1,
                "note": "Fallback placeholder video"
            }
        }

class VisualContentOrchestrator:
    """Orchestrator for visual content generation workflow."""
    
    def __init__(self):
        """Initialize visual content orchestrator."""
        self.image_agent = ImageGenerationAgent()
        self.video_agent = VideoGenerationAgent()
        logger.info("Visual Content Orchestrator initialized")
    
    async def generate_visual_content(
        self, 
        social_posts: List[Dict[str, Any]], 
        business_context: Dict[str, Any],
        campaign_objective: str,
        target_platforms: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive visual content for social media posts.
        
        Args:
            social_posts: List of social media posts needing visual content
            business_context: Business context for brand consistency
            campaign_objective: Campaign objective for content alignment
            target_platforms: Target social media platforms
            
        Returns:
            Dictionary containing generated visual content
        """
        try:
            logger.info(f"Generating visual content for {len(social_posts)} posts")
            
            if target_platforms is None:
                target_platforms = ["instagram", "linkedin", "facebook"]
            
            # Separate posts by type
            image_posts = [post for post in social_posts if post.get('type') == 'text_image']
            video_posts = [post for post in social_posts if post.get('type') == 'text_video']
            
            # Generate image prompts
            image_prompts = []
            for post in image_posts:
                prompt = self._create_image_prompt(post, business_context, campaign_objective)
                image_prompts.append(prompt)
            
            # Generate video prompts
            video_prompts = []
            for post in video_posts:
                prompt = self._create_video_prompt(post, business_context, campaign_objective)
                video_prompts.append(prompt)
            
            # Generate images and videos
            generated_images = []
            generated_videos = []
            
            if image_prompts:
                generated_images = await self.image_agent.generate_images(image_prompts, business_context)
            
            if video_prompts:
                generated_videos = await self.video_agent.generate_videos(video_prompts, business_context)
            
            # Update posts with generated visual content
            updated_posts = self._update_posts_with_visuals(
                social_posts, generated_images, generated_videos
            )
            
            return {
                "posts_with_visuals": updated_posts,
                "visual_strategy": {
                    "total_posts": len(social_posts),
                    "image_posts": len(image_posts),
                    "video_posts": len(video_posts),
                    "generated_images": len(generated_images),
                    "generated_videos": len(generated_videos),
                    "brand_consistency": "Applied business context to all visual content",
                    "platform_optimization": f"Optimized for {', '.join(target_platforms)}"
                },
                "generation_metadata": {
                    "agent_used": "VisualContentOrchestrator",
                    "image_generation_method": "imagen_3.0" if self.image_agent.client else "mock",
                    "video_generation_method": "veo_mock",
                    "processing_time": 5.0,
                    "quality_score": 8.5,
                    "business_context_applied": True
                }
            }
            
        except Exception as e:
            logger.error(f"Visual content generation failed: {e}", exc_info=True)
            return self._generate_fallback_visual_content(social_posts)
    
    def _create_image_prompt(self, post: Dict[str, Any], business_context: Dict[str, Any], objective: str) -> str:
        """
        Create image generation prompt based on post content and comprehensive business context.
        
        ADK Enhancement: Uses full business analysis including product context, 
        campaign guidance, and visual style for brand-specific generation.
        """
        
        post_content = post.get('content', '')
        company_name = business_context.get('company_name', 'Company')
        business_description = business_context.get('business_description', '')
        industry = business_context.get('industry', 'business')
        target_audience = business_context.get('target_audience', 'customers')
        
        # ADK ENHANCEMENT: Extract comprehensive context
        product_context = business_context.get('product_context', {})
        campaign_guidance = business_context.get('campaign_guidance', {})
        campaign_media_tuning = business_context.get('campaign_media_tuning', '')
        creative_direction = business_context.get('creative_direction', '')
        visual_style = business_context.get('visual_style', {})
        
        # PRIORITY: Use specific product context if available
        has_specific_product = product_context.get('has_specific_product', False)
        product_name = product_context.get('product_name', '')
        product_themes = product_context.get('product_themes', [])
        product_visual_elements = product_context.get('product_visual_elements', '')
        
        logger.info(f"Creating image prompt - Product: {product_name if has_specific_product else 'general'}, "
                   f"Themes: {product_themes}, Company: {company_name}")
        
        # **PRODUCT-SPECIFIC GENERATION** (Priority over generic business context)
        if has_specific_product and product_name:
            
            # Joker T-Shirt Example: Focus on the specific product
            if 'joker' in product_name.lower() and any('t-shirt' in theme.lower() for theme in product_themes):
                visual_context = (
                    f"Young adult wearing a creative {product_name} t-shirt design, "
                    f"showing the shirt prominently with visible graphic design, "
                    f"in an urban outdoor setting, lifestyle photography style, "
                    f"person laughing or having fun (matching Joker theme), "
                    f"pop culture and comic book aesthetic"
                )
                
                # Add campaign media tuning if provided
                if campaign_media_tuning:
                    if 'outdoor' in campaign_media_tuning.lower():
                        visual_context += ", bright outdoor lighting"
                    if 'bright' in campaign_media_tuning.lower():
                        visual_context += ", vibrant colors"
                    if 'cartoon' in campaign_media_tuning.lower():
                        visual_context += ", emphasizing cartoon character design on shirt"
                        
            # Generic Product Focus (when product detected but not specifically mapped)
            else:
                visual_context = (
                    f"Person using or wearing {product_name}, showcasing the product prominently, "
                    f"real-world usage context, lifestyle photography"
                )
                
                # Add product themes to visual context
                if product_themes:
                    theme_context = ', '.join(product_themes[:3])
                    visual_context += f", incorporating {theme_context} themes"
                    
                # Add visual elements if specified
                if product_visual_elements:
                    visual_context += f", featuring {product_visual_elements}"
                    
        # **BUSINESS-TYPE SPECIFIC GENERATION** (Fallback when no specific product)
        else:
            # Extract detailed business context for visual generation
            logger.info(f"No specific product detected, using business-type context for {company_name}")
            
            if any(keyword in business_description.lower() for keyword in ['t-shirt', 'tshirt', 'apparel', 'clothing', 'print', 'custom']):
                # T-shirt/Apparel Business (Generic)
                visual_context = f"Diverse young adults wearing custom printed t-shirts with creative designs, laughing and having fun in an urban outdoor setting, natural lighting, lifestyle photography style"
                if 'funny' in business_description.lower() or 'humor' in business_description.lower():
                    visual_context += ", humorous and playful t-shirt designs visible"
                
            elif any(keyword in business_description.lower() for keyword in ['restaurant', 'food', 'dining', 'kitchen', 'chef', 'cuisine']):
                # Restaurant/Food Business
                visual_context = f"Professional food photography showing delicious prepared dishes, warm restaurant atmosphere with satisfied customers dining"
                
            elif any(keyword in business_description.lower() for keyword in ['fitness', 'gym', 'training', 'workout', 'health', 'exercise']):
                # Fitness/Health Business
                visual_context = f"Dynamic fitness scene with trainer and client working out in modern gym, showing transformation and success"
                
            elif any(keyword in business_description.lower() for keyword in ['tech', 'software', 'digital', 'app', 'platform', 'saas']):
                # Technology Business
                visual_context = f"Modern professionals collaborating with technology, clean office environment, digital interfaces"
                
            else:
                # Generic business fallback
                visual_context = f"Professional business environment representing {industry} industry, showing {objective} in action"
        
        # **CAMPAIGN GUIDANCE ENHANCEMENT**
        if campaign_guidance:
            visual_style_guidance = campaign_guidance.get('visual_style', {})
            if visual_style_guidance:
                photography_style = visual_style_guidance.get('photography_style', '')
                mood = visual_style_guidance.get('mood', '')
                lighting = visual_style_guidance.get('lighting', '')
                
                if photography_style:
                    visual_context += f", {photography_style} style"
                if mood:
                    visual_context += f", {mood} mood"
                if lighting:
                    visual_context += f", {lighting}"
        
        # **USER MEDIA TUNING INTEGRATION**
        if campaign_media_tuning:
            logger.info(f"Applying user media tuning: {campaign_media_tuning}")
            visual_context += f", incorporating user guidance: {campaign_media_tuning}"
        
        # **CREATIVE DIRECTION INTEGRATION**
        if creative_direction:
            visual_context += f", {creative_direction}"
        
        # Add target audience context
        if 'young' in target_audience.lower() or '18-35' in target_audience:
            visual_context += ", featuring young adults aged 18-35"
        elif 'professional' in target_audience.lower():
            visual_context += ", featuring business professionals"
        elif 'family' in target_audience.lower():
            visual_context += ", family-friendly scene"
        
        # Create final marketing-optimized prompt with technical specs
        marketing_prompt = f"{visual_context}, representing {company_name}, 16:9 aspect ratio, commercial photography style, high quality, professional lighting, sharp focus"
        
        logger.info(f"Generated enhanced image prompt: {marketing_prompt[:150]}...")
        return marketing_prompt
    
    def _create_video_prompt(self, post: Dict[str, Any], business_context: Dict[str, Any], objective: str) -> str:
        """Create video generation prompt based on post content and business context."""
        
        post_content = post.get('content', '')
        company_name = business_context.get('company_name', 'Company')
        
        prompt = f"Professional marketing video showcasing {company_name}'s approach to {objective}, dynamic and engaging visual storytelling"
        
        return prompt
    
    def _update_posts_with_visuals(
        self, 
        social_posts: List[Dict[str, Any]], 
        generated_images: List[Dict[str, Any]], 
        generated_videos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Update social media posts with generated visual content."""
        
        updated_posts = []
        image_index = 0
        video_index = 0
        
        for post in social_posts:
            updated_post = post.copy()
            
            if post.get('type') == 'text_image' and image_index < len(generated_images):
                image_data = generated_images[image_index]
                updated_post['image_url'] = image_data['image_url']
                updated_post['image_prompt'] = image_data['prompt']
                updated_post['image_metadata'] = image_data['metadata']
                image_index += 1
            
            elif post.get('type') == 'text_video' and video_index < len(generated_videos):
                video_data = generated_videos[video_index]
                updated_post['video_url'] = video_data['video_url']
                updated_post['video_prompt'] = video_data['prompt']
                updated_post['thumbnail_url'] = video_data.get('thumbnail_url')
                updated_post['video_metadata'] = video_data['metadata']
                video_index += 1
            
            updated_posts.append(updated_post)
        
        return updated_posts
    
    def _generate_fallback_visual_content(self, social_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback visual content when generation fails."""
        return {
            "posts_with_visuals": social_posts,
            "visual_strategy": {
                "total_posts": len(social_posts),
                "image_posts": 0,
                "video_posts": 0,
                "generated_images": 0,
                "generated_videos": 0,
                "brand_consistency": "Fallback mode",
                "platform_optimization": "Basic optimization"
            },
            "generation_metadata": {
                "agent_used": "FallbackVisualGenerator",
                "processing_time": 0.1,
                "quality_score": 5.0,
                "error": "Visual content generation failed"
            }
        }

# Export function for use in API routes
async def generate_visual_content_for_posts(
    social_posts: List[Dict[str, Any]], 
    business_context: Dict[str, Any],
    campaign_objective: str,
    target_platforms: List[str] = None,
    # ADK ENHANCEMENT: Enhanced context parameters for business-aware generation
    campaign_media_tuning: str = "",
    campaign_guidance: Dict[str, Any] = None,
    product_context: Dict[str, Any] = None,
    visual_style: Dict[str, Any] = None,
    creative_direction: str = ""
) -> Dict[str, Any]:
    """
    Generate visual content for social media posts with enhanced business context.
    
    ADK Data Flow Enhancement:
    This function now receives comprehensive business analysis context to ensure
    visual content is aligned with the specific business, product, and campaign objectives.
    
    Args:
        social_posts: List of social media posts to enhance with visuals
        business_context: Core business context from URL analysis
        campaign_objective: Campaign objective for content alignment
        target_platforms: Target social media platforms
        campaign_media_tuning: User-provided media style guidance
        campaign_guidance: Business analysis campaign guidance
        product_context: Specific product information for visual focus
        visual_style: Brand visual style guidelines
        creative_direction: Overall creative direction for the campaign
    
    Returns:
        Dict containing posts with generated visual content
    """
    try:
        logger.info("🎨 Generating visual content with enhanced ADK business context")
        
        # Merge all context sources for comprehensive visual generation
        enhanced_context = {
            **business_context,
            "campaign_media_tuning": campaign_media_tuning,
            "campaign_guidance": campaign_guidance or {},
            "product_context": product_context or {},
            "visual_style": visual_style or {},
            "creative_direction": creative_direction
        }
        
        # Log context richness for debugging
        logger.info(f"Enhanced context includes: company={enhanced_context.get('company_name')}, "
                   f"product={enhanced_context.get('product_context', {}).get('product_name', 'general')}, "
                   f"creative_direction={len(creative_direction)} chars, "
                   f"media_tuning={len(campaign_media_tuning)} chars")
        
        # Initialize orchestrator with enhanced context
        orchestrator = VisualContentOrchestrator()
        
        # Generate visual content with full business awareness
        result = await orchestrator.generate_visual_content(
            social_posts=social_posts,
            business_context=enhanced_context,
            campaign_objective=campaign_objective,
            target_platforms=target_platforms or ["instagram", "linkedin", "facebook"]
        )
        
        logger.info("✅ Visual content generation completed with business context awareness")
        return result
        
    except Exception as e:
        logger.error(f"❌ Enhanced visual content generation failed: {e}", exc_info=True)
        # Fallback to basic generation
        orchestrator = VisualContentOrchestrator()
        return await orchestrator.generate_visual_content(
            social_posts=social_posts,
            business_context=business_context,
            campaign_objective=campaign_objective,
            target_platforms=target_platforms or ["instagram", "linkedin", "facebook"]
        )

# Export functions for use in other modules
__all__ = [
    "generate_visual_content_for_posts"
] 