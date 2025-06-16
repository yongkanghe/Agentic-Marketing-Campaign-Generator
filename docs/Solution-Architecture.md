## Visual Content Generation Architecture

### Imagen 3.0 Integration Strategy

The visual content generation system leverages Google Imagen 3.0 with sophisticated business context awareness:

#### Context-Aware Image Generation Pipeline
```
Business Context Input → Industry Analysis → Contextual Prompt Engineering → Imagen API → Storage Management → Frontend Display
```

#### Key Components:

1. **ContextAwareImagePromptBuilder**
   - Extracts industry-specific visual elements
   - Applies brand voice to visual style
   - Integrates campaign objectives
   - Optimizes for platform specifications (16:9 for Twitter/X)

2. **Visual Content Agent** (`backend/agents/visual_content_agent.py`)
   ```python
   class ImageGenerationAgent:
       def __init__(self):
           self.image_model = os.getenv('IMAGE_MODEL', 'imagen-3.0-generate-001')
           self.max_images = int(os.getenv('MAX_TEXT_IMAGE_POSTS', '4'))
       
       async def generate_images(self, prompts, business_context):
           # Context-aware generation with cost controls
           pass
   ```

3. **Storage Strategy**
   - **Local Development**: Temporary file storage with placeholder URLs
   - **Production**: Google Cloud Storage + CDN integration
   
#### Industry-Specific Prompt Engineering

**T-Shirt Printing Business Example:**
```python
business_context = {
    "company_name": "CustomTee Pro",
    "business_description": "Custom t-shirt printing with funny designs", 
    "target_audience": "young adults 18-35"
}

# Generated prompt:
"Professional marketing photography of diverse young adults wearing 
custom t-shirts with humorous designs, laughing in urban setting,
16:9 aspect ratio, commercial photography style"
```

**Restaurant Business Example:**
```python
business_context = {
    "company_name": "Mama's Kitchen",
    "business_description": "Italian family restaurant, authentic recipes"
}

# Generated prompt:  
"Warm Italian restaurant scene with family dining, authentic pasta dishes,
rustic decor, professional food photography, 16:9 optimized"
```

### Production Architecture Roadmap

#### Phase 1: Local Development (Current)
```yaml
Image Generation:
  - Enhanced placeholders: Picsum Photos (1024x576, 16:9)
  - Context-aware prompts: Business description integrated
  - Cost controls: 4 image maximum per generation
  - Platform optimization: Twitter/X primary focus

Storage:
  - Local temporary files
  - Placeholder URL generation
  - Development-friendly setup
```

#### Phase 2: Imagen API Integration 
```yaml
Image Generation:
  - Real Imagen 3.0 API calls
  - Enhanced prompt engineering with business context
  - Safety filters and quality controls
  - Error handling with graceful fallbacks

Storage:
  - Local temporary file management
  - Context-aware file naming
  - Automatic cleanup processes
```

#### Phase 3: Production Cloud Deployment
```yaml
Image Generation:
  - Scalable Imagen API integration
  - Advanced context analysis
  - A/B testing for prompt effectiveness

Storage:
  - Google Cloud Storage integration
  - CloudFlare CDN for global delivery
  - Hierarchical storage: campaigns/{company}/{date}/{image_id}
  - Metadata: company, objective, model, timestamp
  - Cache optimization: 1 year cache headers

Monitoring:
  - Generation success rates by industry
  - Cost per image and ROI tracking
  - User engagement with generated images
  - Performance monitoring and alerting
```

### Technical Implementation Details

#### Business Context Schema
```python
@dataclass
class VisualGenerationContext:
    company_name: str
    business_description: str
    industry: str
    product_service_url: Optional[str]
    target_audience: str
    brand_voice: str
    campaign_objective: str
    platform: str = "twitter"  # Primary optimization
    
    def to_prompt_context(self) -> dict:
        return {
            "industry_keywords": self.extract_industry_keywords(),
            "visual_style": self.determine_visual_style(),
            "brand_elements": self.extract_brand_elements(),
            "platform_specs": PLATFORM_SPECS[self.platform]
        }
```

#### Cost Management Strategy
```python
# Environment-based cost controls
MAX_TEXT_IMAGE_POSTS = int(os.getenv('MAX_TEXT_IMAGE_POSTS', '4'))
DAILY_IMAGE_GENERATIONS = int(os.getenv('DAILY_IMAGE_GENERATIONS', '100'))

# Rate limiting per company
@rate_limit(requests=10, window=3600)  # 10 images per hour per company
async def generate_company_images(company_id, prompts):
    pass
```

#### Quality Assurance Pipeline
```python
# Multi-layer content safety
imagen_config = {
    "safety_filter_level": "block_few",    # Marketing content flexibility
    "person_generation": "allow_adult",    # Professional contexts
    "aspect_ratio": "16:9",               # Social media optimization
    "negative_prompt": "blurry, low quality, unprofessional, amateur"
}
```

### Integration with Marketing Workflow

#### Content Generation Flow
1. **Business Analysis**: Extract visual context from company description
2. **Industry Classification**: Apply industry-specific prompt templates
3. **Objective Alignment**: Match visual concepts to campaign goals
4. **Platform Optimization**: Apply platform-specific requirements
5. **Quality Control**: Ensure brand-safe, professional output
6. **Storage & Delivery**: Manage generated assets efficiently

#### Frontend Integration
```typescript
// Enhanced image display with context awareness
interface GeneratedImage {
  id: string;
  image_url: string;
  enhanced_prompt: string;
  business_context_applied: boolean;
  platform_optimized: string;
  generation_metadata: {
    model: string;
    company: string;
    objective: string;
    industry_keywords: string[];
  };
}
```

This architecture provides a sophisticated foundation for context-aware marketing image generation while maintaining cost efficiency and production scalability. 