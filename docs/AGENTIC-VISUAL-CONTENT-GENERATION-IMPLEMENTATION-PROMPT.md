# AGENTIC VISUAL CONTENT GENERATION - IMPLEMENTATION PROMPT

**Date**: 2025-06-25  
**Author**: JP + Claude Sonnet  
**Context**: Google ADK Hackathon - Production-Ready Implementation  
**Priority**: Critical - Hackathon Submission Requirement  
**Compliance**: ADR-019, ADR-015, ADR-014, ADR-013  

## MISSION: IMPLEMENT TRULY AGENTIC VISUAL CONTENT GENERATION

You are implementing a **production-ready, autonomous visual content generation system** that creates real images and videos for ANY business type, product, or service. The system must be **completely dynamic** and work for diverse marketing campaigns across different industries.

## CRITICAL PROBLEM ANALYSIS

### Current System Failures:
- ❌ **No actual files generated** - URLs return 404/405 errors
- ❌ **0KB placeholder content** - Frontend shows empty placeholders
- ❌ **Non-agentic implementation** - Simple API wrappers, not ADK agents
- ❌ **No validation or self-correction** - System doesn't verify success
- ❌ **Missing campaign context integration** - Ignores business analysis

### Required Solution:
- ✅ **Real file generation** - Actual PNG/MP4 files on filesystem
- ✅ **Working HTTP endpoints** - Serve content via proper URLs
- ✅ **True ADK agentic framework** - LlmAgent and SequentialAgent
- ✅ **Autonomous validation** - Self-correction and quality assurance
- ✅ **Dynamic campaign context** - Works for ANY business/product/service

## DYNAMIC CAMPAIGN CONTEXT ARCHITECTURE

### VARIABLE BUSINESS CONTEXTS (Not Hardcoded)

The system must dynamically handle **any business type**:

```python
# Example 1: Photography Business
business_context = {
    "company_name": "Liat Victoria Photography",
    "industry": "Family Photography Services", 
    "business_description": "Professional family photography capturing milestones",
    "product_context": {
        "has_specific_product": True,
        "product_name": "Pro Family Photoshoot",
        "product_themes": ["family", "milestones", "memories", "joy"],
        "product_visual_elements": "natural family interactions, outdoor settings"
    },
    "campaign_guidance": {
        "creative_direction": "warm, natural family moments with authentic emotions",
        "visual_style": {
            "photography_style": "lifestyle", 
            "mood": "warm and inviting",
            "color_palette": "natural tones"
        },
        "media_tuning": "bright outdoor lighting, natural poses, authentic expressions"
    },
    "business_website": "https://www.liatvictoriaphotography.co.uk",
    "target_audience": "families with young children, milestone celebrations"
}

# Example 2: Custom T-Shirt Business  
business_context = {
    "company_name": "illustraMan Custom Tees",
    "industry": "Custom Apparel Design",
    "business_description": "Creative custom t-shirt designs with pop culture themes", 
    "product_context": {
        "has_specific_product": True,
        "product_name": "The Joker - Why Aren't You Laughing T-shirt",
        "product_themes": ["humor", "pop culture", "comic book", "artistic"],
        "product_visual_elements": "bold graphic design, comic aesthetics"
    },
    "campaign_guidance": {
        "creative_direction": "playful, artistic, pop culture focused with humor elements",
        "visual_style": {
            "photography_style": "urban lifestyle",
            "mood": "fun and energetic", 
            "color_palette": "vibrant, contrasting"
        },
        "media_tuning": "urban outdoor settings, people wearing shirts, laughing"
    },
    "target_audience": "young adults, comic book fans, humor enthusiasts"
}

# Example 3: Technology Consulting
business_context = {
    "company_name": "TechSolutions Pro",
    "industry": "Technology Consulting Services",
    "business_description": "Digital transformation consulting for enterprises",
    "product_context": {
        "has_specific_product": False,  # Service-based, not product-specific
        "service_categories": ["digital transformation", "cloud migration", "AI integration"],
        "value_propositions": ["efficiency", "innovation", "scalability"]
    },
    "campaign_guidance": {
        "creative_direction": "professional, innovative, technology-forward messaging",
        "visual_style": {
            "photography_style": "corporate professional",
            "mood": "confident and forward-thinking",
            "color_palette": "modern blues and grays"
        },
        "media_tuning": "modern office environments, technology in use, professional teams"
    },
    "target_audience": "enterprise decision makers, CTOs, digital transformation leaders"
}
```

### DYNAMIC CONTEXT EXTRACTION LOGIC

The agents must **intelligently extract and apply** context:

```python
class BusinessContextAnalyzer:
    """Dynamically analyzes business context for any industry/product/service."""
    
    def extract_visual_context(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract visual context that works for ANY business type."""
        
        # DYNAMIC INDUSTRY DETECTION (Not Hardcoded)
        industry = business_context.get('industry', '').lower()
        business_description = business_context.get('business_description', '').lower()
        
        # PRIORITY 1: Specific Product Context (If Available)
        product_context = business_context.get('product_context', {})
        if product_context.get('has_specific_product', False):
            return self._extract_product_specific_context(product_context, business_context)
        
        # PRIORITY 2: Service Category Context
        elif 'service_categories' in product_context:
            return self._extract_service_specific_context(product_context, business_context)
        
        # PRIORITY 3: Industry Pattern Detection
        else:
            return self._extract_industry_pattern_context(industry, business_description, business_context)
    
    def _extract_product_specific_context(self, product_context, business_context):
        """Handle specific product marketing (t-shirts, photoshoots, etc.)."""
        product_name = product_context.get('product_name', '')
        product_themes = product_context.get('product_themes', [])
        visual_elements = product_context.get('product_visual_elements', '')
        
        # Dynamic context based on actual product
        return {
            "primary_focus": f"person using/wearing/experiencing {product_name}",
            "visual_themes": product_themes,
            "specific_elements": visual_elements,
            "context_type": "product_specific"
        }
    
    def _extract_industry_pattern_context(self, industry, description, business_context):
        """Handle general business/service marketing."""
        
        # DYNAMIC PATTERN MATCHING (Extensible)
        if any(keyword in description for keyword in ['photo', 'photography', 'portrait']):
            return {
                "primary_focus": "professional photography service demonstration",
                "visual_themes": ["quality", "professionalism", "results"],
                "context_type": "photography_service"
            }
        elif any(keyword in description for keyword in ['tech', 'software', 'digital', 'consulting']):
            return {
                "primary_focus": "modern technology solutions in professional environment", 
                "visual_themes": ["innovation", "efficiency", "professionalism"],
                "context_type": "technology_service"
            }
        elif any(keyword in description for keyword in ['food', 'restaurant', 'dining', 'cuisine']):
            return {
                "primary_focus": "culinary excellence and dining experience",
                "visual_themes": ["quality", "taste", "atmosphere"],
                "context_type": "food_service"
            }
        # ADD MORE PATTERNS AS NEEDED - SYSTEM IS EXTENSIBLE
        else:
            return {
                "primary_focus": f"professional {industry} service delivery",
                "visual_themes": ["quality", "professionalism", "results"],
                "context_type": "general_business"
            }
```

## AGENTIC IMPLEMENTATION ARCHITECTURE

### 1. IMAGE GENERATION AGENT (ADK LlmAgent)

```python
class ImageGenerationAgent(LlmAgent):
    """Autonomous image generation with dynamic campaign context integration."""
    
    def __init__(self):
        super().__init__(
            name="ImageGenerationAgent",
            model=Gemini(model_name="gemini-2.5-flash", api_key=GEMINI_API_KEY),
            instruction="""You are an autonomous image generation agent specializing in marketing visuals.
            
Your capabilities:
1. Analyze post content and extract visual requirements
2. Integrate comprehensive business context dynamically
3. Create contextually relevant image prompts
4. Generate images using Google Imagen 3.0
5. Validate image quality and campaign alignment
6. Self-correct if validation fails
7. Cache successful results for efficiency

CRITICAL: You work with ANY business type - photography, t-shirts, consulting, restaurants, etc.
Your prompts must be dynamically created based on the specific business context provided.
            """,
            tools=[self._create_contextual_image_prompt, self._generate_imagen_content, self._validate_image_quality]
        )
        
        self.imagen_client = self._initialize_imagen_client()
        self.cache = CampaignImageCache()
        self.validator = VisualContentValidationTool()
    
    async def generate_and_validate_image(
        self, 
        post_content: str,
        campaign_guidance: Dict[str, Any],
        business_context: Dict[str, Any],
        campaign_id: str,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """Autonomously generate and validate image with self-correction."""
        
        for iteration in range(max_iterations):
            try:
                # STEP 1: Dynamic prompt creation based on ANY business context
                enhanced_prompt = await self._create_contextual_image_prompt(
                    post_content, campaign_guidance, business_context
                )
                
                # STEP 2: Check cache first (efficiency)
                cached_image = self.cache.get_cached_image(enhanced_prompt, "imagen-3.0", campaign_id)
                if cached_image:
                    return await self._validate_cached_image(cached_image, post_content, campaign_guidance)
                
                # STEP 3: Generate real image using Imagen 3.0
                generation_result = await self._generate_imagen_content(enhanced_prompt, campaign_id)
                
                # STEP 4: Download and store actual image file
                if generation_result.get("success"):
                    image_url = await self._save_image_to_filesystem(generation_result, campaign_id)
                    
                    # STEP 5: Autonomous validation
                    validation_result = await self.validator.validate_image_content(
                        image_url, post_content, campaign_guidance, business_context
                    )
                    
                    # STEP 6: Self-correction or success
                    if validation_result.get("valid", False):
                        self.cache.cache_image(enhanced_prompt, "imagen-3.0", campaign_id, image_url, is_current=True)
                        return {
                            "success": True,
                            "image_url": image_url,
                            "prompt": enhanced_prompt,
                            "validation_score": validation_result.get("score", 0.8),
                            "iteration": iteration + 1
                        }
                    else:
                        # Self-correction: Learn from validation feedback
                        logger.warning(f"Image validation failed (iteration {iteration + 1}): {validation_result.get('issues')}")
                        continue
                        
            except Exception as e:
                logger.error(f"Image generation iteration {iteration + 1} failed: {e}")
                continue
        
        # Fallback after max iterations
        return await self._generate_fallback_image(post_content, business_context, campaign_id)
    
    def _create_contextual_image_prompt(
        self, 
        post_content: str, 
        campaign_guidance: Dict[str, Any], 
        business_context: Dict[str, Any]
    ) -> str:
        """Create dynamic image prompt for ANY business type."""
        
        # Extract dynamic context (works for any business)
        company_name = business_context.get('company_name', 'Company')
        industry = business_context.get('industry', 'business')
        
        # DYNAMIC CONTEXT ANALYSIS
        context_analyzer = BusinessContextAnalyzer()
        visual_context = context_analyzer.extract_visual_context(business_context)
        
        # CAMPAIGN GUIDANCE INTEGRATION (Dynamic)
        creative_direction = campaign_guidance.get('creative_direction', '')
        visual_style = campaign_guidance.get('visual_style', {})
        media_tuning = campaign_guidance.get('media_tuning', '')
        
        # BUILD PROMPT DYNAMICALLY
        base_prompt = f"Professional marketing image for {company_name}: {post_content[:100]}"
        
        # Add visual context based on business type
        enhanced_prompt = f"{base_prompt}. {visual_context['primary_focus']}"
        
        # Add campaign guidance
        if creative_direction:
            enhanced_prompt += f", incorporating {creative_direction}"
        
        # Add visual style preferences  
        if visual_style.get('photography_style'):
            enhanced_prompt += f", {visual_style['photography_style']} photography style"
        if visual_style.get('mood'):
            enhanced_prompt += f", {visual_style['mood']} mood"
        
        # Add media tuning overrides
        if media_tuning:
            enhanced_prompt += f", with specific guidance: {media_tuning}"
        
        # Add quality specifications
        enhanced_prompt += ", high quality professional marketing image, engaging composition, brand-aligned"
        
        return enhanced_prompt
```

### 2. VIDEO GENERATION AGENT (ADK LlmAgent)

```python
class VideoGenerationAgent(LlmAgent):
    """Autonomous video generation with dynamic campaign context integration."""
    
    async def generate_and_validate_video(
        self, 
        post_content: str,
        campaign_guidance: Dict[str, Any],
        business_context: Dict[str, Any],
        campaign_id: str,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """Autonomously generate and validate video with self-correction."""
        
        # Similar structure to ImageGenerationAgent but for videos
        # Creates 5-second MP4 files using Google Veo 2.0
        # Stores in data/videos/generated/{campaign_id}/curr_{hash}_{index}.mp4
        # Validates video quality and campaign alignment
        # Self-corrects based on validation feedback
```

### 3. VISUAL CONTENT ORCHESTRATOR (ADK SequentialAgent)

```python
class VisualContentOrchestratorAgent(SequentialAgent):
    """Coordinates autonomous visual content generation with parallel processing."""
    
    def __init__(self):
        self.image_agent = ImageGenerationAgent()
        self.video_agent = VideoGenerationAgent()
        
        super().__init__(
            name="VisualContentOrchestratorAgent", 
            sub_agents=[self.image_agent, self.video_agent],
            description="Orchestrates autonomous visual content generation with validation"
        )
    
    async def generate_visual_content_for_posts(
        self,
        social_posts: List[Dict[str, Any]],
        business_context: Dict[str, Any],
        campaign_guidance: Dict[str, Any],
        campaign_id: str
    ) -> Dict[str, Any]:
        """Generate visual content for ANY business type with autonomous validation."""
        
        results = {
            "posts_with_visuals": [],
            "generation_metadata": {
                "agent_used": "VisualContentOrchestratorAgent",
                "business_type": business_context.get('industry', 'general'),
                "campaign_context_applied": True,
                "autonomous_validation": True
            }
        }
        
        # Process each post with parallel agent coordination
        for post in social_posts:
            post_type = post.get('type', 'text_url')
            
            # Determine visual requirements
            needs_image = post_type in ['text_image', 'image']
            needs_video = post_type in ['text_video', 'video'] 
            
            # Coordinate autonomous agents
            tasks = []
            if needs_image:
                tasks.append(self.image_agent.generate_and_validate_image(
                    post.get('content', ''), campaign_guidance, business_context, campaign_id
                ))
            if needs_video:
                tasks.append(self.video_agent.generate_and_validate_video(
                    post.get('content', ''), campaign_guidance, business_context, campaign_id  
                ))
            
            # Execute in parallel with error handling
            if tasks:
                task_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results and update post
                for result in task_results:
                    if isinstance(result, dict) and result.get('success'):
                        if 'image_url' in result:
                            post['image_url'] = result['image_url']
                            post['image_prompt'] = result.get('prompt')
                        elif 'video_url' in result:
                            post['video_url'] = result['video_url'] 
                            post['video_prompt'] = result.get('prompt')
                    else:
                        # Handle failures gracefully
                        error_msg = str(result) if isinstance(result, Exception) else result.get('error', 'Unknown error')
                        post['error'] = f"Visual generation failed: {error_msg}"
            
            results['posts_with_visuals'].append(post)
        
        return results
```

## DYNAMIC FILESYSTEM STORAGE

### Directory Structure (Campaign-Specific)

```bash
data/
├── images/
│   ├── generated/
│   │   └── {campaign_id}/           # Dynamic campaign ID
│   │       ├── curr_{hash}_0.png    # Current image files
│   │       ├── curr_{hash}_1.png    # Multiple images per campaign
│   │       └── curr_{hash}_2.png
│   └── cache/
│       └── {campaign_id}/           # Campaign-specific cache
│           ├── curr_{hash}.json     # Current image cache metadata
│           └── {hash}.json          # Historical cache
└── videos/
    ├── generated/
    │   └── {campaign_id}/           # Dynamic campaign ID  
    │       ├── curr_{hash}_0.mp4    # Current video files (5-second MP4s)
    │       ├── curr_{hash}_1.mp4    # Multiple videos per campaign
    │       └── curr_{hash}_2.mp4
    └── cache/
        └── {campaign_id}/           # Campaign-specific cache
            ├── curr_{hash}.json     # Current video cache metadata
            └── {hash}.json          # Historical cache
```

## VALIDATION AND TESTING REQUIREMENTS

### 1. Filesystem Validation
```bash
# These commands MUST succeed after implementation:
ls -la data/images/generated/{campaign_id}/     # Shows actual PNG files
ls -la data/videos/generated/{campaign_id}/     # Shows actual MP4 files
file data/images/generated/{campaign_id}/*.png  # Confirms PNG format and size > 0
file data/videos/generated/{campaign_id}/*.mp4  # Confirms MP4 format and size > 500KB
```

### 2. HTTP Endpoint Testing
```bash
# These MUST return HTTP 200 with actual content:
curl -I http://localhost:8000/api/v1/content/images/{campaign_id}/{filename}
curl -I http://localhost:8000/api/v1/content/videos/{campaign_id}/{filename}
```

### 3. Dynamic Business Context Testing

Test with multiple business types:
- Photography Business (Liat Victoria Photography)
- Custom T-Shirt Business (illustraMan)
- Technology Consulting (TechSolutions Pro)
- Restaurant Business
- Each should generate contextually appropriate visuals

## SUCCESS CRITERIA

### Technical Requirements ✅
- [ ] Real PNG/MP4 files generated on filesystem
- [ ] Working HTTP endpoints serving actual content  
- [ ] True ADK LlmAgent and SequentialAgent implementation
- [ ] Autonomous validation and self-correction
- [ ] Dynamic campaign context integration (any business type)
- [ ] Error handling and graceful fallbacks

### User Experience Requirements ✅
- [ ] Images display correctly in frontend
- [ ] Videos are playable with controls
- [ ] No 0KB placeholders or broken links
- [ ] Realistic file sizes (images >50KB, videos >500KB)
- [ ] Fast loading with proper caching

## DELIVERABLE

A **production-ready, autonomous visual content generation system** that works for ANY business type with automatically generated, contextually appropriate visual content that aligns with their specific business objectives and creative vision.

---

**Author**: JP + 2025-06-25  
**Implementation Note**: This system is designed to be **completely flexible and extensible** for any business type, product, or service. 