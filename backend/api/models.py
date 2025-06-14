"""
FILENAME: models.py
DESCRIPTION/PURPOSE: Pydantic models for API request/response handling
Author: JP + 2024-12-19

This module defines the data models used for API communication between
the frontend and backend, ensuring type safety and validation.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from enum import Enum

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
class BusinessAnalysis(BaseModel):
    """Business analysis results from URL and file processing."""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    value_propositions: List[str] = Field(default_factory=list)
    brand_voice: Optional[str] = None
    competitive_advantages: List[str] = Field(default_factory=list)
    market_positioning: Optional[str] = None

class FileUpload(BaseModel):
    """File upload information."""
    filename: str
    content_type: str
    size: int
    category: str  # "images", "documents", "campaigns"

class SocialMediaPost(BaseModel):
    """Social media post structure."""
    id: str
    type: PostType
    content: str
    url: Optional[str] = None
    image_prompt: Optional[str] = None
    video_prompt: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    platform_optimized: Dict[str, str] = Field(default_factory=dict)
    engagement_score: Optional[float] = None
    selected: bool = False

# Request Models
class CampaignRequest(BaseModel):
    """Enhanced campaign creation request."""
    # Basic campaign info
    business_description: str = Field(..., min_length=10, max_length=2000)
    objective: str = Field(..., min_length=5, max_length=500)
    target_audience: str = Field(..., min_length=5, max_length=500)
    
    # Enhanced fields
    campaign_type: CampaignType
    creativity_level: int = Field(..., ge=1, le=10)
    
    # URL analysis
    business_website: Optional[HttpUrl] = None
    about_page_url: Optional[HttpUrl] = None
    product_service_url: Optional[HttpUrl] = None
    
    # File uploads (handled separately via multipart)
    uploaded_files: List[FileUpload] = Field(default_factory=list)
    
    # Campaign template
    template_data: Optional[Dict[str, Any]] = None

class URLAnalysisRequest(BaseModel):
    """URL analysis request."""
    urls: List[HttpUrl] = Field(..., min_items=1, max_items=5)
    analysis_depth: str = Field(default="standard", pattern="^(basic|standard|comprehensive)$")

class ContentGenerationRequest(BaseModel):
    """Content generation request."""
    business_context: BusinessAnalysis
    campaign_objective: str
    creativity_level: int = Field(..., ge=1, le=10)
    post_count: int = Field(default=9, ge=3, le=15)
    include_hashtags: bool = True

class SocialPostRegenerationRequest(BaseModel):
    """Social post regeneration request."""
    business_context: BusinessAnalysis
    post_type: PostType
    current_posts: List[SocialMediaPost]
    regenerate_count: int = Field(default=3, ge=1, le=5)

# Response Models
class CampaignResponse(BaseModel):
    """Campaign creation response."""
    campaign_id: str
    summary: str
    business_analysis: BusinessAnalysis
    social_posts: List[SocialMediaPost]
    created_at: datetime
    status: str = "completed"

class URLAnalysisResponse(BaseModel):
    """URL analysis response."""
    business_analysis: BusinessAnalysis
    url_insights: Dict[str, Dict[str, Any]]
    processing_time: float
    confidence_score: float
    business_intelligence: Optional[Dict[str, Any]] = None
    analysis_metadata: Optional[Dict[str, Any]] = None

class ContentGenerationResponse(BaseModel):
    """Content generation response."""
    posts: List[SocialMediaPost]
    hashtag_suggestions: List[str]
    generation_metadata: Dict[str, Any]
    processing_time: float

class SocialPostRegenerationResponse(BaseModel):
    """Social post regeneration response."""
    new_posts: List[SocialMediaPost]
    regeneration_metadata: Dict[str, Any]
    processing_time: float

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    status_code: int
    path: str
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None

# Agent State Models
class AgentState(BaseModel):
    """Agent execution state."""
    agent_name: str
    status: str  # "pending", "running", "completed", "failed"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class WorkflowState(BaseModel):
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
class HealthResponse(BaseModel):
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