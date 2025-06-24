"""
FILENAME: models.py
DESCRIPTION/PURPOSE: Pydantic models for API request/response handling
Author: JP + 2025-06-15

This module defines the data models used for API communication between
the frontend and backend, ensuring type safety and validation.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum
# Function to convert snake_case to camelCase for Pydantic aliases
def to_camel(string: str) -> str:
    """Convert snake_case to camelCase for API response consistency (ADR-018)."""
    components = string.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])

# Base model with camelCase aliasing
class Base(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

# Enums
class CampaignType(str, Enum):
    """Campaign type enumeration."""
    PRODUCT = "product"
    SERVICE = "service"
    BRAND = "brand"
    EVENT = "event"

class CreativityLevel(int, Enum):
    """Creativity level enumeration (1-10 scale)."""
    CONSERVATIVE = 1
    MODERATE = 5
    EXPERIMENTAL = 10

class PostType(str, Enum):
    """Social media post type enumeration."""
    TEXT_URL = "text_url"
    TEXT_IMAGE = "text_image"
    TEXT_VIDEO = "text_video"

# Base Models
class BusinessAnalysis(Base):
    """
    Business analysis results from URL and file processing.
    
    ADK Enhancement: This model now includes all fields required for 
    proper data flow to downstream content generation agents.
    """
    # Core business information
    company_name: Optional[str] = None
    business_description: Optional[str] = None  # ADK ENHANCEMENT: Required for content generation
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    
    # Source URLs for context
    business_website: Optional[HttpUrl] = None
    about_page_url: Optional[HttpUrl] = None
    product_service_url: Optional[HttpUrl] = None

    # Business context
    value_propositions: List[str] = Field(default_factory=list)
    brand_voice: Optional[str] = None
    competitive_advantages: List[str] = Field(default_factory=list)
    market_positioning: Optional[str] = None
    key_messaging: List[str] = Field(default_factory=list)  # ADK ENHANCEMENT
    
    # ADK ENHANCEMENT: Product-specific context for Visual Content Agent
    product_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # ADK ENHANCEMENT: Campaign guidance for UI and content generation
    campaign_guidance: Optional[Dict[str, Any]] = Field(default_factory=dict)

class FileUpload(Base):
    """File upload information."""
    filename: str
    content_type: str
    size: int
    category: str  # "images", "documents", "campaigns"

class SocialMediaPost(Base):
    """Social media post structure with per-post error handling (ADR-016)."""
    id: str
    type: PostType
    content: str
    url: Optional[str] = None
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    video_prompt: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None  # ADK ENHANCEMENT: Missing field for video thumbnails
    hashtags: List[str] = Field(default_factory=list)
    platform_optimized: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    engagement_score: Optional[float] = None
    selected: bool = False
    error: Optional[str] = None  # ADR-016: Per-post error handling

# Request Models
class CampaignRequest(Base):
    """Enhanced campaign creation request."""
    # Basic campaign info
    business_description: str = Field(..., min_length=10, max_length=2000)
    objective: str = Field(..., min_length=5, max_length=500)
    target_audience: str = Field(..., min_length=5, max_length=500)
    
    # Enhanced fields
    campaign_type: CampaignType
    creativity_level: int = Field(..., ge=1, le=10)
    post_count: int = Field(default=9, ge=3, le=15)
    
    # URL analysis
    business_website: Optional[HttpUrl] = None
    about_page_url: Optional[HttpUrl] = None
    product_service_url: Optional[HttpUrl] = None
    
    # File uploads (handled separately via multipart)
    uploaded_files: List[FileUpload] = Field(default_factory=list)
    
    # Campaign template
    template_data: Optional[Dict[str, Any]] = None

class URLAnalysisRequest(Base):
    """URL analysis request."""
    urls: List[str] = Field(..., min_length=1, max_length=5)
    analysis_depth: str = Field(default="standard", pattern="^(basic|standard|comprehensive)$")

class ContentGenerationRequest(Base):
    """Content generation request."""
    campaign_type: Optional[CampaignType] = None
    business_context: BusinessAnalysis
    campaign_objective: str
    creativity_level: int = Field(..., ge=1, le=10)
    post_count: int = Field(default=9, ge=3, le=15)
    include_hashtags: bool = True

class SocialPostRegenerationRequest(Base):
    """Social post regeneration request."""
    post_type: PostType
    regenerate_count: int = Field(default=3, ge=1, le=10)
    business_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    creativity_level: Optional[int] = Field(default=7, ge=1, le=10)
    current_posts: Optional[List[SocialMediaPost]] = Field(default_factory=list)

# Response Models
class CampaignResponse(Base):
    """Campaign creation response."""
    campaign_id: str
    summary: str
    business_analysis: BusinessAnalysis
    social_posts: List[SocialMediaPost]
    created_at: datetime
    status: str = "completed"

class URLAnalysisResponse(Base):
    """URL analysis response."""
    business_analysis: BusinessAnalysis
    url_insights: Dict[str, Dict[str, Any]]
    processing_time: float
    confidence_score: float
    business_intelligence: Optional[Dict[str, Any]] = None
    analysis_metadata: Optional[Dict[str, Any]] = None

class ContentGenerationResponse(Base):
    """Content generation response."""
    posts: List[SocialMediaPost]
    hashtag_suggestions: List[str]
    generation_metadata: Dict[str, Any]
    processing_time: float

class SocialPostRegenerationResponse(Base):
    """Social post regeneration response with camelCase output (ADR-018)."""
    new_posts: List[SocialMediaPost]
    regeneration_metadata: Dict[str, Any]
    processing_time: float

class ErrorResponse(Base):
    """Error response model."""
    error: str
    status_code: int
    path: str
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None

# Agent State Models
class AgentState(Base):
    """Agent execution state."""
    agent_name: str
    status: str  # "pending", "running", "completed", "failed"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class WorkflowState(Base):
    """Complete workflow state tracking."""
    workflow_id: str
    campaign_request: CampaignRequest
    agent_states: List[AgentState] = Field(default_factory=list)
    current_agent: Optional[str] = None
    overall_status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    final_result: Optional[CampaignResponse] = None

# Health Check Models
class HealthResponse(Base):
    """Health check response."""
    status: str
    agent_initialized: bool
    gemini_key_configured: bool
    services: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.now)

class AgentStatusResponse(BaseModel):
    """Agent status response."""
    agent_name: str
    agent_type: str
    sub_agents: List[str]
    description: str
    status: str
    last_execution: Optional[datetime] = None 