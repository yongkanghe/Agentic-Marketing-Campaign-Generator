"""
FILENAME: business_analysis_agent.py
DESCRIPTION/PURPOSE: Business analysis agent using Google ADK and Gemini for URL analysis and business intelligence extraction
Author: JP + 2024-12-19
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig

logger = logging.getLogger(__name__)

class BusinessAnalysisContext:
    """Context object for business analysis data."""
    def __init__(self):
        self.urls: List[str] = []
        self.scraped_content: Dict[str, str] = {}
        self.business_analysis: Dict[str, Any] = {}
        self.url_insights: Dict[str, Any] = {}
        self.confidence_score: float = 0.0
        self.processing_time: float = 0.0

class URLScrapingAgent:
    """Agent for scraping and extracting content from URLs."""
    
    async def scrape_url(self, url: str, max_chars: int = 5000) -> Dict[str, Any]:
        """Scrape content from a URL with error handling."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract key content
                        title = soup.find('title')
                        title_text = title.get_text().strip() if title else ""
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text content
                        text = soup.get_text()
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = ' '.join(chunk for chunk in chunks if chunk)
                        
                        # Truncate if too long
                        if len(text) > max_chars:
                            text = text[:max_chars] + "..."
                        
                        return {
                            "url": url,
                            "title": title_text,
                            "content": text,
                            "status": "success",
                            "content_length": len(text)
                        }
                    else:
                        return {
                            "url": url,
                            "status": "error",
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {
                "url": url,
                "status": "error",
                "error": str(e)
            }

async def create_content_extraction_agent() -> LlmAgent:
    """Creates agent for extracting structured business information from scraped content."""
    return LlmAgent(
        name="ContentExtractionAgent",
        model="gemini-2.0-flash-exp",
        instruction="""You are an expert business analyst. Analyze the provided website content and extract key business information.

Website Content:
{scraped_content}

Extract and structure the following information:
1. Company/Business Name
2. Industry/Sector
3. Products/Services offered
4. Target Audience/Customer segments
5. Value Propositions
6. Brand Voice/Tone
7. Competitive Advantages
8. Contact Information
9. Key Topics/Themes
10. Business Model insights

Provide your analysis in JSON format:
{
  "company_name": "extracted name",
  "industry": "industry classification",
  "products_services": ["list of offerings"],
  "target_audience": "audience description",
  "value_propositions": ["key value props"],
  "brand_voice": "voice description",
  "competitive_advantages": ["advantages"],
  "contact_info": "contact details",
  "key_topics": ["main themes"],
  "business_model": "model description",
  "confidence": 0.85
}""",
        description="Extracts structured business information from website content.",
        output_key="business_data",
    )

async def create_market_analysis_agent() -> LlmAgent:
    """Creates agent for market and competitive analysis."""
    return LlmAgent(
        name="MarketAnalysisAgent",
        model="gemini-2.0-flash-exp",
        instruction="""Based on the extracted business data: {business_data}

Perform a comprehensive market analysis:

1. Market Positioning Analysis
2. Competitive Landscape Assessment
3. Target Market Insights
4. Growth Opportunities
5. Marketing Strategy Recommendations
6. Brand Differentiation Factors

Provide analysis in JSON format:
{
  "market_positioning": "positioning analysis",
  "competitive_landscape": "competitive assessment",
  "target_market_insights": "market insights",
  "growth_opportunities": ["opportunities"],
  "marketing_recommendations": ["strategies"],
  "differentiation_factors": ["factors"],
  "market_confidence": 0.80
}""",
        description="Performs market and competitive analysis.",
        output_key="market_analysis",
    )

async def create_business_intelligence_agent() -> LlmAgent:
    """Creates agent for generating comprehensive business intelligence."""
    return LlmAgent(
        name="BusinessIntelligenceAgent",
        model="gemini-2.0-flash-exp",
        instruction="""Synthesize the business data and market analysis to create comprehensive business intelligence.

Business Data: {business_data}
Market Analysis: {market_analysis}

Generate a comprehensive business intelligence report:

1. Executive Summary
2. Business Overview
3. Market Position
4. Competitive Advantages
5. Target Audience Profile
6. Marketing Opportunities
7. Strategic Recommendations
8. Risk Assessment
9. Success Metrics

Format as structured JSON:
{
  "executive_summary": "concise overview",
  "business_overview": "detailed business description",
  "market_position": "market positioning",
  "competitive_advantages": ["advantages"],
  "target_audience_profile": "audience analysis",
  "marketing_opportunities": ["opportunities"],
  "strategic_recommendations": ["recommendations"],
  "risk_assessment": "risk analysis",
  "success_metrics": ["metrics"],
  "overall_confidence": 0.85
}""",
        description="Generates comprehensive business intelligence report.",
        output_key="business_intelligence",
    )

async def create_business_analysis_workflow() -> SequentialAgent:
    """Creates the complete business analysis workflow."""
    content_agent = await create_content_extraction_agent()
    market_agent = await create_market_analysis_agent()
    intelligence_agent = await create_business_intelligence_agent()

    return SequentialAgent(
        name="BusinessAnalysisWorkflow",
        sub_agents=[content_agent, market_agent, intelligence_agent],
        description="Complete business analysis workflow from URL content to business intelligence.",
    )

class BusinessAnalysisService:
    """Service for orchestrating business analysis using ADK agents."""
    
    def __init__(self):
        self.scraper = URLScrapingAgent()
        self.workflow_agent = None
    
    async def initialize(self):
        """Initialize the ADK workflow agent."""
        if not self.workflow_agent:
            self.workflow_agent = await create_business_analysis_workflow()
    
    async def analyze_urls(self, urls: List[str], analysis_depth: str = "standard") -> Dict[str, Any]:
        """Analyze business URLs and extract comprehensive business intelligence."""
        await self.initialize()
        
        context = BusinessAnalysisContext()
        context.urls = urls
        
        try:
            # Step 1: Scrape content from URLs
            logger.info(f"Scraping content from {len(urls)} URLs")
            scraping_tasks = [self.scraper.scrape_url(url) for url in urls]
            scraping_results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
            
            # Combine scraped content
            combined_content = ""
            url_insights = {}
            
            for result in scraping_results:
                if isinstance(result, dict) and result.get("status") == "success":
                    url = result["url"]
                    content = result["content"]
                    combined_content += f"\n\n--- Content from {url} ---\n{content}"
                    
                    url_insights[url] = {
                        "content_type": "business_website",
                        "title": result.get("title", ""),
                        "content_length": result.get("content_length", 0),
                        "status": "success"
                    }
                else:
                    url = result.get("url", "unknown") if isinstance(result, dict) else "unknown"
                    url_insights[url] = {
                        "status": "error",
                        "error": result.get("error", str(result)) if isinstance(result, dict) else str(result)
                    }
            
            if not combined_content.strip():
                raise ValueError("No content could be extracted from the provided URLs")
            
            # Step 2: Run ADK workflow for business analysis
            logger.info("Running ADK business analysis workflow")
            
            run_config = RunConfig()
            invocation_context = InvocationContext(
                inputs={"scraped_content": combined_content},
                run_config=run_config
            )
            
            # Execute the workflow
            result = await self.workflow_agent.run(invocation_context)
            
            # Extract results from workflow
            business_data = result.outputs.get("business_data", {})
            market_analysis = result.outputs.get("market_analysis", {})
            business_intelligence = result.outputs.get("business_intelligence", {})
            
            # Parse JSON responses if they're strings
            import json
            if isinstance(business_data, str):
                try:
                    business_data = json.loads(business_data)
                except json.JSONDecodeError:
                    business_data = {"error": "Failed to parse business data"}
            
            if isinstance(market_analysis, str):
                try:
                    market_analysis = json.loads(market_analysis)
                except json.JSONDecodeError:
                    market_analysis = {"error": "Failed to parse market analysis"}
            
            if isinstance(business_intelligence, str):
                try:
                    business_intelligence = json.loads(business_intelligence)
                except json.JSONDecodeError:
                    business_intelligence = {"error": "Failed to parse business intelligence"}
            
            # Calculate confidence score
            confidence_scores = [
                business_data.get("confidence", 0.5),
                market_analysis.get("market_confidence", 0.5),
                business_intelligence.get("overall_confidence", 0.5)
            ]
            overall_confidence = sum(confidence_scores) / len(confidence_scores)
            
            # Update URL insights with extracted topics
            for url in url_insights:
                if url_insights[url].get("status") == "success":
                    url_insights[url].update({
                        "key_topics": business_data.get("key_topics", []),
                        "confidence": business_data.get("confidence", 0.5),
                        "extracted_data": {
                            "company_info": business_data.get("company_name", ""),
                            "products_services": ", ".join(business_data.get("products_services", [])),
                            "contact_info": business_data.get("contact_info", "")
                        }
                    })
            
            return {
                "business_analysis": {
                    "company_name": business_data.get("company_name", "Unknown"),
                    "industry": business_data.get("industry", "Unknown"),
                    "target_audience": business_data.get("target_audience", "Unknown"),
                    "value_propositions": business_data.get("value_propositions", []),
                    "brand_voice": business_data.get("brand_voice", "Unknown"),
                    "competitive_advantages": business_data.get("competitive_advantages", []),
                    "market_positioning": market_analysis.get("market_positioning", "Unknown")
                },
                "url_insights": url_insights,
                "business_intelligence": business_intelligence,
                "confidence_score": overall_confidence,
                "processing_time": 5.0,  # Placeholder - would track actual time
                "analysis_metadata": {
                    "analysis_depth": analysis_depth,
                    "urls_processed": len(urls),
                    "successful_extractions": len([u for u in url_insights.values() if u.get("status") == "success"])
                }
            }
            
        except Exception as e:
            logger.error(f"Business analysis failed: {e}", exc_info=True)
            raise Exception(f"Business analysis failed: {str(e)}")

# Global service instance
business_analysis_service = BusinessAnalysisService() 