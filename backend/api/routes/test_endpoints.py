"""
FILENAME: test_endpoints.py
DESCRIPTION/PURPOSE: Test-friendly API endpoints for quick validation
Author: JP + 2025-06-22

This module provides simplified endpoints for testing that bypass complex validation
and external API calls, allowing for fast test execution.
"""

from fastapi import APIRouter
from typing import Dict, Any
import time
import json

router = APIRouter()

@router.post("/test/url-analysis")
async def test_url_analysis(request: Dict[str, Any]):
    """Test-friendly URL analysis endpoint with realistic Joker T-shirt response."""
    urls = request.get("urls", ["https://example.com"])
    
    # Check campaign type based on URLs
    is_joker_campaign = any("joker" in url.lower() or "illustraman" in url.lower() for url in urls)
    is_evre_campaign = any("evre" in url.lower() or "amzn.to" in url.lower() or "amazon" in url.lower() for url in urls)
    
    if is_joker_campaign:
        return {
            "success": True,
            "business_analysis": {
                "company_name": "illustraMan",
                "industry": "Digital Art & Print-on-Demand",
                "business_type": "individual_creator",
                "target_audience": "Pop culture enthusiasts, comic book fans, art collectors, young adults 18-35",
                "brand_voice": "Creative, artistic, humorous, pop culture-aware",
                "value_propositions": [
                    "Unique artistic t-shirt designs",
                    "Pop culture and comic book themes",
                    "High-quality digital art prints"
                ],
                "product_context": {
                    "has_specific_product": True,
                    "product_name": "The Joker - Why Aren't You Laughing T-shirt",
                    "product_themes": ["Comic book art", "Joker character", "Dark humor", "Pop culture"],
                    "product_visual_elements": "Joker character artwork with artistic styling"
                }
            },
            "url_insights": {
                "primary_url": urls[0],
                "analysis_depth": request.get("analysis_depth", "standard"),
                "confidence_score": 0.92
            },
            "suggested_themes": ["Artistic", "Bold", "Pop Culture", "Creative", "Vibrant"],
            "suggested_tags": ["#Joker", "#TShirt", "#Art", "#PopCulture", "#Design", "#Comics"],
            "processing_time": 0.15,
            "test_mode": True
        }
    elif is_evre_campaign:
        return {
            "success": True,
            "business_analysis": {
                "company_name": "EVRE",
                "industry": "Outdoor Furniture & Garden Accessories",
                "business_type": "e_commerce_retailer",
                "target_audience": "Homeowners, garden enthusiasts, outdoor living aficionados, families with gardens, ages 30-60",
                "brand_voice": "Premium, reliable, family-focused, outdoor lifestyle",
                "value_propositions": [
                    "High-quality weatherproof outdoor furniture",
                    "Modern designs for outdoor living spaces",
                    "Durable materials for long-lasting use"
                ],
                "product_context": {
                    "has_specific_product": True,
                    "product_name": "EVRE Outdoor Settee",
                    "product_themes": ["Garden furniture", "Outdoor living", "Premium quality", "Weatherproof"],
                    "product_visual_elements": "Modern outdoor settee with glass table, weatherproof design"
                }
            },
            "url_insights": {
                "primary_url": urls[0],
                "analysis_depth": request.get("analysis_depth", "standard"),
                "confidence_score": 0.89
            },
            "suggested_themes": ["Premium", "Outdoor Living", "Family", "Garden", "Quality"],
            "suggested_tags": ["#OutdoorFurniture", "#GardenLife", "#EVRE", "#OutdoorLiving", "#Settee", "#Premium"],
            "processing_time": 0.18,
            "test_mode": True
        }
    else:
        return {
            "success": True,
            "business_intelligence": {
                "company_name": "Example Company",
                "industry": "Technology",
                "target_audience": "Tech professionals"
            },
            "url_insights": {
                "primary_url": urls[0],
                "analysis_depth": request.get("analysis_depth", "quick"),
                "confidence_score": 0.85
            },
            "processing_time": 0.1,
            "test_mode": True
        }

@router.post("/test/campaign-create")
async def test_campaign_create(request: Dict[str, Any]):
    """Test-friendly campaign creation endpoint with realistic Joker T-shirt response."""
    campaign_name = request.get("name", "Test Campaign")
    
    # Check campaign type based on name
    is_joker_campaign = "joker" in campaign_name.lower()
    is_evre_campaign = "evre" in campaign_name.lower() or "settee" in campaign_name.lower() or "outdoor" in campaign_name.lower()
    
    if is_joker_campaign:
        campaign_id = "joker-tshirt-campaign-2024-001"
        return {
            "success": True,
            "campaign_id": campaign_id,
            "campaign": {
                "id": campaign_id,
                "name": campaign_name,
                "status": "created",
                "business_description": request.get("business_description", "Digital artist creating unique t-shirt designs"),
                "objective": request.get("objective", "promote the new product and increase sales"),
                "target_audience": request.get("target_audience", "Pop culture enthusiasts, comic book fans"),
                "campaign_type": request.get("campaign_type", "product"),
                "creativity_level": request.get("creativity_level", 8),
                "brand_themes": ["Artistic", "Bold", "Pop Culture", "Creative"],
                "product_focus": {
                    "product_name": "The Joker - Why Aren't You Laughing T-shirt",
                    "product_type": "Apparel",
                    "artistic_style": "Digital illustration"
                },
                "suggested_platforms": ["instagram", "facebook", "twitter"]
            },
            "processing_time": 0.15,
            "test_mode": True
        }
    elif is_evre_campaign:
        campaign_id = "evre-outdoor-settee-campaign-2024-001"
        return {
            "success": True,
            "campaign_id": campaign_id,
            "campaign": {
                "id": campaign_id,
                "name": campaign_name,
                "status": "created",
                "business_description": request.get("business_description", "Premium outdoor furniture retailer"),
                "objective": request.get("objective", "Promote views and get conversion/sales for outdoor settee"),
                "target_audience": request.get("target_audience", "Homeowners, garden enthusiasts, outdoor living aficionados"),
                "campaign_type": request.get("campaign_type", "product"),
                "creativity_level": request.get("creativity_level", 7),
                "brand_themes": ["Premium", "Outdoor Living", "Family", "Garden", "Quality"],
                "product_focus": {
                    "product_name": "EVRE Outdoor Settee",
                    "product_type": "Garden Furniture",
                    "key_features": "Weatherproof, modern design, glass table"
                },
                "suggested_platforms": ["instagram", "facebook", "pinterest"]
            },
            "processing_time": 0.12,
            "test_mode": True
        }
    else:
        campaign_id = f"test-campaign-{int(time.time())}"
        return {
            "success": True,
            "campaign_id": campaign_id,
            "campaign": {
                "id": campaign_id,
                "name": campaign_name,
                "status": "created",
                "business_description": request.get("business_description", "Test business"),
                "objective": request.get("objective", "test"),
                "target_audience": request.get("target_audience", "test audience"),
                "campaign_type": request.get("campaign_type", "product"),
                "creativity_level": request.get("creativity_level", 5)
            },
            "processing_time": 0.05,
            "test_mode": True
        }

@router.get("/test/health")
async def test_health():
    """Test health endpoint."""
    return {
        "status": "healthy",
        "service": "AI Marketing Campaign Post Generator",
        "version": "1.0.0-test",
        "timestamp": time.time(),
        "test_mode": True
    }

@router.post("/test/content-generate")
async def test_content_generate(request: Dict[str, Any]):
    """Test-friendly content generation endpoint with realistic Joker T-shirt content."""
    campaign_id = request.get("campaign_id", "test-campaign")
    post_count = request.get("post_count", 3)
    platforms = request.get("platforms", ["instagram"])
    
    # Check campaign type based on campaign ID
    is_joker_campaign = "joker" in campaign_id.lower()
    is_evre_campaign = "evre" in campaign_id.lower() or "settee" in campaign_id.lower() or "outdoor" in campaign_id.lower()
    
    posts = []
    if is_joker_campaign:
        joker_posts = [
            {
                "id": "joker-post-1",
                "type": "text_image",
                "content": "🃏 Why so serious? Get your hands on this incredible Joker t-shirt that captures the essence of Gotham's most iconic villain! Perfect for comic book lovers and art enthusiasts. 🎭✨",
                "platform": "instagram",
                "hashtags": ["#Joker", "#TShirt", "#PopCulture", "#ComicArt", "#Design", "#WhyArentYouLaughing", "#Gotham"],
                "engagement_score": 8.7,
                "visual_elements": "Dark, artistic Joker illustration with bold colors",
                "call_to_action": "Shop now and embrace your inner villain!"
            },
            {
                "id": "joker-post-2", 
                "type": "text_image",
                "content": "Art meets madness in this stunning Joker design! 🎨 Each detail crafted to perfection, bringing the character's chaotic energy to life on premium fabric. A must-have for any pop culture collection! 🔥",
                "platform": "facebook",
                "hashtags": ["#JokerArt", "#TShirtDesign", "#PopCultureFashion", "#DigitalArt", "#ComicBook"],
                "engagement_score": 8.2,
                "visual_elements": "Close-up of artistic details and fabric quality",
                "call_to_action": "Add to cart before it's gone!"
            },
            {
                "id": "joker-post-3",
                "type": "text_image", 
                "content": "🎭 'Why aren't you laughing?' - The question that haunts Gotham now on your favorite tee! This artistic masterpiece combines dark humor with incredible design. Perfect for making a statement! 💜🖤",
                "platform": "twitter",
                "hashtags": ["#Joker", "#TShirt", "#Art", "#ComicFan", "#Fashion", "#PopCulture"],
                "engagement_score": 7.9,
                "visual_elements": "Lifestyle shot showing the t-shirt being worn",
                "call_to_action": "Get yours today!"
            }
        ]
        
        # Use the first post_count posts
        posts = joker_posts[:post_count]
        
        # Adjust platforms if specified
        for i, platform in enumerate(platforms[:len(posts)]):
            posts[i]["platform"] = platform
            
    elif is_evre_campaign:
        evre_posts = [
            {
                "id": "evre-post-1",
                "type": "text_image",
                "content": "🌿 Transform your garden into a luxury outdoor oasis with the EVRE Outdoor Settee! ✨ Premium weatherproof design meets modern style - perfect for family gatherings and peaceful moments. 🏡 Shop now: https://amzn.to/45uWLJm",
                "platform": "instagram",
                "hashtags": ["#OutdoorFurniture", "#GardenLife", "#EVRE", "#OutdoorLiving", "#Settee", "#Premium", "#WeatherProof"],
                "engagement_score": 8.4,
                "visual_elements": "Modern outdoor settee with glass table in garden setting",
                "call_to_action": "Shop now on Amazon!"
            },
            {
                "id": "evre-post-2",
                "type": "text_image", 
                "content": "☀️ Summer entertaining made elegant! The EVRE Outdoor Settee combines durability with sophisticated design. 🌟 Perfect for hosting friends or enjoying quiet morning coffee in your garden paradise. Quality that lasts! 💚",
                "platform": "facebook",
                "hashtags": ["#OutdoorEntertaining", "#GardenFurniture", "#EVRE", "#QualityDesign", "#OutdoorStyle"],
                "engagement_score": 8.1,
                "visual_elements": "Lifestyle shot of people enjoying the settee outdoors",
                "call_to_action": "Discover the EVRE collection!"
            },
            {
                "id": "evre-post-3",
                "type": "text_image",
                "content": "🏡 Create memories that last with furniture built to endure! The EVRE Outdoor Settee: where premium meets practical. Weatherproof, stylish, and designed for the modern outdoor lifestyle. 🌈 #GardenGoals",
                "platform": "pinterest",
                "hashtags": ["#OutdoorDecor", "#GardenDesign", "#EVRE", "#OutdoorFurniture", "#HomeDesign", "#PatioStyle"],
                "engagement_score": 7.8,
                "visual_elements": "Styled garden scene with settee as focal point",
                "call_to_action": "Pin for your garden inspiration!"
            }
        ]
        
        # Use the first post_count posts
        posts = evre_posts[:post_count]
        
        # Adjust platforms if specified
        for i, platform in enumerate(platforms[:len(posts)]):
            posts[i]["platform"] = platform
            
    else:
        # Generate generic test posts
        for i in range(post_count):
            posts.append({
                "id": f"test-post-{i+1}",
                "type": "text_image",
                "content": f"Test social media post #{i+1} for campaign {campaign_id}",
                "platform": platforms[i % len(platforms)] if platforms else "instagram",
                "hashtags": ["#test", "#marketing", "#ai"],
                "engagement_score": 7.5 + (i * 0.3)
            })
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "posts": posts,
        "generation_metadata": {
            "posts_generated": len(posts),
            "processing_time": 0.25,
            "agent_used": "TestContentAgent" + ("_Joker" if is_joker_campaign else ""),
            "campaign_theme": "Joker T-shirt Art" if is_joker_campaign else "Generic"
        },
        "test_mode": True
    }

@router.get("/test/database-status")
async def test_database_status():
    """Test database status endpoint."""
    try:
        from database.database import get_database_status
        status = get_database_status()
        return {
            "success": True,
            "database": status,
            "test_mode": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test_mode": True
        }

@router.post("/test/image-generate")
async def test_image_generate(request: Dict[str, Any]):
    """Test-friendly image generation endpoint."""
    campaign_id = request.get("campaign_id", "test-campaign")
    posts = request.get("posts", [])
    image_style = request.get("image_style", "standard")
    
    # Check campaign type for realistic responses
    is_joker_campaign = "joker" in campaign_id.lower()
    is_evre_campaign = "evre" in campaign_id.lower() or "settee" in campaign_id.lower()
    
    generated_images = []
    for i, post in enumerate(posts[:3]):  # Limit to 3 posts
        if is_joker_campaign:
            generated_images.append({
                "post_id": post.get("id", f"post-{i+1}"),
                "image_prompt": f"Artistic Joker t-shirt design with bold colors and comic book styling, {image_style} composition",
                "image_url": f"https://example.com/generated/joker-tshirt-{i+1}.jpg",
                "visual_elements": "Dark artistic Joker illustration with vibrant colors, t-shirt product focus",
                "style_tags": ["artistic", "comic_book", "bold", "pop_culture"]
            })
        elif is_evre_campaign:
            generated_images.append({
                "post_id": post.get("id", f"post-{i+1}"),
                "image_prompt": f"Premium outdoor settee in modern garden setting, {image_style} lighting with lifestyle elements",
                "image_url": f"https://example.com/generated/evre-settee-{i+1}.jpg",
                "visual_elements": "Modern outdoor furniture in elegant garden setting, weatherproof design showcase",
                "style_tags": ["premium", "outdoor_living", "modern", "lifestyle"]
            })
        else:
            generated_images.append({
                "post_id": post.get("id", f"post-{i+1}"),
                "image_prompt": f"Generic product image with {image_style} styling",
                "image_url": f"https://example.com/generated/product-{i+1}.jpg",
                "visual_elements": "Standard product photography",
                "style_tags": ["clean", "professional"]
            })
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "generated_images": generated_images,
        "generation_metadata": {
            "images_generated": len(generated_images),
            "style_applied": image_style,
            "processing_time": 0.3,
            "ai_model": "TestImageGenerator"
        },
        "test_mode": True
    }

@router.post("/test/video-generate")
async def test_video_generate(request: Dict[str, Any]):
    """Test-friendly video generation endpoint."""
    campaign_id = request.get("campaign_id", "test-campaign")
    base_posts = request.get("base_posts", [])
    video_style = request.get("video_style", "standard")
    duration = request.get("duration", "30_seconds")
    
    # Check campaign type for realistic responses
    is_joker_campaign = "joker" in campaign_id.lower()
    is_evre_campaign = "evre" in campaign_id.lower() or "settee" in campaign_id.lower()
    
    if is_joker_campaign:
        video_content = {
            "video_id": f"joker-video-{int(time.time())}",
            "video_url": "https://example.com/generated/joker-tshirt-promo.mp4",
            "thumbnail_url": "https://example.com/generated/joker-tshirt-thumb.jpg",
            "script_outline": [
                "Opening: Joker artwork close-up with dramatic music",
                "Product showcase: T-shirt design details and quality",
                "Lifestyle shot: Person wearing the t-shirt",
                "Call-to-action: Shop now with URL overlay"
            ],
            "visual_elements": [
                "Dynamic Joker artwork animations",
                "Product rotation and detail shots",
                "Comic book style transitions",
                "Bold text overlays with quotes"
            ],
            "audio_elements": {
                "background_music": "Dark, dramatic comic book theme",
                "voiceover_style": "Mysterious, engaging narrator",
                "sound_effects": "Comic book style transitions"
            }
        }
    elif is_evre_campaign:
        video_content = {
            "video_id": f"evre-video-{int(time.time())}",
            "video_url": "https://example.com/generated/evre-settee-showcase.mp4",
            "thumbnail_url": "https://example.com/generated/evre-settee-thumb.jpg",
            "script_outline": [
                "Opening: Beautiful garden setting establishing shot",
                "Product focus: Settee design and weatherproof features",
                "Lifestyle moment: Family enjoying outdoor time",
                "Call-to-action: Amazon purchase link display"
            ],
            "visual_elements": [
                "Smooth camera movements around garden setting",
                "Close-up shots of premium materials and design",
                "Natural lighting showcasing outdoor durability",
                "Lifestyle shots with people enjoying the furniture"
            ],
            "audio_elements": {
                "background_music": "Peaceful, uplifting outdoor lifestyle theme",
                "voiceover_style": "Warm, family-focused narrator",
                "sound_effects": "Natural outdoor ambiance"
            }
        }
    else:
        video_content = {
            "video_id": f"generic-video-{int(time.time())}",
            "video_url": "https://example.com/generated/product-video.mp4",
            "thumbnail_url": "https://example.com/generated/product-thumb.jpg",
            "script_outline": ["Product introduction", "Feature highlights", "Call-to-action"],
            "visual_elements": ["Standard product shots"],
            "audio_elements": {"background_music": "Generic upbeat", "voiceover_style": "Professional"}
        }
    
    return {
        "success": True,
        "campaign_id": campaign_id,
        "video_content": video_content,
        "generation_metadata": {
            "duration": duration,
            "style": video_style,
            "posts_used": len(base_posts),
            "processing_time": 0.5,
            "ai_model": "TestVideoGenerator"
        },
        "test_mode": True
    } 