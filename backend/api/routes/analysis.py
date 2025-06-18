"""
FILENAME: analysis.py
DESCRIPTION/PURPOSE: URL and file analysis API routes with Gemini ADK integration
Author: JP + 2025-06-15
"""

import logging
import sys
import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

# Add backend directory to Python path for proper imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ..models import URLAnalysisRequest, URLAnalysisResponse, BusinessAnalysis

# Import the business analysis service
try:
    from agents.business_analysis_agent import analyze_business_urls
    business_analysis_service = True
except ImportError as e:
    logger.error(f"Failed to import analyze_business_urls: {e}")
    # Fallback to None - will use mock data
    business_analysis_service = False

# Import the agent that performs the actual analysis
try:
    from agents.business_analysis_agent import URLAnalysisAgent
except ImportError:
    URLAnalysisAgent = None

logger = logging.getLogger(__name__)
router = APIRouter()

def _is_valid_url(url: str) -> bool:
    """Validate URL format."""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

@router.post("/url", response_model=URLAnalysisResponse)
async def analyze_business_url(request: URLAnalysisRequest):
    """
    Analyzes one or more business URLs to extract business context using the real AI agent.
    """
    if not URLAnalysisAgent:
        logger.error("URLAnalysisAgent is not available.")
        raise HTTPException(status_code=500, detail="AI services are not configured.")

    try:
        logger.info(f"Received request to analyze URLs: {request.urls}")
        agent = URLAnalysisAgent()
        analysis_result = await agent.analyze_urls(
            urls=request.urls,
            analysis_type=request.analysis_depth
        )

        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        logger.info("🔧 STARTING theme extraction process...")
        
        # Extract themes and tags for frontend compatibility
        suggested_themes = []
        suggested_tags = []
        
        logger.info(f"DEBUG: Extracting themes from analysis result...")
        
        if "business_analysis" in analysis_result and analysis_result["business_analysis"]:
            business_analysis = analysis_result["business_analysis"]
            logger.info(f"DEBUG: Business analysis found")
            
            # Extract themes from campaign guidance
            campaign_guidance = business_analysis.get("campaign_guidance", {})
            logger.info(f"DEBUG: Campaign guidance keys: {list(campaign_guidance.keys())}")
            
            content_themes = campaign_guidance.get("content_themes", {})
            logger.info(f"DEBUG: Content themes keys: {list(content_themes.keys())}")
            
            # Get primary themes
            primary_themes = content_themes.get("primary_themes", [])
            logger.info(f"DEBUG: Primary themes found: {primary_themes}")
            if primary_themes:
                suggested_themes.extend(primary_themes)
            
            # Get product-specific themes (handle null case)
            product_themes = content_themes.get("product_specific_themes")
            if product_themes and isinstance(product_themes, list):
                suggested_themes.extend(product_themes[:3])  # Limit to 3 more themes
            
            # Generate suggested tags from various sources
            # Use value propositions as tags
            value_props = business_analysis.get("value_propositions", [])
            for prop in value_props[:4]:  # Limit to 4
                # Convert to hashtag format (remove spaces, special chars)
                tag = prop.replace(" ", "").replace(",", "").replace("&", "And")
                if len(tag) > 3 and len(tag) < 20:  # Reasonable tag length
                    suggested_tags.append(tag)
            
            # Add industry-based tags
            industry = business_analysis.get("industry", "")
            if industry:
                # Extract key words from industry
                industry_words = industry.replace("(", "").replace(")", "").split()
                for word in industry_words[:3]:
                    if len(word) > 3:
                        suggested_tags.append(word.replace(",", ""))
            
            # Add competitive advantages as tags
            comp_advantages = business_analysis.get("competitive_advantages", [])
            for advantage in comp_advantages[:2]:  # Limit to 2
                # Extract key words
                words = advantage.split()[:2]  # First 2 words
                for word in words:
                    clean_word = word.replace(",", "").replace(".", "")
                    if len(clean_word) > 3:
                        suggested_tags.append(clean_word)
        
        # Fallback themes and tags if none extracted
        if not suggested_themes:
            suggested_themes = ["Professional", "Modern", "Innovative", "Trustworthy", "Quality"]
        
        if not suggested_tags:
            suggested_tags = ["Business", "Quality", "Value", "Innovation", "Service", "Growth"]
        
        # Remove duplicates and limit counts
        suggested_themes = list(dict.fromkeys(suggested_themes))[:8]  # Max 8 themes
        suggested_tags = list(dict.fromkeys(suggested_tags))[:10]     # Max 10 tags
        
        # Add themes and tags to top level for frontend compatibility
        analysis_result["suggested_themes"] = suggested_themes
        analysis_result["suggested_tags"] = suggested_tags
        
        logger.info(f"Extracted {len(suggested_themes)} themes and {len(suggested_tags)} tags")
        
        return analysis_result

    except Exception as e:
        logger.error(f"URL analysis endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/files")
async def analyze_files(
    files: List[UploadFile] = File(...),
    analysis_type: str = Form(default="standard", pattern="^(basic|standard|comprehensive)$")
):
    """Analyze uploaded files for business insights."""
    
    try:
        logger.info(f"Analyzing {len(files)} uploaded files")
        
        file_analyses = []
        analysis_results = []  # Backward-compatible field for tests
        
        for file in files:
            # Read file content
            content = await file.read()
            
            # Mock file analysis (replace with real ADK multimodal agent call)
            analysis = {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content),
                "analysis": {
                    "file_type": "image" if file.content_type.startswith("image/") else "document",
                    "key_insights": [
                        "Professional design elements",
                        "Brand consistency",
                        "Target audience alignment"
                    ],
                    "extracted_elements": {
                        "colors": ["#1976d2", "#ffffff", "#f5f5f5"],
                        "text_content": "Sample extracted text",
                        "visual_style": "Modern and professional"
                    },
                    "confidence": 0.82
                }
            }
            file_analyses.append(analysis)
            
            # Backward-compatible analysis_results for tests
            analysis_results.append({
                "filename": file.filename,
                "file_type": file.content_type,
                "content_summary": f"Analysis of {file.filename}",
                "key_insights": analysis["analysis"]["key_insights"],
                "analysis_status": "success"
            })
        
        # Enhanced insights based on analysis type
        enhanced_insights = {}
        if analysis_type == "comprehensive":
            enhanced_insights = {
                "business_focus": "AI solutions for small businesses",
                "target_market": "Small business owners",
                "key_themes": ["AI technology", "Business automation", "Small business solutions"]
            }
        
        response_data = {
            "file_analyses": file_analyses,
            "total_files": len(files),
            "processing_time": 1.8,
            "overall_insights": {
                "brand_consistency": "High",
                "visual_quality": "Professional",
                "content_relevance": "Strong"
            },
            # Backward-compatible fields for tests
            "analysis_results": analysis_results,
            "extracted_insights": {
                "brand_elements": ["Professional design", "Consistent colors"],
                "content_themes": ["Business focus", "Professional presentation"],
                "quality_indicators": ["High resolution", "Clear messaging"],
                **enhanced_insights
            },
            "analysis_metadata": {
                "analysis_type": analysis_type,
                "files_processed": len(files),
                "processing_method": "mock_analysis"
            }
        }
        
        return response_data
        
    except Exception as e:
        logger.error(f"File analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"File analysis failed: {str(e)}"
        ) 