"""
FILENAME: campaigns.py
DESCRIPTION/PURPOSE: Campaign management API routes with ADK agent integration
Author: JP + 2025-06-15
"""

import logging
import time
import os
import json
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..models import CampaignRequest, CampaignResponse, BusinessAnalysis, SocialMediaPost
from agents.marketing_orchestrator import execute_campaign_workflow
from utils.auth import get_current_user
from google import genai
from database.database import get_campaign_by_id, update_campaign_analysis

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

@router.post("/api/v1/campaigns/{campaign_id}/guidance-chat", response_model=Dict[str, Any])
async def chat_with_campaign_guidance(
    campaign_id: str,
    request: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """
    Chat with the campaign guidance AI to refine and improve campaign guidance.
    
    This endpoint allows users to have a conversation with the AI to:
    - Clarify business context and objectives
    - Refine visual style and creative direction
    - Adjust campaign guidance based on specific requirements
    - Get explanations about campaign decisions
    """
    try:
        logger.info(f"Campaign guidance chat for campaign {campaign_id}")
        
        # Get current campaign from in-memory store
        if campaign_id not in campaigns_store:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = campaigns_store[campaign_id]
        user_message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Initialize Gemini client for guidance chat
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-preview-05-20')
        
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        client = genai.Client(api_key=gemini_api_key)
        
        # Build context-aware prompt for guidance refinement
        business_analysis = campaign.get("business_analysis", {})
        current_guidance = business_analysis.get("campaign_guidance", {})
        
        system_prompt = f"""
        You are a specialized marketing campaign advisor helping to refine campaign guidance.
        
        CURRENT CAMPAIGN CONTEXT:
        - Company/Creator: {business_analysis.get('company_name', 'Unknown')}
        - Industry: {business_analysis.get('industry', 'Unknown')}
        - Business Type: {business_analysis.get('business_type', 'Unknown')}
        - Target Audience: {business_analysis.get('target_audience', 'Unknown')}
        
        CURRENT CAMPAIGN GUIDANCE:
        {json.dumps(current_guidance, indent=2)}
        
        CONVERSATION HISTORY:
        {json.dumps(conversation_history, indent=2)}
        
        USER'S NEW MESSAGE: {user_message}
        
        Your role is to:
        1. Help refine and improve the campaign guidance based on user feedback
        2. Provide specific, actionable suggestions for visual content creation
        3. Explain campaign decisions and reasoning
        4. Suggest improvements to make guidance more specific and effective
        5. Focus on the individual creator's work (not platform features for marketplace sellers)
        
        Respond in JSON format with:
        {{
            "response": "Your conversational response to the user",
            "suggested_updates": {{
                "field_name": "suggested new value",
                // Only include fields that should be updated based on conversation
            }},
            "explanation": "Brief explanation of why these updates would improve the campaign",
            "next_questions": ["question 1", "question 2"] // Optional follow-up questions
        }}
        
        Be conversational, helpful, and focus on actionable improvements.
        """
        
        # Generate AI response
        response = client.models.generate_content(
            model=gemini_model,
            contents=system_prompt
        )
        
        try:
            # Parse AI response
            import re
            
            ai_text = response.text
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                ai_response = json.loads(json_match.group())
            else:
                # Fallback if no JSON found
                ai_response = {
                    "response": ai_text,
                    "suggested_updates": {},
                    "explanation": "AI provided general guidance feedback",
                    "next_questions": []
                }
            
            # Update conversation history
            updated_history = conversation_history + [
                {"role": "user", "message": user_message, "timestamp": datetime.utcnow().isoformat()},
                {"role": "assistant", "message": ai_response["response"], "timestamp": datetime.utcnow().isoformat()}
            ]
            
            return {
                "success": True,
                "ai_response": ai_response,
                "conversation_history": updated_history,
                "campaign_id": campaign_id
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return {
                "success": True,
                "ai_response": {
                    "response": response.text,
                    "suggested_updates": {},
                    "explanation": "AI provided guidance feedback",
                    "next_questions": []
                },
                "conversation_history": conversation_history + [
                    {"role": "user", "message": user_message, "timestamp": datetime.utcnow().isoformat()},
                    {"role": "assistant", "message": response.text, "timestamp": datetime.utcnow().isoformat()}
                ],
                "campaign_id": campaign_id
            }
        
    except Exception as e:
        logger.error(f"Campaign guidance chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process guidance chat: {str(e)}")

@router.put("/api/v1/campaigns/{campaign_id}/guidance", response_model=Dict[str, Any])
async def update_campaign_guidance(
    campaign_id: str,
    guidance_updates: Dict[str, Any],
    current_user: str = Depends(get_current_user)
):
    """
    Update campaign guidance with user modifications.
    
    Allows users to directly edit and update campaign guidance fields.
    """
    try:
        logger.info(f"Updating campaign guidance for campaign {campaign_id}")
        
        # Get current campaign from in-memory store
        if campaign_id not in campaigns_store:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = campaigns_store[campaign_id]
        
        # Update guidance in campaign data
        business_analysis = campaign.get("business_analysis", {})
        current_guidance = business_analysis.get("campaign_guidance", {})
        
        # Deep merge the updates
        def deep_merge(base_dict, update_dict):
            for key, value in update_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    deep_merge(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_merge(current_guidance, guidance_updates)
        business_analysis["campaign_guidance"] = current_guidance
        campaign["business_analysis"] = business_analysis
        
        # Update in store
        campaigns_store[campaign_id] = campaign
        
        return {
            "success": True,
            "message": "Campaign guidance updated successfully",
            "updated_guidance": current_guidance,
            "campaign_id": campaign_id
        }
        
    except Exception as e:
        logger.error(f"Campaign guidance update error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update campaign guidance: {str(e)}") 