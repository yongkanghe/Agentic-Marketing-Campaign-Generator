"""
FILENAME: social_auth.py
DESCRIPTION/PURPOSE: Social media OAuth authentication routes for campaign scheduling integration
Author: JP + 2025-06-22

This module provides OAuth 2.0 authentication endpoints for social media platforms:
- LinkedIn, Twitter/X, Instagram, Facebook, TikTok
- Secure token storage and management
- Platform connection status management
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlencode, parse_qs

from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx
from cryptography.fernet import Fernet

from database.database import get_database_connection

# Configure logging
logger = logging.getLogger(__name__)

# Social media platform configurations
SOCIAL_PLATFORMS = {
    "linkedin": {
        "api_version": "v2",
        "oauth_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "scopes": ["w_member_social", "r_liteprofile", "r_emailaddress"],
        "posting_endpoint": "/v2/ugcPosts",
        "char_limit": 3000,
        "supports_images": True,
        "supports_video": True
    },
    "twitter": {
        "api_version": "v2",
        "oauth_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "scopes": ["tweet.read", "tweet.write", "users.read"],
        "posting_endpoint": "/2/tweets",
        "char_limit": 280,
        "supports_images": True,
        "supports_video": True,
        "requires_pkce": True
    },
    "instagram": {
        "api_version": "Graph API",
        "oauth_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "scopes": ["instagram_basic", "instagram_content_publish", "pages_show_list"],
        "posting_endpoint": "/me/media",
        "char_limit": 2200,
        "supports_images": True,
        "supports_video": True,
        "requires_facebook_auth": True
    },
    "facebook": {
        "api_version": "Graph API v18.0",
        "oauth_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "scopes": ["pages_manage_posts", "pages_read_engagement", "pages_show_list"],
        "posting_endpoint": "/page-id/feed",
        "char_limit": 63206,
        "supports_images": True,
        "supports_video": True
    },
    "tiktok": {
        "api_version": "TikTok for Developers",
        "oauth_url": "https://www.tiktok.com/auth/authorize/",
        "token_url": "https://open-api.tiktok.com/oauth/access_token/",
        "scopes": ["video.upload", "user.info.basic"],
        "posting_endpoint": "/share/video/upload/",
        "char_limit": 150,
        "supports_images": False,
        "supports_video": True,
        "requires_video_content": True
    }
}

# Router
router = APIRouter()

# Token encryption setup
def get_encryption_key() -> bytes:
    """Get encryption key from environment or generate one for development."""
    key = os.getenv("SOCIAL_TOKEN_ENCRYPTION_KEY")
    if not key:
        # For development - in production this should be set in environment
        logger.warning("SOCIAL_TOKEN_ENCRYPTION_KEY not set, using development key")
        return Fernet.generate_key()
    return key.encode() if isinstance(key, str) else key

CIPHER_SUITE = Fernet(get_encryption_key())

# Request/Response Models
class SocialAuthRequest(BaseModel):
    platform: str
    callback_url: str

class SocialAuthResponse(BaseModel):
    oauth_url: str
    state: str

class SocialConnection(BaseModel):
    id: int
    platform: str
    platform_user_id: str
    platform_username: Optional[str]
    connection_status: str
    scopes: List[str]
    connected_at: datetime
    last_used_at: Optional[datetime]

class ConnectionsResponse(BaseModel):
    connections: List[SocialConnection]

# Utility Functions
def encrypt_token(token: str) -> str:
    """Encrypt OAuth token for secure storage."""
    return CIPHER_SUITE.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt OAuth token from storage."""
    return CIPHER_SUITE.decrypt(encrypted_token.encode()).decode()

def generate_oauth_state(user_id: str, platform: str) -> str:
    """Generate secure OAuth state parameter."""
    import secrets
    import hashlib
    
    state_data = f"{user_id}:{platform}:{secrets.token_urlsafe(16)}"
    return hashlib.sha256(state_data.encode()).hexdigest()[:32]

def validate_oauth_state(state: str, user_id: str, platform: str) -> bool:
    """Validate OAuth state parameter - simplified for demo."""
    # In production, store and validate state properly
    return len(state) == 32 and state.isalnum()

async def get_current_user_id(request: Request) -> str:
    """Get current user ID from session - simplified for demo."""
    # In production, implement proper session management
    # For now, return demo user
    return "demo_user"

# OAuth Flow Endpoints
@router.post("/initiate", response_model=SocialAuthResponse)
async def initiate_oauth_flow(
    auth_request: SocialAuthRequest,
    request: Request
):
    """Initiate OAuth flow for a social media platform."""
    logger.info(f"Initiating OAuth flow for platform: {auth_request.platform}")
    
    if auth_request.platform not in SOCIAL_PLATFORMS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform: {auth_request.platform}"
        )
    
    user_id = await get_current_user_id(request)
    platform_config = SOCIAL_PLATFORMS[auth_request.platform]
    
    # Generate OAuth state
    state = generate_oauth_state(user_id, auth_request.platform)
    
    # Get OAuth credentials from environment
    client_id_key = f"{auth_request.platform.upper()}_CLIENT_ID"
    client_id = os.getenv(client_id_key)
    
    if not client_id:
        logger.error(f"OAuth client ID not configured for {auth_request.platform}")
        raise HTTPException(
            status_code=500,
            detail=f"OAuth not configured for {auth_request.platform}. Please set {client_id_key} environment variable."
        )
    
    # Build OAuth URL
    oauth_params = {
        "client_id": client_id,
        "redirect_uri": auth_request.callback_url,
        "scope": " ".join(platform_config["scopes"]),
        "state": state,
        "response_type": "code"
    }
    
    # Platform-specific OAuth parameters
    if auth_request.platform == "twitter" and platform_config.get("requires_pkce"):
        # Twitter requires PKCE
        import secrets
        import hashlib
        import base64
        
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        oauth_params.update({
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        })
        
        # Store code verifier for token exchange (in production, use proper session storage)
        # For demo, we'll handle this in the callback
    
    oauth_url = f"{platform_config['oauth_url']}?{urlencode(oauth_params)}"
    
    logger.info(f"Generated OAuth URL for {auth_request.platform}")
    
    return SocialAuthResponse(
        oauth_url=oauth_url,
        state=state
    )

@router.get("/callback/{platform}")
async def oauth_callback(
    platform: str,
    code: str,
    state: str,
    request: Request
):
    """Handle OAuth callback from social media platform."""
    logger.info(f"Handling OAuth callback for platform: {platform}")
    
    if platform not in SOCIAL_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
    
    user_id = await get_current_user_id(request)
    
    # Validate state parameter
    if not validate_oauth_state(state, user_id, platform):
        logger.warning(f"Invalid OAuth state for platform: {platform}")
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    
    try:
        # Exchange authorization code for access token
        access_token, refresh_token, expires_in, user_info = await exchange_oauth_code(
            platform, code, user_id
        )
        
        # Store the connection in database
        connection_id = await store_social_connection(
            user_id=user_id,
            platform=platform,
            platform_user_id=user_info.get("id", "unknown"),
            platform_username=user_info.get("username", user_info.get("name")),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            scopes=SOCIAL_PLATFORMS[platform]["scopes"]
        )
        
        logger.info(f"Successfully connected {platform} for user {user_id}")
        
        # Return success response (in production, redirect to frontend with success message)
        return {
            "success": True,
            "connection": {
                "id": connection_id,
                "platform": platform,
                "username": user_info.get("username", user_info.get("name")),
                "connected_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"OAuth callback error for {platform}: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth authentication failed: {str(e)}")

async def exchange_oauth_code(platform: str, code: str, user_id: str) -> tuple:
    """Exchange OAuth authorization code for access token."""
    platform_config = SOCIAL_PLATFORMS[platform]
    
    # Get OAuth credentials
    client_id = os.getenv(f"{platform.upper()}_CLIENT_ID")
    client_secret = os.getenv(f"{platform.upper()}_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError(f"OAuth credentials not configured for {platform}")
    
    # Prepare token request
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": f"{os.getenv('BACKEND_URL', 'http://localhost:8080')}/api/v1/auth/social/callback/{platform}"
    }
    
    # Platform-specific token exchange
    if platform == "twitter":
        # Twitter OAuth 2.0 with PKCE
        token_data["code_verifier"] = "demo_code_verifier"  # In production, retrieve stored verifier
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            platform_config["token_url"],
            data=token_data,
            headers={"Accept": "application/json"}
        )
        
        if response.status_code != 200:
            logger.error(f"Token exchange failed for {platform}: {response.text}")
            raise ValueError(f"Token exchange failed: {response.status_code}")
        
        token_response = response.json()
        
        access_token = token_response.get("access_token")
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response.get("expires_in", 3600)
        
        if not access_token:
            raise ValueError("No access token received")
        
        # Get user information
        user_info = await get_platform_user_info(platform, access_token)
        
        return access_token, refresh_token, expires_in, user_info

async def get_platform_user_info(platform: str, access_token: str) -> dict:
    """Get user information from social media platform."""
    user_endpoints = {
        "linkedin": "https://api.linkedin.com/v2/people/~",
        "twitter": "https://api.twitter.com/2/users/me",
        "instagram": "https://graph.instagram.com/me",
        "facebook": "https://graph.facebook.com/me",
        "tiktok": "https://open-api.tiktok.com/user/info/"
    }
    
    if platform not in user_endpoints:
        return {"id": "unknown", "username": "unknown"}
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Platform-specific headers
            if platform == "linkedin":
                headers["X-Restli-Protocol-Version"] = "2.0.0"
            
            response = await client.get(user_endpoints[platform], headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Extract user info based on platform
                if platform == "linkedin":
                    return {
                        "id": user_data.get("id"),
                        "name": f"{user_data.get('firstName', {}).get('localized', {}).get('en_US', '')} {user_data.get('lastName', {}).get('localized', {}).get('en_US', '')}".strip()
                    }
                elif platform == "twitter":
                    return {
                        "id": user_data.get("data", {}).get("id"),
                        "username": user_data.get("data", {}).get("username")
                    }
                else:
                    return {
                        "id": user_data.get("id"),
                        "username": user_data.get("username", user_data.get("name"))
                    }
            else:
                logger.warning(f"Failed to get user info for {platform}: {response.status_code}")
                return {"id": "unknown", "username": "unknown"}
                
    except Exception as e:
        logger.error(f"Error getting user info for {platform}: {e}")
        return {"id": "unknown", "username": "unknown"}

async def store_social_connection(
    user_id: str,
    platform: str,
    platform_user_id: str,
    platform_username: Optional[str],
    access_token: str,
    refresh_token: Optional[str],
    expires_in: int,
    scopes: List[str]
) -> int:
    """Store social media connection in database."""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Encrypt tokens
        encrypted_access_token = encrypt_token(access_token)
        encrypted_refresh_token = encrypt_token(refresh_token) if refresh_token else None
        
        # Calculate expiration time
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        # Insert or update connection
        cursor.execute("""
            INSERT OR REPLACE INTO social_media_connections (
                user_id, platform, platform_user_id, platform_username,
                access_token, refresh_token, token_expires_at, scopes,
                connection_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', datetime('now'), datetime('now'))
        """, (
            user_id, platform, platform_user_id, platform_username,
            encrypted_access_token, encrypted_refresh_token, expires_at,
            json.dumps(scopes)
        ))
        
        connection_id = cursor.lastrowid
        if connection_id is None:
            raise ValueError("Failed to get connection ID from database")
            
        conn.commit()
        conn.close()
        
        logger.info(f"Stored social connection {connection_id} for {platform}")
        return connection_id
        
    except Exception as e:
        logger.error(f"Failed to store social connection: {e}")
        raise

# Connection Management Endpoints
@router.get("/connections", response_model=ConnectionsResponse)
async def get_user_connections(request: Request):
    """Get user's social media connections."""
    user_id = await get_current_user_id(request)
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, platform, platform_user_id, platform_username,
                   scopes, connection_status, created_at, last_used_at
            FROM social_media_connections
            WHERE user_id = ? AND connection_status = 'active'
            ORDER BY created_at DESC
        """, (user_id,))
        
        connections = []
        for row in cursor.fetchall():
            connections.append(SocialConnection(
                id=row[0],
                platform=row[1],
                platform_user_id=row[2],
                platform_username=row[3],
                connection_status=row[5],
                scopes=json.loads(row[4]) if row[4] else [],
                connected_at=datetime.fromisoformat(row[6]),
                last_used_at=datetime.fromisoformat(row[7]) if row[7] else None
            ))
        
        conn.close()
        
        return ConnectionsResponse(connections=connections)
        
    except Exception as e:
        logger.error(f"Failed to get user connections: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve connections")

@router.delete("/disconnect/{platform}")
async def disconnect_platform(platform: str, request: Request):
    """Disconnect a social media platform."""
    if platform not in SOCIAL_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
    
    user_id = await get_current_user_id(request)
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE social_media_connections
            SET connection_status = 'revoked', updated_at = datetime('now')
            WHERE user_id = ? AND platform = ?
        """, (user_id, platform))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail=f"No connection found for {platform}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Disconnected {platform} for user {user_id}")
        
        return {
            "success": True,
            "message": f"Successfully disconnected from {platform}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disconnect {platform}: {e}")
        raise HTTPException(status_code=500, detail="Failed to disconnect platform")

@router.get("/status")
async def get_auth_status(request: Request):
    """Get authentication status for all platforms."""
    user_id = await get_current_user_id(request)
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT platform, connection_status, platform_username, created_at
            FROM social_media_connections
            WHERE user_id = ? AND connection_status = 'active'
        """, (user_id,))
        
        connected_platforms = {}
        for row in cursor.fetchall():
            connected_platforms[row[0]] = {
                "connected": True,
                "status": row[1],
                "username": row[2],
                "connected_at": row[3]
            }
        
        conn.close()
        
        # Build complete status for all platforms
        platform_status = {}
        for platform in SOCIAL_PLATFORMS:
            platform_status[platform] = connected_platforms.get(platform, {
                "connected": False,
                "status": "not_connected"
            })
        
        return {
            "user_id": user_id,
            "platforms": platform_status,
            "total_connected": len(connected_platforms)
        }
        
    except Exception as e:
        logger.error(f"Failed to get auth status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve authentication status")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for social authentication service."""
    # Check if required environment variables are set
    missing_configs = []
    for platform in SOCIAL_PLATFORMS:
        client_id_key = f"{platform.upper()}_CLIENT_ID"
        client_secret_key = f"{platform.upper()}_CLIENT_SECRET"
        
        if not os.getenv(client_id_key):
            missing_configs.append(client_id_key)
        if not os.getenv(client_secret_key):
            missing_configs.append(client_secret_key)
    
    return {
        "service": "social_auth",
        "status": "healthy" if not missing_configs else "degraded",
        "supported_platforms": list(SOCIAL_PLATFORMS.keys()),
        "missing_configurations": missing_configs,
        "encryption_key_set": bool(os.getenv("SOCIAL_TOKEN_ENCRYPTION_KEY"))
    }