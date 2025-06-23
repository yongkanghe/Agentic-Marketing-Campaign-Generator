"""
FILENAME: social_posts.py
DESCRIPTION/PURPOSE: Social media post scheduling and publishing routes for campaign management
Author: JP + 2025-06-22

This module provides endpoints for:
- Scheduling posts to social media platforms
- Managing scheduled posts
- Publishing posts to social media
- Tracking post status and performance
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from asyncio import create_task, gather

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
import httpx

from database.database import get_database_connection
from .social_auth import decrypt_token, SOCIAL_PLATFORMS

# Configure logging
logger = logging.getLogger(__name__)

# Router
router = APIRouter()

# Request/Response Models
class PostContent(BaseModel):
    content: str
    platforms: List[str]
    scheduled_time: str
    media_urls: Optional[List[str]] = []
    hashtags: Optional[List[str]] = []
    mentions: Optional[List[str]] = []

class SchedulingOptions(BaseModel):
    interval_hours: int
    start_time: str

class SchedulePostsRequest(BaseModel):
    campaign_id: str
    posts: List[PostContent]
    scheduling_options: SchedulingOptions

class ScheduledPostResponse(BaseModel):
    id: str
    platform: str
    status: str
    scheduled_time: str
    posted_time: Optional[str]
    platform_post_id: Optional[str]
    error: Optional[str]

class ScheduledPostsResponse(BaseModel):
    scheduled_posts: List[ScheduledPostResponse]

# Utility Functions
async def get_current_user_id(request: Request) -> str:
    """Get current user ID from session - simplified for demo."""
    return "demo_user"

async def get_active_connection(user_id: str, platform: str) -> Optional[dict]:
    """Get active social media connection for user and platform."""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, access_token, refresh_token, token_expires_at, platform_user_id
            FROM social_media_connections
            WHERE user_id = ? AND platform = ? AND connection_status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id, platform))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "access_token": decrypt_token(row[1]),
                "refresh_token": decrypt_token(row[2]) if row[2] else None,
                "expires_at": row[3],
                "platform_user_id": row[4]
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get connection for {platform}: {e}")
        return None

# Scheduling Endpoints
@router.post("/schedule", response_model=dict)
async def schedule_posts(
    schedule_request: SchedulePostsRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Schedule posts to social media platforms."""
    logger.info(f"Scheduling posts for campaign: {schedule_request.campaign_id}")
    
    user_id = await get_current_user_id(request)
    
    # Validate campaign exists and belongs to user
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id FROM campaigns 
        WHERE id = ? AND user_id = ?
    """, (schedule_request.campaign_id, user_id))
    
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    scheduled_post_ids = []
    
    try:
        # Process each post content
        for post_index, post_content in enumerate(schedule_request.posts):
            # Calculate scheduled time for this post
            base_time = datetime.fromisoformat(post_content.scheduled_time.replace('Z', '+00:00'))
            scheduled_time = base_time + timedelta(
                hours=post_index * schedule_request.scheduling_options.interval_hours
            )
            
            # Schedule to each selected platform
            for platform in post_content.platforms:
                if platform not in SOCIAL_PLATFORMS:
                    logger.warning(f"Unsupported platform: {platform}")
                    continue
                
                # Check if user has active connection for this platform
                connection = await get_active_connection(user_id, platform)
                if not connection:
                    logger.warning(f"No active connection for {platform}")
                    continue
                
                # Create scheduled post record
                post_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO scheduled_posts (
                        id, campaign_id, user_id, social_connection_id,
                        platform, post_content, media_urls, hashtags, mentions,
                        scheduled_time, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', datetime('now'), datetime('now'))
                """, (
                    post_id, schedule_request.campaign_id, user_id, connection["id"],
                    platform, post_content.content, 
                    json.dumps(post_content.media_urls or []),
                    json.dumps(post_content.hashtags or []),
                    json.dumps(post_content.mentions or []),
                    scheduled_time
                ))
                
                scheduled_post_ids.append(post_id)
                logger.info(f"Scheduled post {post_id} for {platform} at {scheduled_time}")
        
        conn.commit()
        conn.close()
        
        # Add background task to process scheduled posts
        background_tasks.add_task(process_scheduled_posts)
        
        return {
            "success": True,
            "scheduled_posts": len(scheduled_post_ids),
            "post_ids": scheduled_post_ids,
            "message": f"Successfully scheduled {len(scheduled_post_ids)} posts"
        }
        
    except Exception as e:
        conn.close()
        logger.error(f"Failed to schedule posts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule posts: {str(e)}")

@router.get("/scheduled/{campaign_id}", response_model=ScheduledPostsResponse)
async def get_scheduled_posts(campaign_id: str, request: Request):
    """Get scheduled posts for a campaign."""
    user_id = await get_current_user_id(request)
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, platform, status, scheduled_time, actual_post_time,
                   platform_post_id, posting_error
            FROM scheduled_posts
            WHERE campaign_id = ? AND user_id = ?
            ORDER BY scheduled_time ASC
        """, (campaign_id, user_id))
        
        scheduled_posts = []
        for row in cursor.fetchall():
            scheduled_posts.append(ScheduledPostResponse(
                id=row[0],
                platform=row[1],
                status=row[2],
                scheduled_time=row[3],
                posted_time=row[4],
                platform_post_id=row[5],
                error=row[6]
            ))
        
        conn.close()
        
        return ScheduledPostsResponse(scheduled_posts=scheduled_posts)
        
    except Exception as e:
        logger.error(f"Failed to get scheduled posts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve scheduled posts")

@router.post("/publish/{post_id}")
async def publish_post_now(post_id: str, request: Request):
    """Immediately publish a scheduled post."""
    user_id = await get_current_user_id(request)
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Get the scheduled post
        cursor.execute("""
            SELECT sp.id, sp.platform, sp.post_content, sp.media_urls, sp.hashtags,
                   sp.social_connection_id, smc.access_token, smc.platform_user_id
            FROM scheduled_posts sp
            JOIN social_media_connections smc ON sp.social_connection_id = smc.id
            WHERE sp.id = ? AND sp.user_id = ? AND sp.status = 'pending'
        """, (post_id, user_id))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise HTTPException(
                status_code=404, 
                detail="Scheduled post not found or already published"
            )
        
        post_data = {
            "id": row[0],
            "platform": row[1],
            "content": row[2],
            "media_urls": json.loads(row[3]) if row[3] else [],
            "hashtags": json.loads(row[4]) if row[4] else [],
            "access_token": decrypt_token(row[6]),
            "platform_user_id": row[7]
        }
        
        conn.close()
        
        # Publish the post
        result = await publish_to_platform(post_data)
        
        # Update the post status
        conn = get_database_connection()
        cursor = conn.cursor()
        
        if result["success"]:
            cursor.execute("""
                UPDATE scheduled_posts
                SET status = 'posted', actual_post_time = datetime('now'),
                    platform_post_id = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (result.get("platform_post_id"), post_id))
            
            message = f"Post published successfully to {post_data['platform']}"
        else:
            cursor.execute("""
                UPDATE scheduled_posts
                SET status = 'failed', posting_error = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (result.get("error"), post_id))
            
            message = f"Failed to publish post: {result.get('error')}"
        
        conn.commit()
        conn.close()
        
        return {
            "success": result["success"],
            "message": message,
            "platform_post_id": result.get("platform_post_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to publish post: {str(e)}")

@router.delete("/cancel/{post_id}")
async def cancel_scheduled_post(post_id: str, request: Request):
    """Cancel a scheduled post."""
    user_id = await get_current_user_id(request)
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE scheduled_posts
            SET status = 'cancelled', updated_at = datetime('now')
            WHERE id = ? AND user_id = ? AND status = 'pending'
        """, (post_id, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(
                status_code=404,
                detail="Scheduled post not found or cannot be cancelled"
            )
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Scheduled post cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel post {post_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel post")

# Publishing Functions
async def publish_to_platform(post_data: dict) -> dict:
    """Publish content to a specific social media platform."""
    platform = post_data["platform"]
    platform_config = SOCIAL_PLATFORMS.get(platform)
    
    if not platform_config:
        return {"success": False, "error": f"Unsupported platform: {platform}"}
    
    try:
        if platform == "linkedin":
            return await publish_to_linkedin(post_data)
        elif platform == "twitter":
            return await publish_to_twitter(post_data)
        elif platform == "instagram":
            return await publish_to_instagram(post_data)
        elif platform == "facebook":
            return await publish_to_facebook(post_data)
        elif platform == "tiktok":
            return await publish_to_tiktok(post_data)
        else:
            return {"success": False, "error": f"Publishing not implemented for {platform}"}
            
    except Exception as e:
        logger.error(f"Publishing error for {platform}: {e}")
        return {"success": False, "error": str(e)}

async def publish_to_twitter(post_data: dict) -> dict:
    """Publish post to Twitter/X."""
    try:
        headers = {
            "Authorization": f"Bearer {post_data['access_token']}",
            "Content-Type": "application/json"
        }
        
        tweet_data = {
            "text": post_data["content"]
        }
        
        # Add media if available
        if post_data.get("media_urls"):
            # Note: In production, you'd need to upload media first and get media IDs
            logger.info("Media URLs found but media upload not implemented for demo")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.twitter.com/2/tweets",
                headers=headers,
                json=tweet_data
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "platform_post_id": result["data"]["id"],
                    "response": result
                }
            else:
                logger.error(f"Twitter API error: {response.text}")
                return {
                    "success": False,
                    "error": f"Twitter API error: {response.status_code}"
                }
                
    except Exception as e:
        return {"success": False, "error": str(e)}

async def publish_to_linkedin(post_data: dict) -> dict:
    """Publish post to LinkedIn."""
    try:
        headers = {
            "Authorization": f"Bearer {post_data['access_token']}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # LinkedIn UGC Posts API format
        ugc_post = {
            "author": f"urn:li:person:{post_data['platform_user_id']}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_data["content"]
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers=headers,
                json=ugc_post
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "platform_post_id": result.get("id", "unknown"),
                    "response": result
                }
            else:
                logger.error(f"LinkedIn API error: {response.text}")
                return {
                    "success": False,
                    "error": f"LinkedIn API error: {response.status_code}"
                }
                
    except Exception as e:
        return {"success": False, "error": str(e)}

async def publish_to_instagram(post_data: dict) -> dict:
    """Publish post to Instagram - requires Facebook Graph API."""
    # Instagram posting is complex and requires container creation first
    # For demo, return success with note
    logger.info("Instagram publishing requires complex container workflow - demo mode")
    return {
        "success": True,
        "platform_post_id": f"demo_instagram_{uuid.uuid4().hex[:8]}",
        "note": "Demo mode - Instagram publishing requires full container workflow"
    }

async def publish_to_facebook(post_data: dict) -> dict:
    """Publish post to Facebook."""
    # Facebook page posting requires page access token and page ID
    # For demo, return success with note
    logger.info("Facebook publishing requires page management setup - demo mode")
    return {
        "success": True,
        "platform_post_id": f"demo_facebook_{uuid.uuid4().hex[:8]}",
        "note": "Demo mode - Facebook publishing requires page management setup"
    }

async def publish_to_tiktok(post_data: dict) -> dict:
    """Publish post to TikTok - video content only."""
    # TikTok only supports video content
    if not post_data.get("media_urls"):
        return {
            "success": False,
            "error": "TikTok requires video content - no media URLs provided"
        }
    
    logger.info("TikTok publishing requires video upload workflow - demo mode")
    return {
        "success": True,
        "platform_post_id": f"demo_tiktok_{uuid.uuid4().hex[:8]}",
        "note": "Demo mode - TikTok publishing requires video upload workflow"
    }

# Background Task Functions
async def process_scheduled_posts():
    """Background task to process scheduled posts that are due."""
    logger.info("Processing scheduled posts...")
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Get posts that are due for publishing (within the last 5 minutes to handle timing)
        current_time = datetime.now()
        past_due_time = current_time - timedelta(minutes=5)
        
        cursor.execute("""
            SELECT sp.id, sp.platform, sp.post_content, sp.media_urls, sp.hashtags,
                   smc.access_token, smc.platform_user_id
            FROM scheduled_posts sp
            JOIN social_media_connections smc ON sp.social_connection_id = smc.id
            WHERE sp.status = 'pending' 
              AND sp.scheduled_time <= ? 
              AND sp.scheduled_time >= ?
              AND smc.connection_status = 'active'
            ORDER BY sp.scheduled_time ASC
        """, (current_time, past_due_time))
        
        posts_to_publish = cursor.fetchall()
        conn.close()
        
        if not posts_to_publish:
            logger.info("No posts due for publishing")
            return
        
        logger.info(f"Found {len(posts_to_publish)} posts to publish")
        
        # Process each post
        for post_row in posts_to_publish:
            post_data = {
                "id": post_row[0],
                "platform": post_row[1],
                "content": post_row[2],
                "media_urls": json.loads(post_row[3]) if post_row[3] else [],
                "hashtags": json.loads(post_row[4]) if post_row[4] else [],
                "access_token": decrypt_token(post_row[5]),
                "platform_user_id": post_row[6]
            }
            
            # Publish the post
            result = await publish_to_platform(post_data)
            
            # Update the post status
            conn = get_database_connection()
            cursor = conn.cursor()
            
            if result["success"]:
                cursor.execute("""
                    UPDATE scheduled_posts
                    SET status = 'posted', actual_post_time = datetime('now'),
                        platform_post_id = ?, updated_at = datetime('now')
                    WHERE id = ?
                """, (result.get("platform_post_id"), post_data["id"]))
                
                logger.info(f"Successfully published post {post_data['id']} to {post_data['platform']}")
            else:
                cursor.execute("""
                    UPDATE scheduled_posts
                    SET status = 'failed', posting_error = ?, 
                        retry_count = retry_count + 1, updated_at = datetime('now')
                    WHERE id = ?
                """, (result.get("error"), post_data["id"]))
                
                logger.error(f"Failed to publish post {post_data['id']}: {result.get('error')}")
            
            conn.commit()
            conn.close()
            
    except Exception as e:
        logger.error(f"Error processing scheduled posts: {e}")

# Status and Analytics Endpoints
@router.get("/status/summary")
async def get_posting_summary(request: Request):
    """Get summary of posting status across all campaigns."""
    user_id = await get_current_user_id(request)
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, platform, COUNT(*) as count
            FROM scheduled_posts
            WHERE user_id = ?
            GROUP BY status, platform
            ORDER BY status, platform
        """, (user_id,))
        
        summary = {}
        for row in cursor.fetchall():
            status, platform, count = row
            if status not in summary:
                summary[status] = {}
            summary[status][platform] = count
        
        conn.close()
        
        return {
            "user_id": user_id,
            "summary": summary,
            "total_platforms": len(SOCIAL_PLATFORMS),
            "supported_platforms": list(SOCIAL_PLATFORMS.keys())
        }
        
    except Exception as e:
        logger.error(f"Failed to get posting summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve posting summary")