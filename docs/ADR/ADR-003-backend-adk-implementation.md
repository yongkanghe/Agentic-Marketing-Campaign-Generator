# ADR-003: Backend ADK Sequential Agent Implementation

**Date**: 2025-06-15  
**Status**: Accepted  
**Author**: JP  

## Context

The AI Marketing Campaign Post Generator project required a backend API service to replace the mocked AI functionality in the frontend. The backend needed to integrate with Google's ADK (Agent Development Kit) to provide real AI-powered marketing campaign generation capabilities.

## Decision

We implemented a comprehensive backend API service using FastAPI with ADK sequential agent integration, following Google ADK samples best practices.

### Architecture Components

1. **FastAPI Application Structure**
   - `backend/api/main.py` - Application entry point with CORS and middleware
   - `backend/api/models.py` - Pydantic models for request/response validation
   - `backend/api/routes/` - Modular route organization

2. **ADK Sequential Agent Hierarchy**
   - **MarketingOrchestratorAgent** (Root Sequential Agent)
     - **BusinessAnalysisAgent** (Sequential)
       - URLAnalysisAgent (LLM)
       - FileAnalysisAgent (LLM)
       - BusinessContextAgent (LLM)
     - **ContentGenerationAgent** (Sequential)
       - SocialContentAgent (LLM)
       - HashtagOptimizationAgent (LLM)

### Agent Relationship Diagram
```ascii
[ MarketingOrchestratorAgent (Sequential Root) ]
    |
    |--- 1. [ BusinessAnalysisAgent (Sequential) ]
    |         |
    |         |--- 1a. [ URLAnalysisAgent (LLM) ]
    |         |         (Input: URLs; Output: url_analysis)
    |         |
    |         |--- 1b. [ FileAnalysisAgent (LLM) ]
    |         |         (Input: Uploaded files; Output: file_analysis)
    |         |
    |         |--- 1c. [ BusinessContextAgent (LLM) ]
    |                   (Input: url_analysis, file_analysis, user_input, etc.;
    |                    Output: business_context with detailed visual direction)
    |
    |--- 2. [ ContentGenerationAgent (Sequential) ]
              |
              |--- 2a. [ SocialContentAgent (LLM) ]
              |         (Input: business_context, objective, etc.;
              |          Output: social_content including text & prompts for images/videos)
              |
              |--- 2b. [ HashtagOptimizationAgent (LLM) ]
                        (Input: business_context, social_content;
                         Output: hashtag_optimization)

---------------------------------------------------------------------
Separate, but invoked by API layer using outputs from above:

[ VisualContentOrchestrator ]
    |
    |--- [ ImageGenerationAgent ]
    |     (Input: Image prompts from SocialContentAgent output, business_context;
    |      Output: Generated images (real via Imagen or placeholders))
    |
    |--- [ VideoGenerationAgent ]
          (Input: Video prompts from SocialContentAgent output, business_context;
           Output: Mocked video data)
---------------------------------------------------------------------
```

3. **API Endpoints**
   - `POST /api/v1/campaigns/create` - Enhanced campaign creation
   - `POST /api/v1/analysis/url` - Business URL analysis
   - `POST /api/v1/analysis/files` - File upload and analysis
   - `POST /api/v1/content/generate` - Social media content generation
   - `POST /api/v1/content/regenerate` - Post regeneration

### Key Implementation Decisions

#### 1. Sequential Agent Pattern
- **Rationale**: Ensures proper context flow between analysis and generation phases
- **Benefits**: Maintainable, traceable, and follows ADK best practices
- **Trade-offs**: Sequential execution may be slower than parallel, but ensures quality

#### 2. Comprehensive Business Analysis
- **URL Analysis**: Web scraping and content extraction for business intelligence
- **File Analysis**: Multimodal processing of images, documents, and campaign assets
- **Context Synthesis**: Unified business profile for consistent content generation

#### 3. Multi-Format Content Generation
- **Text + URL Posts**: Product/service link integration
- **Text + Image Posts**: AI-generated visual concepts with detailed prompts. Actual image generation via Imagen API is attempted if `GEMINI_API_KEY` is available, with fallbacks to placeholders upon API error. Note: `ImageGenerationAgent` initialization fails if the API key is absent at startup.
- **Text + Video Posts**: AI-generated video concepts and storyboard descriptions. Actual video generation via Veo API is currently mocked; the system does not yet integrate with a live Veo service.

#### 4. Platform Optimization
- **Cross-Platform Content**: LinkedIn, Twitter/X, Instagram, Facebook, TikTok
- **Hashtag Strategy**: Trending, niche, and brand-specific hashtag optimization
- **Engagement Prediction**: AI-powered engagement scoring

## Implementation Details

### Agent Configuration
```python
# Model configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Sequential agent creation with proper context flow
orchestrator = SequentialAgent(
    name="MarketingOrchestratorAgent",
    sub_agents=[business_agent, content_agent],
    instruction="Master orchestrator for complete marketing campaign workflow"
)
```

### API Integration
```python
# FastAPI route with ADK integration
@router.post("/create", response_model=CampaignResponse)
async def create_campaign(request: CampaignRequest) -> CampaignResponse:
    workflow_result = await execute_campaign_workflow(
        business_description=request.business_description,
        objective=request.objective,
        # ... other parameters
    )
    return CampaignResponse(**workflow_result)
```

### Mock vs Real Implementation
- **Development Mode**: Mock responses when GEMINI_API_KEY not configured
- **Production Mode**: Real ADK agent execution with Gemini integration for text-based analysis and content. Image generation is attempted with Imagen API if configured, otherwise uses fallbacks. Video generation is mocked.
- **Graceful Fallback**: Comprehensive error handling and logging

## Consequences

### Positive
- **Complete Backend API**: Fully functional FastAPI service ready for frontend integration
- **ADK Best Practices**: Follows Google ADK samples patterns for maintainability
- **Comprehensive Workflow**: End-to-end campaign creation from analysis to content generation
- **Scalable Architecture**: Sequential agents can be easily extended or modified
- **Type Safety**: Pydantic models ensure API contract validation
- **Development Ready**: Mock mode and fallbacks enable development without API keys for most features, though `ImageGenerationAgent` will raise an error on initialization if `GEMINI_API_KEY` is missing.

### Negative
- **Sequential Execution**: May be slower than parallel processing for some operations
- **Complexity**: Multiple agent layers require careful state management
- **Resource Usage**: Multiple LLM calls per campaign creation
- **API Key Dependency**: Requires GEMINI_API_KEY for full functionality

### Neutral
- **Learning Curve**: Developers need to understand ADK patterns
- **Testing Strategy**: Requires both unit and integration testing approaches
- **Documentation Maintenance**: Complex architecture needs comprehensive documentation

## Alternatives Considered

### 1. Simple FastAPI with Direct Gemini Calls
- **Pros**: Simpler implementation, faster execution
- **Cons**: Less maintainable, harder to extend, no context flow management

### 2. Parallel Agent Execution
- **Pros**: Faster execution, better resource utilization
- **Cons**: Complex state management, potential context loss between agents

### 3. Microservices Architecture
- **Pros**: Better scalability, service isolation
- **Cons**: Increased complexity, deployment overhead for POC stage

## Implementation Status

- ✅ **FastAPI Application**: Complete with CORS, middleware, and error handling
- ✅ **Pydantic Models**: Comprehensive request/response validation
- ✅ **ADK Agent Hierarchy**: Full sequential agent implementation
- ✅ **API Routes**: Campaign, content, and analysis endpoints
- ✅ **Mock Implementation**: Development-ready with fallback responses
- ✅ **Documentation**: Comprehensive code documentation and ADR
- ⏳ **Frontend Integration**: Next step - connect React frontend to API
- ⏳ **Real AI Testing**: Required for text analysis/generation and image generation (conditional on `GEMINI_API_KEY`). Video generation uses mock data.
- ⏳ **Production Deployment**: Cloud Run deployment configuration needed

## Next Steps

1. **Frontend Integration**: Update MarketingContext to use real API endpoints
2. **Environment Setup**: Configure GEMINI_API_KEY for real AI testing
3. **Integration Testing**: End-to-end testing with real Gemini responses
4. **Performance Optimization**: Monitor and optimize agent execution times
5. **Production Deployment**: Set up Cloud Run deployment pipeline

## References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Sequential Agents](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Models](https://docs.pydantic.dev/)

---

**Related ADRs**: 
- [ADR-001: Technology Stack Selection](./ADR-001-technology-stack.md)
- [ADR-002: Enhanced Campaign Creation Architecture](./ADR-002-enhanced-campaign-creation.md) 