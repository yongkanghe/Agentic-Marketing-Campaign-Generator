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
from agents.marketing_orchestrator import execute_campaign_workflow

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

@router.get("/", response_model=Dict[str, Any])
async def list_campaigns(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """List campaigns with pagination."""
    
    # Get campaigns from store
    all_campaigns = list(campaigns_store.values())
    total = len(all_campaigns)
    
    # Apply pagination
    paginated_campaigns = all_campaigns[offset:offset + limit]
    
    # Convert to response format
    campaigns = []
    for workflow_result in paginated_campaigns:
        campaign = {
            "campaign_id": workflow_result["campaign_id"],
            "summary": workflow_result["summary"],
            "created_at": workflow_result["created_at"],
            "status": workflow_result["status"]
        }
        campaigns.append(campaign)
    
    return {
        "campaigns": campaigns,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }

@router.delete("/{campaign_id}", response_model=Dict[str, str])
async def delete_campaign(campaign_id: str) -> Dict[str, str]:
    """Delete a campaign by ID."""
    
    if campaign_id not in campaigns_store:
        raise HTTPException(
            status_code=404,
            detail=f"Campaign not found: {campaign_id}"
        )
    
    del campaigns_store[campaign_id]
    
    return {
        "message": f"Campaign {campaign_id} deleted successfully"
    }

@router.post("/{campaign_id}/duplicate", response_model=CampaignResponse)
async def duplicate_campaign(campaign_id: str) -> CampaignResponse:
    """Duplicate an existing campaign."""
    
    if campaign_id not in campaigns_store:
        raise HTTPException(
            status_code=404,
            detail=f"Campaign not found: {campaign_id}"
        )
    
    # Get original campaign
    original_workflow = campaigns_store[campaign_id]
    
    # Create new campaign ID
    new_campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}_dup"
    
    # Duplicate the workflow result
    duplicated_workflow = original_workflow.copy()
    duplicated_workflow["campaign_id"] = new_campaign_id
    duplicated_workflow["summary"] = f"Copy of {original_workflow['summary']}"
    duplicated_workflow["created_at"] = datetime.now().isoformat()
    
    # Store duplicated campaign
    campaigns_store[new_campaign_id] = duplicated_workflow
    
    return CampaignResponse(
        campaign_id=duplicated_workflow["campaign_id"],
        summary=duplicated_workflow["summary"],
        business_analysis=BusinessAnalysis(**duplicated_workflow["business_analysis"]),
        social_posts=[SocialMediaPost(**post) for post in duplicated_workflow["social_posts"]],
        created_at=datetime.fromisoformat(duplicated_workflow["created_at"]),
        status=duplicated_workflow["status"]
    )

@router.get("/{campaign_id}/export")
async def export_campaign(campaign_id: str, format: str = "json"):
    """Export a campaign in the specified format."""
    
    if campaign_id not in campaigns_store:
        raise HTTPException(
            status_code=404,
            detail=f"Campaign not found: {campaign_id}"
        )
    
    if format not in ["json", "csv", "xlsx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported export format: {format}. Supported formats: json, csv, xlsx"
        )
    
    workflow_result = campaigns_store[campaign_id]
    
    if format == "json":
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=workflow_result,
            headers={"Content-Disposition": f"attachment; filename=campaign_{campaign_id}.json"}
        )
    else:
        # For CSV and XLSX, return a placeholder response
        raise HTTPException(
            status_code=501,
            detail=f"Export format {format} not yet implemented"
        ) 