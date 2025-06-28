"""
FILENAME: campaigns.py
DESCRIPTION/PURPOSE: Campaign management API routes with ADK agent integration and CAMPAIGN ISOLATION
Author: JP + 2025-06-25

CRITICAL: Each campaign must be completely isolated - no shared state, context, or cache contamination.
"""

import logging
import time
import os
import json
import uuid
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..models import CampaignRequest, CampaignResponse, BusinessAnalysis, SocialMediaPost
from agents.marketing_orchestrator import execute_campaign_workflow
# Auth temporarily disabled for MVP
# from utils.auth import get_current_user
from google import genai
from database.database import get_campaign_by_id, update_campaign_analysis

logger = logging.getLogger(__name__)
router = APIRouter()

# CAMPAIGN ISOLATION: Each campaign gets its own isolated storage
campaigns_store: Dict[str, Dict[str, Any]] = {}

# CAMPAIGN ISOLATION: Track active campaigns to prevent context bleeding
active_campaigns: Dict[str, Dict[str, Any]] = {}

# Temporary auth placeholder for MVP
def get_current_user() -> str:
    """Temporary auth placeholder for MVP - returns default user"""
    return "demo_user"

def create_isolated_campaign_context(campaign_id: str, request: CampaignRequest) -> Dict[str, Any]:
    """
    Create completely isolated campaign context to prevent any cross-campaign contamination.
    
    CRITICAL: This ensures each campaign is processed in complete isolation.
    """
    isolated_context = {
        "campaign_id": campaign_id,
        "session_id": f"session_{campaign_id}_{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "request_hash": hash(f"{campaign_id}_{time.time()}_{request.model_dump()}"),
        "isolation_key": f"campaign_isolation_{campaign_id}",
        
        # Campaign-specific data (deep copy to prevent reference sharing)
        "business_description": request.business_description,
        "objective": request.objective,
        "target_audience": request.target_audience,
        "campaign_type": request.campaign_type.value,
        "creativity_level": request.creativity_level,
        "post_count": request.post_count,
        
        # URLs (if provided)
        "business_website": str(request.business_website) if request.business_website else None,
        "about_page_url": str(request.about_page_url) if request.about_page_url else None,
        "product_service_url": str(request.product_service_url) if request.product_service_url else None,
        
        # Isolation metadata
        "cache_namespace": f"campaign_{campaign_id}",
        "agent_session_id": f"agent_session_{campaign_id}",
        "processing_isolation": True
    }
    
    logger.info(f"🔒 Created isolated context for campaign {campaign_id}")
    logger.debug(f"🔒 Isolation key: {isolated_context['isolation_key']}")
    
    return isolated_context

def cleanup_campaign_context(campaign_id: str):
    """Clean up campaign context after processing to prevent memory leaks."""
    try:
        # Remove from active campaigns
        if campaign_id in active_campaigns:
            del active_campaigns[campaign_id]
            logger.info(f"🧹 Cleaned up active campaign context: {campaign_id}")
        
        # Note: We keep campaigns_store for API access, but clear processing context
        
    except Exception as e:
        logger.warning(f"Campaign context cleanup warning for {campaign_id}: {e}")

@router.post("/create", response_model=CampaignResponse)
async def create_campaign(
    request: CampaignRequest,
    current_user: str = Depends(get_current_user)
) -> CampaignResponse:
    """Create a new marketing campaign using the ADK agent workflow."""
    start_time = time.time()
    
    try:
        logger.info(f"Creating campaign: {request.objective}")
        
        # Generate unique campaign ID for complete isolation
        campaign_id = f"campaign_{uuid.uuid4().hex[:12]}_{int(time.time())}"
        
        # Create isolated campaign context
        isolated_context = create_isolated_campaign_context(campaign_id, request)
        
        # Track active campaign to prevent context bleeding
        active_campaigns[campaign_id] = isolated_context
        
        # Execute the ADK marketing workflow with isolated context
        workflow_result = await execute_campaign_workflow(
            business_description=isolated_context["business_description"],
            objective=isolated_context["objective"],
            target_audience=isolated_context["target_audience"],
            campaign_type=isolated_context["campaign_type"],
            creativity_level=isolated_context["creativity_level"],
            post_count=isolated_context["post_count"],
            business_website=isolated_context["business_website"],
            about_page_url=isolated_context["about_page_url"],
            product_service_url=isolated_context["product_service_url"],
            uploaded_files=[file.dict() for file in request.uploaded_files],
            # CRITICAL: Pass campaign isolation context
            campaign_id=campaign_id,
            session_id=isolated_context["session_id"],
            isolation_key=isolated_context["isolation_key"]
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
        
        # Clean up isolation context after successful processing
        cleanup_campaign_context(campaign_id)
        
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

@router.post("/{campaign_id}/guidance-chat", response_model=Dict[str, Any])
async def chat_with_campaign_guidance(
    campaign_id: str,
    request: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """
    Chat with AI to refine campaign guidance.
    Provides conversational interface for improving campaign strategy.
    """
    try:
        logger.info(f"Processing guidance chat for campaign {campaign_id}")
        
        # Get campaign data for context
        campaign_data = await get_campaign_by_id(campaign_id, current_user)
        if not campaign_data:
            # Fallback to in-memory store
            if campaign_id not in campaigns_store:
                raise HTTPException(status_code=404, detail="Campaign not found")
            campaign_data = campaigns_store[campaign_id]
        
        # Extract user message
        user_message = request.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get conversation history
        chat_history = request.get("conversation_history", [])
        
        # Initialize Gemini client
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Get model from environment
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Build context prompt with campaign data
        business_analysis = campaign_data.get("business_analysis", {})
        context_prompt = f"""
You are an AI marketing strategist helping refine campaign guidance. 

CURRENT CAMPAIGN CONTEXT:
- Company: {business_analysis.get('company_name', 'Unknown')}
- Industry: {business_analysis.get('industry', 'Unknown')}
- Business Type: {business_analysis.get('business_type', 'Unknown')}
- Target Audience: {business_analysis.get('target_audience', 'Unknown')}
- Brand Voice: {business_analysis.get('brand_voice', 'Unknown')}

CURRENT CAMPAIGN GUIDANCE:
- Creative Direction: {business_analysis.get('creative_direction', 'None set')}
- Visual Style: {business_analysis.get('visual_style', 'None set')}
- Content Themes: {business_analysis.get('content_themes', 'None set')}
- Image Generation: {business_analysis.get('image_generation_guidance', 'None set')}
- Video Generation: {business_analysis.get('video_generation_guidance', 'None set')}

INSTRUCTIONS:
1. Help the user refine their campaign guidance based on their specific needs
2. Provide specific, actionable suggestions for improving campaign effectiveness
3. Focus on the user's actual business/creator context, not generic advice
4. When suggesting changes, be specific about what fields to update and how
5. Maintain the creator's authentic voice and brand personality

User's request: {user_message}

Provide helpful guidance and specific suggestions for improving the campaign.
"""

        # Build conversation for Gemini
        messages = []
        
        # Add conversation history
        for msg in chat_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current user message
        messages.append({
            "role": "user", 
            "content": context_prompt
        })
        
        # Generate AI response
        response = client.models.generate_content(
            model=gemini_model,
            contents=context_prompt
        )
        
        ai_response = response.text
        
        # Update conversation history
        updated_history = chat_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response}
        ]
        
        return {
            "response": ai_response,
            "conversation_history": updated_history,
            "suggestions": {
                "has_suggestions": True,
                "message": "AI provided guidance refinement suggestions"
            }
        }
        
    except Exception as e:
        logger.error(f"Guidance chat failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )

@router.put("/{campaign_id}/guidance", response_model=Dict[str, Any])
async def update_campaign_guidance(
    campaign_id: str,
    guidance_updates: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """
    Update campaign guidance fields directly.
    Allows manual editing of campaign strategy elements.
    """
    try:
        logger.info(f"Updating guidance for campaign {campaign_id}")
        
        # Get campaign data
        campaign_data = await get_campaign_by_id(campaign_id, current_user)
        if not campaign_data:
            # Fallback to in-memory store
            if campaign_id not in campaigns_store:
                raise HTTPException(status_code=404, detail="Campaign not found")
            campaign_data = campaigns_store[campaign_id]
        
        # Deep merge function for nested updates
        def deep_merge(base_dict, update_dict):
            """Recursively merge update_dict into base_dict"""
            for key, value in update_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_merge(base_dict[key], value)
                else:
                    base_dict[key] = value
            return base_dict
        
        # Update business analysis with new guidance
        if "business_analysis" not in campaign_data:
            campaign_data["business_analysis"] = {}
        
        # Apply updates to business analysis
        deep_merge(campaign_data["business_analysis"], guidance_updates)
        
        # Save updated campaign
        update_result = await update_campaign_analysis(campaign_id, current_user, campaign_data["business_analysis"])
        if update_result:
            # Also update in-memory store
            campaigns_store[campaign_id] = campaign_data
            
            return {
                "success": True,
                "message": "Campaign guidance updated successfully",
                "updated_fields": list(guidance_updates.keys())
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save guidance updates")
            
    except Exception as e:
        logger.error(f"Guidance update failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Guidance update failed: {str(e)}"
        ) 