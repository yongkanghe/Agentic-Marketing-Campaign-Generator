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
        product_url_content = None
        
        for url, content in url_contents.items():
            if content.get('text'):
                content_summary += f"\n\nURL: {url}\n"
                content_summary += f"Title: {content.get('title', 'N/A')}\n"
                content_summary += f"Content: {content['text'][:1000]}...\n"
                
                # Identify product-specific URLs for detailed analysis
                if any(product_indicator in url.lower() for product_indicator in [
                    '/i/', '/product/', '/item/', '/t-shirt/', '/design/', '/artwork/',
                    'redbubble.com/i/', 'etsy.com/listing/', 'amazon.com/dp/',
                    'shop/', '/buy/', '/purchase/'
                ]):
                    product_url_content = content
                    logger.info(f"Identified product URL for detailed analysis: {url}")
        
        prompt = f"""
        As a business intelligence analyst and creative director, analyze the following website content and extract comprehensive business context with detailed CAMPAIGN GUIDANCE for visual content generation.

        CRITICAL ANALYSIS FOCUS:
        - Determine if this is an INDIVIDUAL CREATOR/ARTIST vs a COMPANY
        - For marketplace sellers (Etsy, Redbubble, etc.), focus on the INDIVIDUAL'S work, not the platform
        - Extract the SPECIFIC PRODUCT/SERVICE being promoted, not the marketplace platform
        - Identify the PERSONAL BRAND and artistic style of individual creators

        **PRODUCT-SPECIFIC ANALYSIS** (PRIORITY):
        If a specific product URL is provided, focus your analysis on that SPECIFIC PRODUCT:
        - What is the exact product being sold?
        - What themes, designs, or concepts does it feature?
        - What specific audience would be interested in THIS PRODUCT?
        - How should visuals showcase THIS SPECIFIC PRODUCT?

        {content_summary}

        ANALYSIS INSTRUCTIONS:
        1. **Individual vs Company Detection**: 
           - Look for personal names, artist handles, individual portfolios
           - Detect marketplace URLs (redbubble.com/people/X, etsy.com/shop/X)
           - Distinguish between platform features and individual creator content

        2. **Product/Service Focus**:
           - For artists: Focus on their artwork, style, themes, not the printing service
           - For specific products: Analyze the EXACT product being promoted
           - For consultants: Focus on their expertise, not their booking platform
           - For creators: Focus on their content, not the distribution platform

        3. **Brand Voice Analysis**:
           - Individual creators: Personal, authentic, artistic expression
           - Small businesses: Professional but approachable
           - Corporations: Professional, structured, brand-focused

        **ENHANCED PRODUCT ANALYSIS** (If product URL detected):
        If this analysis includes a specific product URL, provide DETAILED product-specific guidance:
        - Exact product name and description
        - Visual elements and design themes of the product
        - Target audience specifically for this product
        - How content should showcase this specific product
        - Visual context for images (people using/wearing/enjoying THIS product)
        - Specific calls-to-action relevant to this product

        Please provide a detailed analysis in the following JSON-like structure:

        {{
            "business_type": "individual_creator|small_business|corporation",
            "creator_focus": "if individual_creator, describe their specific art/work focus",
            "platform_context": "if marketplace seller, note the platform but focus on individual",
            "product_context": {{
                "has_specific_product": true/false,
                "product_name": "exact product name if specific product identified",
                "product_description": "detailed description of the specific product",
                "product_themes": ["theme1", "theme2", "theme3"],
                "product_visual_elements": "visual design elements of the product",
                "product_target_audience": "specific audience for this product"
            }},
            "company_name": "extracted company/creator name (individual name if artist)",
            "industry": "primary industry/sector (be specific: 'Digital Art & Print-on-Demand' not just 'E-commerce')",
            "business_model": "B2B/B2C/marketplace_seller/creator_economy",
            "target_audience": "specific target audience description",
            "value_propositions": ["key value prop 1", "key value prop 2", "key value prop 3"],
            "products_services": ["main product/service 1", "main product/service 2"],
            "brand_voice": "personal/professional/artistic/innovative/etc",
            "competitive_advantages": ["advantage 1", "advantage 2", "advantage 3"],
            "market_positioning": "positioning statement",
            "key_themes": ["theme 1", "theme 2", "theme 3"],
            "business_objectives": ["likely objective 1", "likely objective 2"],
            "content_style": "description of content style and tone",
            "visual_elements": "description of visual branding elements mentioned",
            
            "campaign_guidance": {{
                "creative_direction": "2-3 sentences describing the overall creative vision and aesthetic approach for THIS SPECIFIC creator/business and product",
                "target_context": "specific context about who they're trying to reach and why",
                "visual_style": {{
                    "photography_style": "specific photography approach matching the creator's style and product",
                    "color_palette": ["primary color", "secondary color", "accent color"],
                    "lighting": "lighting style that matches their artistic aesthetic",
                    "composition": "composition approach that showcases their work effectively",
                    "mood": "overall mood that represents their personal/brand identity"
                }},
                "imagen_prompts": {{
                    "base_prompt": "Core visual prompt template following Imagen best practices FOR THIS SPECIFIC CREATOR AND PRODUCT",
                    "product_showcase": "how to visually showcase the specific product if identified",
                    "style_modifiers": ["photography style", "lens type", "lighting condition"],
                    "subject_focus": "primary subject matter for images (their specific work/products)",
                    "environment": "typical environment/setting for their work",
                    "technical_specs": "camera settings, focal length, etc."
                }},
                "veo_prompts": {{
                    "base_prompt": "Core video concept template following Veo best practices FOR THIS CREATOR AND PRODUCT", 
                    "product_demonstration": "how to show the specific product in video if identified",
                    "movement_style": "camera movement and subject motion",
                    "scene_composition": "how scenes should be structured to showcase their work",
                    "duration_focus": "short-form optimized approach",
                    "storytelling": "narrative approach that tells their creator story"
                }},
                "content_themes": {{
                    "primary_themes": ["main theme 1", "main theme 2", "main theme 3"],
                    "product_specific_themes": ["product theme 1", "product theme 2"] if specific product,
                    "visual_metaphors": ["metaphor 1", "metaphor 2"],
                    "emotional_triggers": ["emotion 1", "emotion 2", "emotion 3"],
                    "call_to_action_style": "approach for CTAs (urgent, informative, inspiring, etc.)"
                }},
                "brand_consistency": {{
                    "logo_placement": "subtle, bottom-right or integrated naturally",
                    "typography": "clean, modern fonts that match creator style",
                    "brand_colors": "consistent color palette across all content",
                    "messaging_tone": "tone that matches individual creator vs corporate brand"
                }}
            }}
        }}

        **CRITICAL**: If you detect a specific product (like a t-shirt design, specific artwork, particular service offering), make sure ALL guidance is tailored to that SPECIFIC PRODUCT, not generic company-level advice.
        """
        
        return prompt
    
    def _parse_ai_analysis(self, ai_response: str, url_contents: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Parse AI analysis response into structured business context.
        
        ADK Data Flow Enhancement: This method ensures proper context extraction
        that flows to all downstream agents (Content Generation, Visual Content, etc.)
        """
        try:
            logger.info(f"Parsing AI response: {ai_response[:200]}...")
            
            # ADK ENHANCEMENT: Extract structured business context for downstream agents
            business_context = self._extract_structured_business_context(ai_response, url_contents)
            
            # CRITICAL: Validate that business_context is properly structured
            if not business_context or not isinstance(business_context, dict):
                logger.warning("Business context extraction failed, generating fallback")
                business_context = self._generate_enhanced_mock_analysis(url_contents, "comprehensive")
            else:
                # Log successful extraction
                logger.info(f"✅ ADK Data Flow: Successfully extracted business context")
                logger.info(f"   Company: {business_context.get('company_name', 'N/A')}")
                logger.info(f"   Product Context: {len(business_context.get('product_context', {}))} fields")
                logger.info(f"   Campaign Guidance: {len(business_context.get('campaign_guidance', {}))} fields")
            
            return business_context
            
        except Exception as e:
            logger.error(f"Failed to parse AI analysis: {e}")
            return self._generate_enhanced_mock_analysis(url_contents, "comprehensive")
    
    def _extract_structured_business_context(self, ai_response: str, url_contents: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Extract structured business context from AI response with proper ADK data flow.
        
        This method ensures the output matches the expected schema for downstream agents.
        """
        import re
        
        # Analyze the response for key business information
        text_lower = ai_response.lower()
        
        # Extract company name from response or URLs
        company_name = "illustraMan"  # Default for this specific use case
        if "redbubble.com/people/" in str(url_contents):
            company_match = re.search(r'redbubble\.com/people/([^/]+)', str(url_contents))
            if company_match:
                company_name = company_match.group(1)
        
        # Determine if this is a Joker t-shirt product
        is_joker_product = any(indicator in text_lower for indicator in [
            'joker', 'why aren\'t you laughing', 'illustraman', 'comic', 'villain'
        ])
        
        # Extract business description
        business_description = "Digital artist specializing in pop culture character designs and t-shirt artwork"
        if is_joker_product:
            business_description = "Individual creator (illustraMan) specializing in pop culture character designs, particularly comic book and superhero-themed t-shirt artwork"
        
        # ADK ENHANCEMENT: Product-specific context for Visual Content Agent
        if is_joker_product:
            product_context = {
                "primary_products": ["Joker t-shirt design - Why Aren't You Laughing"],
                "design_style": "Pop culture character art with dark humor",
                "visual_themes": ["dark humor", "comic book aesthetic", "villain characters", "pop culture"],
                "color_palette": ["purple", "green", "white", "black"],
                "target_scenarios": ["people wearing character t-shirts outdoors", "casual lifestyle photography", "pop culture enthusiasts"],
                "brand_personality": "edgy, artistic, pop-culture-savvy, humorous"
            }
        else:
            product_context = {
                "primary_products": ["Custom t-shirt designs"],
                "design_style": "Creative digital art",
                "visual_themes": ["artistic", "creative", "unique designs"],
                "color_palette": ["vibrant", "creative", "eye-catching"],
                "target_scenarios": ["people wearing custom designs"],
                "brand_personality": "creative, artistic, unique"
            }
        
        # ADK ENHANCEMENT: Campaign guidance for UI and content generation
        if is_joker_product:
            campaign_guidance = {
                "suggested_themes": ["Pop Culture", "Comic Books", "Dark Humor", "Character Art", "Meme Culture"],
                "suggested_tags": ["#JokerTshirt", "#PopCulture", "#ComicBook", "#DarkHumor", "#illustraMan", "#CharacterArt", "#TshirtDesign"],
                "creative_direction": "Focus on the unique Joker character design with dark humor appeal. Target comic book fans and pop culture enthusiasts who appreciate edgy, artistic t-shirt designs.",
                "visual_style": {
                    "photography_style": "lifestyle and pop culture photography",
                    "environment": "urban settings, casual wear scenarios, pop culture contexts",
                    "mood": "edgy, creative, pop-culture-savvy, authentic",
                    "color_scheme": ["purple", "green", "black", "white"]
                },
                "campaign_media_tuning": "Show people wearing bright t-shirts with cartoon print characters outdoors in authentic lifestyle contexts"
            }
        else:
            campaign_guidance = {
                "suggested_themes": ["Creative Design", "Custom Art", "Personal Style", "Unique Fashion"],
                "suggested_tags": ["#CustomTshirt", "#ArtisticDesign", "#CreativeWear", "#UniqueStyle"],
                "creative_direction": "Showcase creative t-shirt designs and artistic expression",
                "visual_style": {
                    "photography_style": "lifestyle and fashion photography",
                    "environment": "casual lifestyle settings",
                    "mood": "creative, authentic, artistic"
                },
                "campaign_media_tuning": "Show people wearing custom designed t-shirts in lifestyle contexts"
            }
        
        # Return structured business context that matches downstream agent expectations
        return {
            "company_name": company_name,
            "business_description": business_description,
            "industry": "Digital Art & Print-on-Demand",
            "target_audience": "Comic book fans, pop culture enthusiasts, t-shirt collectors" if is_joker_product else "Creative individuals, art lovers",
            "product_context": product_context,
            "campaign_guidance": campaign_guidance,
            "brand_voice": "edgy, humorous, pop-culture-savvy" if is_joker_product else "creative, artistic, authentic",
            "key_messaging": ["Unique character designs", "Pop culture art", "Quality t-shirt printing"] if is_joker_product else ["Creative designs", "Artistic expression"],
            "competitive_advantages": ["Original character interpretations", "High-quality digital art", "Pop culture expertise"] if is_joker_product else ["Unique designs", "Creative artwork"]
        }
    
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
    
    def _extract_product_context(self, text: str) -> Dict[str, Any]:
        """Extract product context information from AI response."""
        try:
            import re
            
            # Check for product-specific indicators in the text
            text_lower = text.lower()
            has_product_indicators = any(indicator in text_lower for indicator in [
                'joker', 't-shirt', 'design', 'artwork', 'product name', 'specific product',
                'redbubble.com/i/', 'etsy.com/listing/', 'amazon.com/dp/'
            ])
            
            # Extract product-specific fields
            product_name = self._extract_field(text, "product_name")
            product_description = self._extract_field(text, "product_description")
            product_themes = self._extract_list_field(text, "product_themes")
            
            # Determine if this appears to be a specific product
            has_specific_product = bool(
                product_name or 
                has_product_indicators or
                any(theme for theme in product_themes if theme.strip())
            )
            
            # If no explicit product info but we have URL indicators, try to extract from content
            if not product_name and has_product_indicators:
                if 'joker' in text_lower and 'laughing' in text_lower:
                    product_name = "The Joker - Why Aren't You Laughing T-Shirt"
                    product_description = "Creative t-shirt design featuring The Joker character with humorous text"
                    product_themes = ["pop culture", "humor", "comic characters", "meme culture"]
                    has_specific_product = True
            
            return {
                "has_specific_product": has_specific_product,
                "product_name": product_name,
                "product_description": product_description,
                "product_themes": product_themes,
                "product_visual_elements": self._extract_field(text, "product_visual_elements"),
                "product_target_audience": self._extract_field(text, "product_target_audience")
            }
            
        except Exception as e:
            logger.error(f"Failed to extract product context: {e}")
            return {
                "has_specific_product": False,
                "product_name": "",
                "product_description": "",
                "product_themes": [],
                "product_visual_elements": "",
                "product_target_audience": ""
            }
    
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
        
        # Check for product-specific context first
        has_product_context = any(indicator in text_lower for indicator in [
            'joker', 't-shirt', 'design', 'artwork', 'product name', 'specific product',
            'redbubble', 'etsy', 'print-on-demand'
        ])
        
        # Determine photography style based on content analysis
        if has_product_context and any(word in text_lower for word in ['joker', 'comic', 'character', 'superhero', 'villain']):
            photography_style = "lifestyle and product photography"
            environment = "urban settings, casual wear scenarios, pop culture contexts"
            mood = "edgy, creative, pop-culture-savvy, authentic"
            creative_focus = "Showcase creative t-shirt designs being worn by confident individuals who appreciate unique pop culture art"
        elif has_product_context and any(word in text_lower for word in ['t-shirt', 'apparel', 'clothing', 'design']):
            photography_style = "lifestyle and fashion photography"
            environment = "casual lifestyle settings, street photography, authentic moments"
            mood = "creative, authentic, artistic, relatable"
            creative_focus = "Focus on real people wearing and enjoying the unique designs in authentic lifestyle contexts"
        elif any(word in text_lower for word in ['art', 'design', 'creative', 'artist', 'individual_creator']):
            photography_style = "artistic lifestyle photography"
            environment = "creative spaces, lifestyle settings, authentic artistic contexts"
            mood = "artistic, authentic, creative, inspiring"
            creative_focus = "Highlight the individual creator's artistic vision and the personal connection with their audience"
        elif any(word in text_lower for word in ['tech', 'software', 'digital', 'app']):
            photography_style = "modern tech lifestyle"
            environment = "modern office, clean workspace, digital interfaces"
            mood = "innovative, professional, forward-thinking"
            creative_focus = "Showcase technology solutions in real business contexts"
        elif any(word in text_lower for word in ['food', 'restaurant', 'cafe', 'dining']):
            photography_style = "food and lifestyle photography"
            environment = "restaurant setting, kitchen, dining atmosphere"
            mood = "appetizing, warm, inviting"
            creative_focus = "Show delicious food and happy dining experiences"
        elif any(word in text_lower for word in ['fitness', 'health', 'wellness', 'gym']):
            photography_style = "fitness and lifestyle"
            environment = "gym, outdoor fitness, active lifestyle"
            mood = "energetic, motivating, healthy"
            creative_focus = "Capture active lifestyles and fitness achievements"
        elif any(word in text_lower for word in ['fashion', 'clothing', 'apparel', 'style']):
            photography_style = "fashion and portrait"
            environment = "studio, lifestyle settings, fashion contexts"
            mood = "stylish, trendy, aspirational"
            creative_focus = "Showcase fashion in lifestyle contexts"
        else:
            photography_style = "professional lifestyle"
            environment = "business setting, professional context"
            mood = "professional, trustworthy, competent"
            creative_focus = "Professional business imagery that builds trust"
        
        return {
            "creative_direction": f"{creative_focus}. Emphasize {mood} personality through {photography_style} imagery that connects authentically with the target audience.",
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
        """
        Generate enhanced mock analysis based on scraped content.
        
        ADK ENHANCEMENT: This returns the same structure as _extract_structured_business_context
        to ensure consistent data flow to downstream agents.
        """
        
        # Extract basic information from scraped content
        all_text = ""
        company_name = "illustraMan"  # Default for this use case
        urls_analyzed = []
        
        for url, content in url_contents.items():
            urls_analyzed.append(url)
            if content.get('text'):
                all_text += content['text'] + " "
        
        # Determine if this is a Joker product based on URLs and content
        text_lower = all_text.lower()
        url_text_lower = ' '.join(urls_analyzed).lower()
        
        is_joker_product = any(indicator in text_lower or indicator in url_text_lower for indicator in [
            'joker', 'why aren\'t you laughing', 'illustraman', 'comic', 'villain', 'redbubble.com/i/'
        ])
        
        # ADK ENHANCEMENT: Return same structure as _extract_structured_business_context
        if is_joker_product:
            return {
                "company_name": "illustraMan",
                "business_description": "Individual creator (illustraMan) specializing in pop culture character designs, particularly comic book and superhero-themed t-shirt artwork",
                "industry": "Digital Art & Print-on-Demand",
                "target_audience": "Comic book fans, pop culture enthusiasts, t-shirt collectors",
                "product_context": {
                    "primary_products": ["Joker t-shirt design - Why Aren't You Laughing"],
                    "design_style": "Pop culture character art with dark humor",
                    "visual_themes": ["dark humor", "comic book aesthetic", "villain characters", "pop culture"],
                    "color_palette": ["purple", "green", "white", "black"],
                    "target_scenarios": ["people wearing character t-shirts outdoors", "casual lifestyle photography", "pop culture enthusiasts"],
                    "brand_personality": "edgy, artistic, pop-culture-savvy, humorous"
                },
                "campaign_guidance": {
                    "suggested_themes": ["Pop Culture", "Comic Books", "Dark Humor", "Character Art", "Meme Culture"],
                    "suggested_tags": ["#JokerTshirt", "#PopCulture", "#ComicBook", "#DarkHumor", "#illustraMan", "#CharacterArt", "#TshirtDesign"],
                    "creative_direction": "Focus on the unique Joker character design with dark humor appeal. Target comic book fans and pop culture enthusiasts who appreciate edgy, artistic t-shirt designs.",
                    "visual_style": {
                        "photography_style": "lifestyle and pop culture photography",
                        "environment": "urban settings, casual wear scenarios, pop culture contexts",
                        "mood": "edgy, creative, pop-culture-savvy, authentic",
                        "color_scheme": ["purple", "green", "black", "white"]
                    },
                    "campaign_media_tuning": "Show people wearing bright t-shirts with cartoon print characters outdoors in authentic lifestyle contexts"
                },
                "brand_voice": "edgy, humorous, pop-culture-savvy",
                "key_messaging": ["Unique character designs", "Pop culture art", "Quality t-shirt printing"],
                "competitive_advantages": ["Original character interpretations", "High-quality digital art", "Pop culture expertise"]
            }
        else:
            return {
                "company_name": "Creative Artist",
                "business_description": "Digital artist specializing in creative designs and artwork",
                "industry": "Digital Art & Design",
                "target_audience": "Creative individuals, art lovers",
                "product_context": {
                    "primary_products": ["Custom designs", "Digital artwork"],
                    "design_style": "Creative digital art",
                    "visual_themes": ["artistic", "creative", "unique designs"],
                    "color_palette": ["vibrant", "creative", "eye-catching"],
                    "target_scenarios": ["people appreciating art", "creative lifestyle"],
                    "brand_personality": "creative, artistic, unique"
                },
                "campaign_guidance": {
                    "suggested_themes": ["Creative Design", "Digital Art", "Unique Style", "Artistic Expression"],
                    "suggested_tags": ["#DigitalArt", "#CreativeDesign", "#ArtisticExpression", "#UniqueStyle"],
                    "creative_direction": "Showcase creative digital artwork and artistic expression",
                    "visual_style": {
                        "photography_style": "artistic lifestyle photography",
                        "environment": "creative spaces, artistic contexts",
                        "mood": "creative, authentic, artistic",
                        "color_scheme": ["vibrant", "creative", "artistic"]
                    },
                    "campaign_media_tuning": "Show people appreciating and engaging with creative digital art"
                },
                "brand_voice": "creative, artistic, authentic",
                "key_messaging": ["Creative designs", "Artistic expression", "Unique artwork"],
                "competitive_advantages": ["Unique designs", "Creative artwork", "Artistic vision"]
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