"""
FILENAME: campaigns.py
DESCRIPTION/PURPOSE: Campaign management API routes with ADK agent integration
Author: JP + 2024-12-19
"""

import logging
import time
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..models import CampaignRequest, CampaignResponse, BusinessAnalysis, SocialMediaPost
from ...agents.marketing_orchestrator import execute_campaign_workflow

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for demo
campaigns_store: Dict[str, Dict[str, Any]] = {}

@router.post("/create", response_model=CampaignResponse)
async def create_campaign(request: CampaignRequest) -> CampaignResponse:
    """Create a new marketing campaign using the ADK agent workflow."""
    start_time = time.time()
    
    try:
        logger.info(f"Creating campaign: {request.objective}")
        
        # Execute the ADK marketing workflow
        workflow_result = await execute_campaign_workflow(
            business_description=request.business_description,
            objective=request.objective,
            target_audience=request.target_audience,
            campaign_type=request.campaign_type.value,
            creativity_level=request.creativity_level,
            business_website=str(request.business_website) if request.business_website else None,
            about_page_url=str(request.about_page_url) if request.about_page_url else None,
            product_service_url=str(request.product_service_url) if request.product_service_url else None,
            uploaded_files=[file.dict() for file in request.uploaded_files]
        )
        
        # Convert workflow result to response format
        campaign_response = CampaignResponse(
            campaign_id=workflow_result["campaign_id"],
            summary=workflow_result["summary"],
            business_analysis=BusinessAnalysis(**workflow_result["business_analysis"]),
            social_posts=[SocialMediaPost(**post) for post in workflow_result["social_posts"]],
            created_at=datetime.fromisoformat(workflow_result["created_at"]),
            status=workflow_result["status"]
        )
        
        # Store campaign for retrieval
        campaigns_store[campaign_response.campaign_id] = workflow_result
        
        processing_time = time.time() - start_time
        logger.info(f"Campaign created successfully in {processing_time:.2f}s: {campaign_response.campaign_id}")
        
        return campaign_response
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Campaign creation failed after {processing_time:.2f}s: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Campaign creation failed: {str(e)}"
        )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str) -> CampaignResponse:
    """Retrieve a specific campaign by ID."""
    
    if campaign_id not in campaigns_store:
        raise HTTPException(
            status_code=404,
            detail=f"Campaign not found: {campaign_id}"
        )
    
    workflow_result = campaigns_store[campaign_id]
    
    return CampaignResponse(
        campaign_id=workflow_result["campaign_id"],
        summary=workflow_result["summary"],
        business_analysis=BusinessAnalysis(**workflow_result["business_analysis"]),
        social_posts=[SocialMediaPost(**post) for post in workflow_result["social_posts"]],
        created_at=datetime.fromisoformat(workflow_result["created_at"]),
        status=workflow_result["status"]
    ) 