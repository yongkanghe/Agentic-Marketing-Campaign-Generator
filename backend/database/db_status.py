#!/usr/bin/env python3
# Database Status Checker for Video Venture Launch
# Author: JP + 2025-06-16
# Description: Check database status and display table information
# Purpose: Support Makefile database operations with proper error handling

import sqlite3
import os
import sys
from pathlib import Path


def check_database_status(db_path: str = "data/video_venture_launch.db"):
    """Check database status and display comprehensive information"""
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Run 'make db-init' to create it.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✅ Database exists at", db_path)
        
        # Get file size
        file_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        print(f"📁 Database size: {file_size:.2f} MB")
        
        # List all tables
        print("📋 Tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        if not tables:
            print("  - No tables found")
            return False
            
        for table in tables:
            print(f"  - {table[0]}")
        
        # Data counts
        print("📊 Data counts:")
        
        # Core tables
        table_counts = {
            'campaigns': 'Campaigns',
            'users': 'Users', 
            'generated_content': 'Generated Content',
            'campaign_templates': 'Campaign Templates',
            'uploaded_files': 'Uploaded Files',
            'user_sessions': 'User Sessions'
        }
        
        for table_name, display_name in table_counts.items():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - {display_name}: {count}")
            except sqlite3.OperationalError:
                print(f"  - {display_name}: N/A (table not found)")
        
        # Schema version
        try:
            cursor.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1")
            version = cursor.fetchone()
            if version:
                print(f"📋 Schema Version: {version[0]}")
            else:
                print("📋 Schema Version: No version info")
        except sqlite3.OperationalError:
            print("📋 Schema Version: Unknown (legacy schema)")
        
        # Views
        print("👁️  Views:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        views = cursor.fetchall()
        
        if views:
            for view in views:
                print(f"  - {view[0]}")
        else:
            print("  - No views found")
        
        # Indexes
        print("🔍 Indexes:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        indexes = cursor.fetchall()
        
        if indexes:
            print(f"  - Total custom indexes: {len(indexes)}")
        else:
            print("  - No custom indexes found")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main function for command line usage"""
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/video_venture_launch.db"
    
    success = check_database_status(db_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 