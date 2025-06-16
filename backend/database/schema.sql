-- Video Venture Launch Database Schema
-- Author: JP + 2025-06-16
-- Description: Complete SQLite schema for MVP local database
-- Version: 1.0.1 - Updated to align with test expectations

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    username TEXT UNIQUE NOT NULL,         -- Unique username for login
    email TEXT UNIQUE NOT NULL,            -- Email address (unique)
    password_hash TEXT,                    -- Bcrypt hashed password (optional for tests)
    full_name TEXT,                        -- User's full name (aligned with tests)
    profile_data TEXT,                     -- JSON: preferences, settings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,                  -- Track user activity
    is_active BOOLEAN DEFAULT TRUE,        -- Soft delete capability
    
    -- Constraints
    CONSTRAINT users_email_format CHECK (email LIKE '%@%.%'),
    CONSTRAINT users_username_length CHECK (length(username) >= 3)
);

-- ============================================================================
-- CAMPAIGNS TABLE
-- ============================================================================
CREATE TABLE campaigns (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    name TEXT NOT NULL,                     -- Campaign name
    description TEXT,                       -- Campaign description (aligned with tests)
    business_description TEXT,              -- Business context description
    objective TEXT,                         -- Campaign objective
    objectives TEXT,                        -- Campaign objectives (aligned with tests)
    campaign_type TEXT DEFAULT 'general',  -- 'product', 'service', 'brand', 'event', 'general'
    creativity_level INTEGER DEFAULT 5,    -- 1-10 scale for AI creativity
    target_audience TEXT,                   -- Target audience description
    
    -- Business Context URLs
    business_website TEXT,                  -- Primary business website
    about_page_url TEXT,                   -- About page URL
    product_service_url TEXT,              -- Product/service page URL
    
    -- Campaign Configuration
    preferred_design TEXT,                  -- Design preferences
    brand_voice TEXT,                      -- Brand voice guidelines
    campaign_settings TEXT,                -- JSON: additional settings
    
    -- AI Generated Context
    ai_summary TEXT,                       -- AI-generated business summary
    ai_analysis TEXT,                      -- AI analysis results (aligned with tests)
    business_context TEXT,                 -- JSON: comprehensive business analysis
    suggested_themes TEXT,                 -- JSON: array of suggested themes
    suggested_tags TEXT,                   -- JSON: array of suggested tags
    selected_themes TEXT,                  -- JSON: user-selected themes
    selected_tags TEXT,                    -- JSON: user-selected tags
    
    -- Metadata
    user_id TEXT NOT NULL,                 -- Foreign key to users table
    status TEXT DEFAULT 'draft',           -- 'draft', 'active', 'completed', 'archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,                -- When campaign was completed
    
    -- Foreign Key Constraints
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT campaigns_name_length CHECK (length(name) >= 1),
    CONSTRAINT campaigns_creativity_range CHECK (creativity_level BETWEEN 1 AND 10),
    CONSTRAINT campaigns_status_values CHECK (status IN ('draft', 'active', 'completed', 'archived')),
    CONSTRAINT campaigns_type_values CHECK (campaign_type IN ('product', 'service', 'brand', 'event', 'general'))
);

-- ============================================================================
-- GENERATED CONTENT TABLE
-- ============================================================================
CREATE TABLE generated_content (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    campaign_id TEXT NOT NULL,             -- Foreign key to campaigns table
    content_type TEXT NOT NULL,            -- 'idea', 'social_post', 'video_prompt', 'hashtags', 'text_image'
    platform TEXT,                        -- 'linkedin', 'twitter', 'instagram', 'facebook', 'tiktok', 'general'
    
    -- Content Data
    title TEXT,                            -- Content title/headline
    content_text TEXT,                     -- Main content text
    content_data TEXT,                     -- JSON: complete content structure
    
    -- AI Generation Context
    generation_prompt TEXT,                -- Prompt used to generate content
    ai_model TEXT,                         -- AI model used (e.g., 'gemini-2.0-flash')
    ai_metadata TEXT,                      -- JSON: AI generation metadata (aligned with tests)
    generation_parameters TEXT,            -- JSON: temperature, max_tokens, etc.
    
    -- Content Metadata
    hashtags TEXT,                         -- JSON: array of hashtags
    mentions TEXT,                         -- JSON: array of mentions
    media_urls TEXT,                       -- JSON: array of media URLs
    engagement_score REAL,                 -- Predicted engagement score (0-1)
    
    -- User Interaction
    is_selected BOOLEAN DEFAULT FALSE,     -- User selected this content
    is_published BOOLEAN DEFAULT FALSE,    -- Content has been published
    user_edits TEXT,                       -- JSON: user modifications
    user_rating INTEGER,                   -- User rating 1-5
    
    -- Scheduling
    scheduled_for TIMESTAMP,               -- When content is scheduled to publish
    published_at TIMESTAMP,                -- When content was actually published
    platform_post_id TEXT,                -- External platform post ID
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT content_type_values CHECK (content_type IN ('idea', 'social_post', 'video_prompt', 'hashtags', 'summary', 'text_image')),
    CONSTRAINT platform_values CHECK (platform IN ('linkedin', 'twitter', 'instagram', 'facebook', 'tiktok', 'general') OR platform IS NULL),
    CONSTRAINT user_rating_range CHECK (user_rating BETWEEN 1 AND 5 OR user_rating IS NULL),
    CONSTRAINT engagement_score_range CHECK (engagement_score BETWEEN 0 AND 1 OR engagement_score IS NULL)
);

-- ============================================================================
-- UPLOADED FILES TABLE
-- ============================================================================
CREATE TABLE uploaded_files (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    campaign_id TEXT NOT NULL,             -- Foreign key to campaigns table
    user_id TEXT NOT NULL,                 -- Foreign key to users table
    
    -- File Information
    original_filename TEXT NOT NULL,       -- Original uploaded filename
    stored_filename TEXT NOT NULL,         -- Stored filename (UUID-based)
    file_path TEXT NOT NULL,               -- Relative path to file
    file_size INTEGER NOT NULL,            -- File size in bytes
    mime_type TEXT NOT NULL,               -- MIME type
    file_category TEXT NOT NULL,           -- 'image', 'document', 'campaign_asset', 'other'
    
    -- File Analysis
    analysis_status TEXT DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    analysis_results TEXT,                 -- JSON: AI analysis results
    extracted_text TEXT,                   -- Extracted text from documents
    image_analysis TEXT,                   -- JSON: image analysis results
    
    -- Metadata
    upload_source TEXT,                    -- 'web_upload', 'drag_drop', 'api'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT file_category_values CHECK (file_category IN ('image', 'document', 'campaign_asset', 'other')),
    CONSTRAINT analysis_status_values CHECK (analysis_status IN ('pending', 'processing', 'completed', 'failed')),
    CONSTRAINT file_size_positive CHECK (file_size > 0)
);

-- ============================================================================
-- CAMPAIGN TEMPLATES TABLE
-- ============================================================================
CREATE TABLE campaign_templates (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    name TEXT NOT NULL,                     -- Template name
    description TEXT,                       -- Template description
    category TEXT NOT NULL,                -- 'product_launch', 'brand_awareness', 'event_promotion', 'custom'
    
    -- Template Configuration
    template_data TEXT NOT NULL,           -- JSON: complete template structure
    default_settings TEXT,                 -- JSON: default campaign settings
    prompt_templates TEXT,                 -- JSON: AI prompt templates
    
    -- Usage Tracking
    usage_count INTEGER DEFAULT 0,         -- How many times template was used
    is_public BOOLEAN DEFAULT FALSE,       -- Available to all users
    created_by TEXT,                       -- User ID who created template
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    
    -- Check Constraints
    CONSTRAINT template_category_values CHECK (category IN ('product_launch', 'brand_awareness', 'event_promotion', 'custom')),
    CONSTRAINT template_name_length CHECK (length(name) >= 1)
);

-- ============================================================================
-- USER SESSIONS TABLE
-- ============================================================================
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,                    -- Session ID (UUID v4)
    user_id TEXT NOT NULL,                 -- Foreign key to users table
    session_token TEXT UNIQUE NOT NULL,    -- Unique session token
    session_data TEXT,                     -- JSON: session-specific data
    ip_address TEXT,                       -- Client IP address
    user_agent TEXT,                       -- Client user agent
    expires_at TIMESTAMP NOT NULL,         -- Session expiration time
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,        -- Session active status
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT session_expires_future CHECK (expires_at > created_at)
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Users table indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Campaigns table indexes
CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_type ON campaigns(campaign_type);
CREATE INDEX idx_campaigns_created_at ON campaigns(created_at);
CREATE INDEX idx_campaigns_updated_at ON campaigns(updated_at);

-- Generated content table indexes
CREATE INDEX idx_content_campaign_id ON generated_content(campaign_id);
CREATE INDEX idx_content_type ON generated_content(content_type);
CREATE INDEX idx_content_platform ON generated_content(platform);
CREATE INDEX idx_content_selected ON generated_content(is_selected);
CREATE INDEX idx_content_published ON generated_content(is_published);
CREATE INDEX idx_content_created_at ON generated_content(created_at);

-- Uploaded files table indexes
CREATE INDEX idx_files_campaign_id ON uploaded_files(campaign_id);
CREATE INDEX idx_files_user_id ON uploaded_files(user_id);
CREATE INDEX idx_files_category ON uploaded_files(file_category);
CREATE INDEX idx_files_analysis_status ON uploaded_files(analysis_status);
CREATE INDEX idx_files_created_at ON uploaded_files(created_at);

-- Campaign templates table indexes
CREATE INDEX idx_templates_category ON campaign_templates(category);
CREATE INDEX idx_templates_public ON campaign_templates(is_public);
CREATE INDEX idx_templates_created_by ON campaign_templates(created_by);
CREATE INDEX idx_templates_usage ON campaign_templates(usage_count);

-- User sessions table indexes
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_sessions_active ON user_sessions(is_active);
CREATE INDEX idx_sessions_last_activity ON user_sessions(last_activity);

-- ============================================================================
-- COMPOSITE INDEXES FOR COMPLEX QUERIES
-- ============================================================================

-- Campaign analytics
CREATE INDEX idx_campaigns_user_status ON campaigns(user_id, status);
CREATE INDEX idx_campaigns_type_status ON campaigns(campaign_type, status);

-- Content analytics
CREATE INDEX idx_content_campaign_type ON generated_content(campaign_id, content_type);
CREATE INDEX idx_content_platform_selected ON generated_content(platform, is_selected);
CREATE INDEX idx_content_rating_engagement ON generated_content(user_rating, engagement_score);

-- File management
CREATE INDEX idx_files_campaign_category ON uploaded_files(campaign_id, file_category);
CREATE INDEX idx_files_user_category ON uploaded_files(user_id, file_category);

-- Session management
CREATE INDEX idx_sessions_user_active ON user_sessions(user_id, is_active);
CREATE INDEX idx_sessions_expires_active ON user_sessions(expires_at, is_active);

-- Template usage
CREATE INDEX idx_templates_public_category ON campaign_templates(is_public, category);

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================
CREATE TABLE schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert current schema version
INSERT INTO schema_version (version, description) 
VALUES ('1.0.1', 'Updated schema to align with test expectations - full_name, description, objectives, ai_analysis fields');

-- ============================================================================
-- DATABASE VIEWS FOR ANALYTICS
-- ============================================================================

-- Campaign summary view with user information
CREATE VIEW campaign_summary AS
SELECT 
    c.id,
    c.name,
    c.campaign_type,
    c.status,
    c.created_at,
    c.updated_at,
    u.username,
    u.full_name,
    COUNT(gc.id) as content_count,
    COUNT(CASE WHEN gc.is_selected = 1 THEN 1 END) as selected_content_count
FROM campaigns c
LEFT JOIN users u ON c.user_id = u.id
LEFT JOIN generated_content gc ON c.id = gc.campaign_id
GROUP BY c.id, c.name, c.campaign_type, c.status, c.created_at, c.updated_at, u.username, u.full_name;

-- User activity summary
CREATE VIEW user_activity_summary AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.created_at as user_since,
    u.last_login,
    COUNT(DISTINCT c.id) as total_campaigns,  -- Fixed: use DISTINCT to avoid duplicate counting
    COUNT(DISTINCT CASE WHEN c.status = 'active' THEN c.id END) as active_campaigns,  -- Fixed: use DISTINCT
    COUNT(DISTINCT CASE WHEN c.status = 'completed' THEN c.id END) as completed_campaigns,  -- Fixed: use DISTINCT
    COUNT(gc.id) as total_content_generated
FROM users u
LEFT JOIN campaigns c ON u.id = c.user_id
LEFT JOIN generated_content gc ON c.id = gc.campaign_id
GROUP BY u.id, u.username, u.email, u.created_at, u.last_login;

-- Content performance view
CREATE VIEW content_performance AS
SELECT 
    gc.id,
    gc.campaign_id,
    gc.content_type,
    gc.platform,
    gc.title,
    gc.is_selected,
    gc.is_published,
    gc.user_rating,
    gc.engagement_score,
    gc.created_at,
    c.name as campaign_name,
    u.username
FROM generated_content gc
JOIN campaigns c ON gc.campaign_id = c.id
JOIN users u ON c.user_id = u.id; 