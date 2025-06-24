"""
FILENAME: ADK-API-REFERENCE-ARCHITECTURE.md  
DESCRIPTION/PURPOSE: ADK-compliant API Reference Architecture Documentation
Author: JP + 2025-06-25
"""

# ADK API Reference Architecture
## AI Marketing Campaign Post Generator

### Overview
This document outlines the ADK-compliant API architecture for the AI Marketing Campaign Post Generator, following Google ADK samples best practices and patterns.

### ADK Framework Integration

#### Agent Structure (ADK Compliant)
```
backend/agents/
├── __init__.py              # Exposes root_agent for ADK CLI
├── agent.py                 # ADK-compliant root agent module
├── marketing_orchestrator.py # Main orchestrator implementation
├── business_analysis_agent.py # Business analysis sub-agents
├── adk_visual_agents.py     # Visual content ADK agents
└── visual_content_agent.py  # Visual content tools
```

#### Root Agent Pattern
Following ADK samples, our root agent is structured as:

```python
# backend/agents/agent.py
from google.adk.agents.sequential_agent import SequentialAgent
from .marketing_orchestrator import create_marketing_orchestrator_agent

async def create_root_agent() -> SequentialAgent:
    """Creates the root agent following ADK best practices."""
    return await create_marketing_orchestrator_agent()

# ADK CLI compatibility - root_agent must be available at module level
root_agent = get_root_agent()
```

### API Architecture

#### FastAPI Application Structure
```
backend/api/
├── main.py                  # FastAPI app with ADK integration
├── models.py               # Pydantic models
└── routes/
    ├── campaigns.py        # Campaign management
    ├── content.py          # Content generation
    ├── analysis.py         # Business analysis
    └── test_endpoints.py   # Testing endpoints
```

#### ADK Agent Initialization
```python
# backend/api/main.py
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from agents.marketing_orchestrator import create_marketing_orchestrator_agent

# Global agent instance
marketing_agent: SequentialAgent = None
session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global marketing_agent
    marketing_agent = await create_marketing_orchestrator_agent()
    yield
```

### Sequential Agent Architecture

#### Marketing Orchestrator (Root Agent)
```
MarketingOrchestratorAgent (SequentialAgent)
├── BusinessAnalysisAgent (SequentialAgent)
│   ├── URLAnalysisAgent (LlmAgent)
│   ├── FileAnalysisAgent (LlmAgent)
│   └── BusinessContextAgent (LlmAgent)
└── ContentGenerationAgent (SequentialAgent)
    ├── SocialContentAgent (LlmAgent)
    ├── HashtagOptimizationAgent (LlmAgent)
    └── VisualContentOrchestratorAgent (SequentialAgent)
        ├── ImageGenerationAgent (LlmAgent)
        └── VideoGenerationAgent (LlmAgent)
```

#### Agent Responsibilities

**BusinessAnalysisAgent**:
- URL content extraction and analysis
- Multimodal file analysis (images, documents)
- Business context synthesis

**ContentGenerationAgent**:
- Social media post generation
- Hashtag optimization
- Visual content orchestration

**VisualContentOrchestratorAgent**:
- Image generation with validation
- Video generation with validation
- Content quality assurance

### API Endpoints

#### Campaign Management
```
POST /api/v1/campaigns/create
GET  /api/v1/campaigns/{campaign_id}
GET  /api/v1/campaigns/list
PUT  /api/v1/campaigns/{campaign_id}/update
```

#### Content Generation
```
POST /api/v1/content/generate           # Generate social posts
POST /api/v1/content/regenerate         # Regenerate specific posts
POST /api/v1/content/visual/generate    # Generate visual content
GET  /api/v1/content/visual/{filename}  # Serve generated images/videos
```

#### Business Analysis
```
POST /api/v1/analysis/url              # Analyze business URLs
POST /api/v1/analysis/files            # Analyze uploaded files
GET  /api/v1/analysis/{analysis_id}    # Get analysis results
```

#### Agent Status
```
GET  /health                           # Health check
GET  /api/v1/agent/status             # ADK agent status
```

### Data Models

#### Campaign Request/Response
```python
class CampaignRequest(BaseModel):
    business_description: str
    objective: str
    target_audience: str
    campaign_type: str
    creativity_level: int
    business_website: Optional[str] = None
    about_page_url: Optional[str] = None
    product_service_url: Optional[str] = None

class CampaignResponse(BaseModel):
    campaign_id: str
    status: str
    business_analysis: Optional[BusinessAnalysis] = None
    social_posts: List[SocialMediaPost] = []
    created_at: datetime
```

#### Content Generation Models
```python
class ContentGenerationRequest(BaseModel):
    business_description: str
    objective: str
    target_audience: str
    campaign_type: str
    creativity_level: int
    post_count: int = 9

class SocialMediaPost(BaseModel):
    platform: str
    content: str
    hashtags: List[str]
    post_type: PostType
    visual_content_url: Optional[str] = None
    engagement_score: Optional[float] = None
```

### ADK Services Integration

#### Session Management
```python
# In-memory session service for development
session_service = InMemorySessionService()

# Production: Can be configured for persistent storage
# session_service = SessionService(db_url="postgresql://...")
```

#### Artifact Management
```python
# In-memory artifact service for development  
artifact_service = InMemoryArtifactService()

# Production: Can be configured for cloud storage
# artifact_service = ArtifactService(storage_uri="gs://bucket/artifacts")
```

### Visual Content Generation

#### ADK Agentic Visual Pipeline
```python
# backend/agents/adk_visual_agents.py
class VisualContentOrchestratorAgent(SequentialAgent):
    """ADK Sequential Agent for visual content generation"""
    
    def __init__(self):
        super().__init__(
            name="VisualContentOrchestratorAgent",
            sub_agents=[
                ImageGenerationAgent(),
                VideoGenerationAgent()
            ]
        )

class ImageGenerationAgent(LlmAgent):
    """ADK LLM Agent with autonomous validation"""
    
    def __init__(self):
        super().__init__(
            name="ImageGenerationAgent",
            model=Gemini(model_name="gemini-2.5-flash"),
            tools=[
                generate_image_tool,
                validate_image_tool,
                save_image_tool
            ]
        )
```

### Testing Strategy

#### ADK Agent Testing
```python
# Test ADK CLI compatibility
def test_root_agent_import():
    from agents import root_agent
    assert isinstance(root_agent, SequentialAgent)
    assert root_agent.name == "MarketingOrchestratorAgent"

# Test agent workflow
@pytest.mark.asyncio
async def test_campaign_workflow():
    from agents.marketing_orchestrator import execute_campaign_workflow
    result = await execute_campaign_workflow(
        business_description="Test business",
        objective="increase_brand_awareness",
        target_audience="young adults",
        campaign_type="product_launch",
        creativity_level=7
    )
    assert "business_analysis" in result
    assert "social_posts" in result
```

### Deployment Considerations

#### Environment Configuration
```bash
# backend/.env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./database/data/database.db
```

#### Port Configuration
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:8080`
- Database: SQLite (local) / PostgreSQL (production)

#### ADK CLI Compatibility
```bash
# Run agent via ADK CLI (from backend directory)
adk run agents

# Run agent via ADK Web UI
adk web agents
```

### Production Deployment

#### Google Cloud Run Configuration
```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ai-marketing-campaign-api
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/ai-marketing-api
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-secret
              key: api-key
```

### Monitoring and Observability

#### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "agent_initialized": marketing_agent is not None,
        "gemini_key_configured": bool(os.getenv("GEMINI_API_KEY")),
        "services": {
            "session_service": "in_memory",
            "artifact_service": "in_memory"
        }
    }
```

#### Logging
```python
# Structured logging for ADK agents
logger = logging.getLogger("ai_marketing_campaign")
logger.info("Marketing orchestrator agent initialized")
logger.debug(f"Agent details: {type(marketing_agent).__name__}")
```

### Security Considerations

#### API Security
- CORS configuration for frontend origins
- TrustedHost middleware for allowed hosts
- Input validation via Pydantic models
- Environment-based secrets management

#### ADK Security
- API key management via environment variables
- Session isolation via InMemorySessionService
- Artifact security via controlled access

### Performance Optimization

#### Async Operations
- All ADK agent operations are async
- Non-blocking API endpoints
- Concurrent sub-agent execution

#### Caching Strategy
- Generated content caching
- Image/video file caching
- Business analysis result caching

### Future Enhancements

#### ADK Framework Evolution
- Migration to newer ADK versions
- Enhanced agent capabilities
- Improved observability

#### Production Features
- Persistent session storage
- Cloud artifact storage
- Advanced monitoring
- Multi-tenant support

---

This architecture follows Google ADK samples best practices while providing a production-ready API for marketing campaign generation. 