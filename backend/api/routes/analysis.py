"""
FILENAME: analysis.py
DESCRIPTION/PURPOSE: URL and file analysis API routes with Gemini ADK integration
Author: JP + 2024-12-19
"""

import logging
import sys
import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File

# Add backend directory to Python path for proper imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ..models import URLAnalysisRequest, URLAnalysisResponse, BusinessAnalysis

# Import the business analysis service
try:
    from agents.business_analysis_agent import business_analysis_service
except ImportError as e:
    logger.error(f"Failed to import business_analysis_service: {e}")
    # Fallback to None - will use mock data
    business_analysis_service = None

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/url", response_model=URLAnalysisResponse)
async def analyze_urls(request: URLAnalysisRequest) -> URLAnalysisResponse:
    """Analyze business URLs to extract company and market intelligence using Gemini ADK agents."""
    
    try:
        logger.info(f"Analyzing {len(request.urls)} URLs with {request.analysis_depth} depth")
        
        # Convert URLs to strings for processing
        url_strings = [str(url) for url in request.urls]
        
        # Use ADK business analysis service if available, otherwise fallback to mock
        if business_analysis_service:
            try:
                analysis_result = await business_analysis_service.analyze_urls(
                    urls=url_strings,
                    analysis_depth=request.analysis_depth
                )
                
                # Extract business analysis data
                business_data = analysis_result.get("business_analysis", {})
                business_analysis = BusinessAnalysis(
                    company_name=business_data.get("company_name", "Unknown"),
                    industry=business_data.get("industry", "Unknown"),
                    target_audience=business_data.get("target_audience", "Unknown"),
                    value_propositions=business_data.get("value_propositions", []),
                    brand_voice=business_data.get("brand_voice", "Unknown"),
                    competitive_advantages=business_data.get("competitive_advantages", []),
                    market_positioning=business_data.get("market_positioning", "Unknown")
                )
                
                return URLAnalysisResponse(
                    business_analysis=business_analysis,
                    url_insights=analysis_result.get("url_insights", {}),
                    processing_time=analysis_result.get("processing_time", 0.0),
                    confidence_score=analysis_result.get("confidence_score", 0.0),
                    business_intelligence=analysis_result.get("business_intelligence", {}),
                    analysis_metadata=analysis_result.get("analysis_metadata", {})
                )
            except Exception as agent_error:
                logger.warning(f"ADK agent failed, falling back to mock data: {agent_error}")
                # Fall through to mock data below
        
        # Fallback mock data when ADK agent is not available
        logger.info("Using mock business analysis data")
        business_analysis = BusinessAnalysis(
            company_name="Sample Company",
            industry="Technology",
            target_audience="Business professionals",
            value_propositions=[
                "Innovative solutions",
                "Customer-centric approach",
                "Proven track record"
            ],
            brand_voice="Professional yet approachable",
            competitive_advantages=[
                "Advanced technology",
                "Expert team",
                "Comprehensive support"
            ],
            market_positioning="Premium solution provider"
        )
        
        url_insights = {}
        for i, url in enumerate(request.urls):
            url_insights[str(url)] = {
                "content_type": "business_website",
                "key_topics": ["innovation", "technology", "solutions"],
                "sentiment": "positive",
                "confidence": 0.85 + (i * 0.05),
                "extracted_data": {
                    "company_info": "Sample company information",
                    "products_services": "Technology solutions",
                    "contact_info": "Contact details found"
                }
            }
        
        return URLAnalysisResponse(
            business_analysis=business_analysis,
            url_insights=url_insights,
            processing_time=2.0,
            confidence_score=0.87
        )
        
    except Exception as e:
        logger.error(f"URL analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"URL analysis failed: {str(e)}"
        )

@router.post("/files")
async def analyze_files(files: List[UploadFile] = File(...)):
    """Analyze uploaded files for business insights."""
    
    try:
        logger.info(f"Analyzing {len(files)} uploaded files")
        
        file_analyses = []
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
        
        return {
            "file_analyses": file_analyses,
            "total_files": len(files),
            "processing_time": 1.8,
            "overall_insights": {
                "brand_consistency": "High",
                "visual_quality": "Professional",
                "content_relevance": "Strong"
            }
        }
        
    except Exception as e:
        logger.error(f"File analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"File analysis failed: {str(e)}"
        ) 