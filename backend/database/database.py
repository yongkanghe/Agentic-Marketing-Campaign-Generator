"""
FILENAME: database.py
DESCRIPTION/PURPOSE: Database initialization and management for AI Marketing Campaign Post Generator
Author: JP + 2025-06-16

This module provides database initialization, connection management, and schema setup
for the SQLite database used in development and testing.
"""

import sqlite3
import os
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_DIR = Path(__file__).parent / "data"
DATABASE_PATH = DATABASE_DIR / "database.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def ensure_database_directory():
    """Ensure the database directory exists."""
    DATABASE_DIR.mkdir(exist_ok=True)
    logger.info(f"Database directory ensured: {DATABASE_DIR}")

def get_database_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    ensure_database_directory()
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn

def init_database() -> bool:
    """Initialize the database with the schema."""
    try:
        ensure_database_directory()
        
        # Read schema file
        if not SCHEMA_PATH.exists():
            logger.error(f"Schema file not found: {SCHEMA_PATH}")
            return False
        
        with open(SCHEMA_PATH, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Execute the schema in chunks (split by semicolon)
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for statement in statements:
            try:
                cursor.execute(statement)
            except sqlite3.Error as e:
                logger.warning(f"Schema statement warning: {e}")
                # Continue with other statements
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized successfully: {DATABASE_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def reset_database() -> bool:
    """Reset the database by deleting and recreating it."""
    try:
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
            logger.info("Existing database deleted")
        
        return init_database()
        
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        return False

def check_database_status() -> dict:
    """Check the status of the database."""
    status = {
        'exists': DATABASE_PATH.exists(),
        'path': str(DATABASE_PATH),
        'size': 0,
        'tables': [],
        'error': None
    }
    
    try:
        if status['exists']:
            status['size'] = DATABASE_PATH.stat().st_size
            
            conn = get_database_connection()
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            status['tables'] = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
    except Exception as e:
        status['error'] = str(e)
        logger.error(f"Error checking database status: {e}")
    
    return status

def create_test_data() -> bool:
    """Create some test data for development."""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Insert test user
        cursor.execute("""
            INSERT OR REPLACE INTO users (id, username, email, password_hash, first_name, last_name, created_at, updated_at) 
            VALUES ('test-user-1', 'testuser', 'test@example.com', 'dummy_hash', 'Test', 'User', datetime('now'), datetime('now'))
        """)
        
        # Insert demo user for demo campaigns
        cursor.execute("""
            INSERT OR REPLACE INTO users (id, username, email, password_hash, first_name, last_name, created_at, updated_at) 
            VALUES ('demo_user', 'demouser', 'demo@example.com', 'dummy_hash', 'Demo', 'User', datetime('now'), datetime('now'))
        """)
        
        # Insert test campaign
        cursor.execute("""
            INSERT OR REPLACE INTO campaigns (
                id, user_id, name, objective, business_description, 
                campaign_type, target_audience, creativity_level, 
                created_at, updated_at
            ) VALUES (
                'test-campaign-1', 'test-user-1', 'Test Campaign', 
                'Test objective', 'Test business description', 
                'product', 'Test audience', 7,
                datetime('now'), datetime('now')
            )
        """)
        
        # Insert demo campaign with business analysis for testing chat
        import json
        demo_business_analysis = {
            "company_name": "Demo Company",
            "industry": "Technology", 
            "business_type": "individual_creator",
            "target_audience": "Tech professionals and entrepreneurs",
            "brand_voice": "Professional, innovative, approachable",
            "creative_direction": "Modern, clean visuals with authentic storytelling",
            "visual_style": "Professional photography with vibrant colors",
            "content_themes": "Innovation, growth, community building",
            "image_generation_guidance": "High-quality, professional imagery with modern aesthetics",
            "video_generation_guidance": "Short, engaging videos with clear messaging"
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO campaigns (
                id, user_id, name, objective, business_description, 
                campaign_type, target_audience, creativity_level,
                business_context, created_at, updated_at
            ) VALUES (
                'demo', 'demo_user', 'Demo Campaign', 
                'Increase brand awareness and engagement', 
                'A technology company focused on innovative solutions for modern businesses', 
                'service', 'Business professionals and tech enthusiasts', 8,
                ?, datetime('now'), datetime('now')
            )
        """, (json.dumps(demo_business_analysis),))
        
        conn.commit()
        conn.close()
        
        logger.info("Test data created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create test data: {e}")
        return False

if __name__ == "__main__":
    """Command line interface for database operations."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python database.py [init|reset|status|test-data]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        success = init_database()
        print("✅ Database initialized" if success else "❌ Database initialization failed")
        sys.exit(0 if success else 1)
        
    elif command == "reset":
        success = reset_database()
        print("✅ Database reset" if success else "❌ Database reset failed")
        sys.exit(0 if success else 1)
        
    elif command == "status":
        status = check_database_status()
        print(f"Database Status:")
        print(f"  Exists: {status['exists']}")
        print(f"  Path: {status['path']}")
        print(f"  Size: {status['size']} bytes")
        print(f"  Tables: {len(status['tables'])}")
        for table in status['tables']:
            print(f"    - {table}")
        if status['error']:
            print(f"  Error: {status['error']}")
            sys.exit(1)
        
    elif command == "test-data":
        success = create_test_data()
        print("✅ Test data created" if success else "❌ Test data creation failed")
        sys.exit(0 if success else 1)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


# Campaign management functions for API support
async def get_campaign_by_id(campaign_id: str, user_id: str) -> Optional[dict]:
    """Get a campaign by ID for a specific user."""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM campaigns 
            WHERE id = ? AND user_id = ?
        """, (campaign_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Convert row to dict and parse JSON fields
            campaign = dict(row)
            
            # Parse JSON fields if they exist
            if campaign.get('business_context'):
                import json
                campaign['business_analysis'] = json.loads(campaign['business_context'])
            
            return campaign
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get campaign {campaign_id}: {e}")
        return None


async def update_campaign_analysis(campaign_id: str, user_id: str, ai_analysis: dict) -> Optional[dict]:
    """Update the AI analysis for a campaign."""
    try:
        import json
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Update the campaign with new AI analysis
        cursor.execute("""
            UPDATE campaigns 
            SET business_context = ?, updated_at = datetime('now')
            WHERE id = ? AND user_id = ?
        """, (json.dumps(ai_analysis), campaign_id, user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return None
        
        conn.commit()
        
        # Return the updated campaign
        cursor.execute("""
            SELECT * FROM campaigns 
            WHERE id = ? AND user_id = ?
        """, (campaign_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            campaign = dict(row)
            campaign['business_analysis'] = ai_analysis
            return campaign
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to update campaign analysis {campaign_id}: {e}")
        return None

async def save_campaign_chat_history(campaign_id: str, user_id: str, conversation_history: list) -> bool:
    """Save conversation history for a campaign."""
    try:
        import json
        
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Check if campaign exists
        cursor.execute("""
            SELECT id FROM campaigns 
            WHERE id = ? AND user_id = ?
        """, (campaign_id, user_id))
        
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Update or insert conversation history
        cursor.execute("""
            INSERT OR REPLACE INTO campaign_chat_history (
                campaign_id, user_id, conversation_history, updated_at
            ) VALUES (?, ?, ?, datetime('now'))
        """, (campaign_id, user_id, json.dumps(conversation_history)))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to save chat history for campaign {campaign_id}: {e}")
        return False

async def get_campaign_chat_history(campaign_id: str, user_id: str) -> list:
    """Get conversation history for a campaign."""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_history FROM campaign_chat_history 
            WHERE campaign_id = ? AND user_id = ?
        """, (campaign_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            import json
            return json.loads(row[0])
        
        return []
        
    except Exception as e:
        logger.error(f"Failed to get chat history for campaign {campaign_id}: {e}")
        return [] 