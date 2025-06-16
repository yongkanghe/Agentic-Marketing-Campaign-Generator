"""
FILENAME: business_analysis_agent.py
DESCRIPTION/PURPOSE: Business analysis agent with URL scraping and AI-powered context extraction
Author: JP + 2025-06-16
"""

import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os
from google import genai

logger = logging.getLogger(__name__)

class URLAnalysisAgent:
    """Agent for analyzing business URLs and extracting context."""
    
    def __init__(self):
        """Initialize URL analysis agent with Gemini client."""
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-preview-05-20')
        
        if self.gemini_api_key:
            try:
                self.client = genai.Client(api_key=self.gemini_api_key)
                logger.info(f"URL Analysis Agent initialized with Gemini model: {self.gemini_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            logger.warning("GEMINI_API_KEY not found - URL analysis will use mock responses")
            self.client = None
    
    async def analyze_urls(self, urls: List[str], analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze multiple URLs and extract business context.
        
        Args:
            urls: List of URLs to analyze
            analysis_type: Type of analysis (basic, standard, comprehensive)
            
        Returns:
            Dictionary containing extracted business context
        """
        try:
            logger.info(f"Starting {analysis_type} analysis of {len(urls)} URLs")
            
            # Scrape content from all URLs
            url_contents = {}
            async with aiohttp.ClientSession() as session:
                for url in urls:
                    try:
                        content = await self._scrape_url_content(session, url)
                        url_contents[url] = content
                        logger.info(f"Successfully scraped content from {url}")
                    except Exception as e:
                        logger.error(f"Failed to scrape {url}: {e}")
                        url_contents[url] = {"error": str(e)}
            
            # Analyze scraped content with AI
            if self.client and any(content.get('text') for content in url_contents.values()):
                business_context = await self._analyze_content_with_ai(url_contents, analysis_type)
            else:
                business_context = self._generate_enhanced_mock_analysis(url_contents, analysis_type)
            
            return {
                "business_analysis": business_context,
                "url_insights": url_contents,
                "analysis_metadata": {
                    "urls_analyzed": len(urls),
                    "successful_scrapes": len([c for c in url_contents.values() if 'text' in c]),
                    "analysis_type": analysis_type,
                    "ai_analysis_used": self.client is not None
                }
            }
            
        except Exception as e:
            logger.error(f"URL analysis failed: {e}", exc_info=True)
            return self._generate_fallback_analysis(urls)
    
    async def _scrape_url_content(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Scrape content from a single URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract key content elements
                    title = soup.find('title')
                    title_text = title.get_text().strip() if title else ""
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Extract main content
                    main_content = soup.get_text()
                    
                    # Clean up text
                    lines = (line.strip() for line in main_content.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    # Limit text length for AI analysis
                    text = text[:5000] if len(text) > 5000 else text
                    
                    # Extract meta information
                    meta_description = soup.find('meta', attrs={'name': 'description'})
                    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
                    
                    return {
                        "url": url,
                        "title": title_text,
                        "text": text,
                        "meta_description": meta_description.get('content', '') if meta_description else '',
                        "meta_keywords": meta_keywords.get('content', '') if meta_keywords else '',
                        "word_count": len(text.split()),
                        "status": "success"
                    }
                else:
                    return {
                        "url": url,
                        "error": f"HTTP {response.status}",
                        "status": "failed"
                    }
                    
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "status": "failed"
            }
    
    async def _analyze_content_with_ai(self, url_contents: Dict[str, Dict], analysis_type: str) -> Dict[str, Any]:
        """Analyze scraped content using Gemini AI."""
        try:
            # Prepare content for AI analysis
            analysis_prompt = self._build_analysis_prompt(url_contents, analysis_type)
            
            # Generate AI analysis
            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=analysis_prompt
            )
            
            # Parse AI response into structured format
            ai_analysis = response.text
            
            # Extract structured information from AI response
            business_context = self._parse_ai_analysis(ai_analysis, url_contents)
            
            logger.info("Successfully completed AI-powered business analysis")
            return business_context
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._generate_enhanced_mock_analysis(url_contents, analysis_type)
    
    def _build_analysis_prompt(self, url_contents: Dict[str, Dict], analysis_type: str) -> str:
        """Build comprehensive analysis prompt for Gemini."""
        
        content_summary = ""
        for url, content in url_contents.items():
            if content.get('text'):
                content_summary += f"\n\nURL: {url}\n"
                content_summary += f"Title: {content.get('title', 'N/A')}\n"
                content_summary += f"Content: {content['text'][:1000]}...\n"
        
        prompt = f"""
        As a business intelligence analyst and creative director, analyze the following website content and extract comprehensive business context with detailed CAMPAIGN GUIDANCE for visual content generation:

        {content_summary}

        Please provide a detailed analysis in the following JSON-like structure:

        {{
            "company_name": "extracted company name",
            "industry": "primary industry/sector",
            "business_model": "B2B/B2C/marketplace/etc",
            "target_audience": "primary target audience description",
            "value_propositions": ["key value prop 1", "key value prop 2", "key value prop 3"],
            "products_services": ["main product/service 1", "main product/service 2"],
            "brand_voice": "professional/casual/innovative/etc",
            "competitive_advantages": ["advantage 1", "advantage 2", "advantage 3"],
            "market_positioning": "positioning statement",
            "key_themes": ["theme 1", "theme 2", "theme 3"],
            "business_objectives": ["likely objective 1", "likely objective 2"],
            "content_style": "description of content style and tone",
            "visual_elements": "description of visual branding elements mentioned",
            
            "campaign_guidance": {{
                "creative_direction": "2-3 sentences describing the overall creative vision and aesthetic approach for this campaign",
                "visual_style": {{
                    "photography_style": "specific photography approach (portrait, lifestyle, product, architectural, etc.)",
                    "color_palette": ["primary color", "secondary color", "accent color"],
                    "lighting": "lighting style (natural, studio, dramatic, soft, etc.)",
                    "composition": "composition approach (close-up, wide-angle, macro, etc.)",
                    "mood": "overall mood and feeling (professional, energetic, calm, innovative, etc.)"
                }},
                "imagen_prompts": {{
                    "base_prompt": "Core visual prompt template following Imagen best practices",
                    "style_modifiers": ["photography style", "lens type", "lighting condition"],
                    "subject_focus": "primary subject matter for images",
                    "environment": "typical environment/setting for visuals",
                    "technical_specs": "camera settings, focal length, etc."
                }},
                "veo_prompts": {{
                    "base_prompt": "Core video concept template following Veo best practices", 
                    "movement_style": "camera movement and subject motion",
                    "scene_composition": "how scenes should be structured",
                    "duration_focus": "short-form optimized approach",
                    "storytelling": "narrative approach for video content"
                }},
                "content_themes": {{
                    "primary_themes": ["main theme 1", "main theme 2", "main theme 3"],
                    "visual_metaphors": ["metaphor 1", "metaphor 2"],
                    "emotional_triggers": ["emotion 1", "emotion 2", "emotion 3"],
                    "call_to_action_style": "approach for CTAs (urgent, informative, inspiring, etc.)"
                }},
                "brand_consistency": {{
                    "logo_placement": "guidelines for logo/brand element placement",
                    "typography": "font style and text overlay approach",
                    "brand_colors": "how to incorporate brand colors",
                    "messaging_tone": "consistent voice across all content"
                }}
            }}
        }}

        CRITICAL: The campaign_guidance section should provide specific, actionable direction that follows Google's Imagen and Veo prompt engineering best practices. This will be used to generate consistent, high-quality visual content across all social media posts.

        Focus on extracting actionable insights for marketing campaign generation. Be specific and detailed.
        """
        
        return prompt
    
    def _parse_ai_analysis(self, ai_response: str, url_contents: Dict[str, Dict]) -> Dict[str, Any]:
        """Parse AI analysis response into structured business context."""
        try:
            # Try to extract JSON-like structure from AI response
            import json
            import re
            
            # Look for JSON-like content in the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    parsed_data = json.loads(json_match.group())
                    return parsed_data
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Parse key information manually
            business_context = {
                "company_name": self._extract_field(ai_response, "company_name"),
                "industry": self._extract_field(ai_response, "industry"),
                "business_model": self._extract_field(ai_response, "business_model"),
                "target_audience": self._extract_field(ai_response, "target_audience"),
                "value_propositions": self._extract_list_field(ai_response, "value_propositions"),
                "products_services": self._extract_list_field(ai_response, "products_services"),
                "brand_voice": self._extract_field(ai_response, "brand_voice"),
                "competitive_advantages": self._extract_list_field(ai_response, "competitive_advantages"),
                "market_positioning": self._extract_field(ai_response, "market_positioning"),
                "key_themes": self._extract_list_field(ai_response, "key_themes"),
                "business_objectives": self._extract_list_field(ai_response, "business_objectives"),
                "content_style": self._extract_field(ai_response, "content_style"),
                "visual_elements": self._extract_field(ai_response, "visual_elements"),
                "campaign_guidance": self._extract_campaign_guidance(ai_response)
            }
            
            return business_context
            
        except Exception as e:
            logger.error(f"Failed to parse AI analysis: {e}")
            return self._generate_enhanced_mock_analysis(url_contents, "comprehensive")
    
    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a single field value from AI response."""
        import re
        pattern = rf'"{field_name}":\s*"([^"]*)"'
        match = re.search(pattern, text)
        return match.group(1) if match else ""
    
    def _extract_list_field(self, text: str, field_name: str) -> List[str]:
        """Extract a list field value from AI response."""
        import re
        pattern = rf'"{field_name}":\s*\[(.*?)\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            items_text = match.group(1)
            items = re.findall(r'"([^"]*)"', items_text)
            return items
        return []
    
    def _extract_campaign_guidance(self, text: str) -> Dict[str, Any]:
        """Extract campaign guidance from AI response."""
        try:
            import re
            import json
            
            # Try to extract campaign_guidance JSON block
            guidance_pattern = r'"campaign_guidance":\s*\{(.*?)\}\s*\}'
            match = re.search(guidance_pattern, text, re.DOTALL)
            
            if match:
                guidance_json = "{" + match.group(1) + "}"
                try:
                    return json.loads(guidance_json)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Generate basic campaign guidance
            return self._generate_fallback_campaign_guidance(text)
            
        except Exception as e:
            logger.error(f"Failed to extract campaign guidance: {e}")
            return self._generate_fallback_campaign_guidance(text)
    
    def _generate_fallback_campaign_guidance(self, analysis_text: str) -> Dict[str, Any]:
        """Generate fallback campaign guidance based on analysis."""
        
        # Analyze content for industry and style cues
        text_lower = analysis_text.lower()
        
        # Determine photography style based on industry
        if any(word in text_lower for word in ['tech', 'software', 'digital', 'app']):
            photography_style = "modern tech lifestyle"
            environment = "modern office, clean workspace, digital interfaces"
            mood = "innovative, professional, forward-thinking"
        elif any(word in text_lower for word in ['food', 'restaurant', 'cafe', 'dining']):
            photography_style = "food and lifestyle photography"
            environment = "restaurant setting, kitchen, dining atmosphere"
            mood = "appetizing, warm, inviting"
        elif any(word in text_lower for word in ['fitness', 'health', 'wellness', 'gym']):
            photography_style = "fitness and lifestyle"
            environment = "gym, outdoor fitness, active lifestyle"
            mood = "energetic, motivating, healthy"
        elif any(word in text_lower for word in ['fashion', 'clothing', 'apparel', 'style']):
            photography_style = "fashion and portrait"
            environment = "studio, lifestyle settings, fashion contexts"
            mood = "stylish, trendy, aspirational"
        else:
            photography_style = "professional lifestyle"
            environment = "business setting, professional context"
            mood = "professional, trustworthy, competent"
        
        return {
            "creative_direction": f"Create visually compelling content that showcases the brand's {mood} personality through {photography_style} imagery, emphasizing authenticity and connection with the target audience.",
            "visual_style": {
                "photography_style": photography_style,
                "color_palette": ["#2563eb", "#64748b", "#f8fafc"],
                "lighting": "natural, soft lighting with professional quality",
                "composition": "clean, modern composition with focus on subject",
                "mood": mood
            },
            "imagen_prompts": {
                "base_prompt": f"Professional {photography_style}, {environment}, high quality, well-lit",
                "style_modifiers": ["35mm lens", "natural lighting", "professional photography"],
                "subject_focus": "people using product/service in real scenarios",
                "environment": environment,
                "technical_specs": "35mm lens, f/2.8, natural lighting, high resolution"
            },
            "veo_prompts": {
                "base_prompt": f"Dynamic {photography_style} video showing real people engaging with the brand",
                "movement_style": "smooth camera movements, natural subject motion",
                "scene_composition": "multiple quick cuts, engaging transitions",
                "duration_focus": "15-30 second social media optimized clips",
                "storytelling": "problem-solution narrative with emotional connection"
            },
            "content_themes": {
                "primary_themes": ["authenticity", "results", "community"],
                "visual_metaphors": ["growth", "transformation", "connection"],
                "emotional_triggers": ["aspiration", "trust", "excitement"],
                "call_to_action_style": "inspiring and action-oriented"
            },
            "brand_consistency": {
                "logo_placement": "subtle, bottom-right or integrated naturally",
                "typography": "clean, modern sans-serif fonts",
                "brand_colors": "consistent color palette across all content",
                "messaging_tone": "professional yet approachable"
            }
        }
    
    def _generate_enhanced_mock_analysis(self, url_contents: Dict[str, Dict], analysis_type: str) -> Dict[str, Any]:
        """Generate enhanced mock analysis based on scraped content."""
        
        # Extract basic information from scraped content
        all_text = ""
        company_name = "Your Company"
        
        for url, content in url_contents.items():
            if content.get('text'):
                all_text += content['text'] + " "
                
                # Try to extract company name from title or content
                title = content.get('title', '')
                if title and len(title.split()) <= 3:
                    company_name = title.split(' - ')[0].split(' | ')[0]
        
        # Analyze content themes
        themes = []
        text_lower = all_text.lower()
        
        if any(word in text_lower for word in ['innovative', 'innovation', 'cutting-edge', 'advanced']):
            themes.append('innovation')
        if any(word in text_lower for word in ['quality', 'premium', 'excellence', 'professional']):
            themes.append('quality')
        if any(word in text_lower for word in ['customer', 'client', 'service', 'support']):
            themes.append('customer-focused')
        if any(word in text_lower for word in ['technology', 'tech', 'digital', 'software']):
            themes.append('technology')
        if any(word in text_lower for word in ['sustainable', 'eco', 'green', 'environment']):
            themes.append('sustainability')
        
        return {
            "company_name": company_name,
            "industry": "Technology Services" if 'technology' in themes else "Professional Services",
            "business_model": "B2B" if any(word in text_lower for word in ['business', 'enterprise', 'corporate']) else "B2C",
            "target_audience": "Business professionals and decision makers",
            "value_propositions": [
                f"Innovative solutions for {company_name}",
                "Proven track record of success",
                "Customer-centric approach"
            ],
            "products_services": [
                "Core service offering",
                "Consulting and advisory",
                "Custom solutions"
            ],
            "brand_voice": "Professional and innovative",
            "competitive_advantages": [
                "Industry expertise",
                "Innovative approach",
                "Strong customer relationships"
            ],
            "market_positioning": f"{company_name} - Leading provider of innovative solutions",
            "key_themes": themes,
            "business_objectives": [
                "Increase market share",
                "Expand customer base",
                "Drive innovation"
            ],
            "content_style": "Professional, informative, and engaging",
            "visual_elements": "Modern, clean design with professional imagery",
            "campaign_guidance": self._generate_fallback_campaign_guidance(all_text)
        }
    
    def _generate_fallback_analysis(self, urls: List[str]) -> Dict[str, Any]:
        """Generate fallback analysis when URL scraping fails."""
        return {
            "business_analysis": {
                "company_name": "Your Company",
                "industry": "Professional Services",
                "target_audience": "Business professionals",
                "value_propositions": ["Quality service delivery", "Customer satisfaction", "Innovation"],
                "brand_voice": "Professional",
                "competitive_advantages": ["Experience", "Quality", "Service"],
                "market_positioning": "Trusted service provider"
            },
            "url_insights": {url: {"error": "Analysis unavailable"} for url in urls},
            "analysis_metadata": {
                "urls_analyzed": len(urls),
                "successful_scrapes": 0,
                "analysis_type": "fallback",
                "ai_analysis_used": False
            }
        }

# Export for use in other modules
async def analyze_business_urls(urls: List[str], analysis_type: str = "comprehensive") -> Dict[str, Any]:
    """Convenience function for URL analysis."""
    agent = URLAnalysisAgent()
    return await agent.analyze_urls(urls, analysis_type) 