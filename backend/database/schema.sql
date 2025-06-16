-- Video Venture Launch Database Schema
-- Author: JP + 2025-06-16
-- Description: Complete SQLite schema for MVP local database
-- Version: 1.0.0

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE users (
    id TEXT PRIMARY KEY,                    -- UUID v4 format
    username TEXT UNIQUE NOT NULL,         -- Unique username for login
    email TEXT UNIQUE NOT NULL,            -- Email address (unique)
    password_hash TEXT NOT NULL,           -- Bcrypt hashed password
    first_name TEXT,                       -- User's first name
    last_name TEXT,                        -- User's last name
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
    business_description TEXT,              -- Business context description
    objective TEXT,                         -- Campaign objective
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
    content_type TEXT NOT NULL,            -- 'idea', 'social_post', 'video_prompt', 'hashtags'
    platform TEXT,                        -- 'linkedin', 'twitter', 'instagram', 'facebook', 'tiktok', 'general'
    
    -- Content Data
    title TEXT,                            -- Content title/headline
    content_text TEXT,                     -- Main content text
    content_data TEXT,                     -- JSON: complete content structure
    
    -- AI Generation Context
    generation_prompt TEXT,                -- Prompt used to generate content
    ai_model TEXT,                         -- AI model used (e.g., 'gemini-2.0-flash')
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
    CONSTRAINT content_type_values CHECK (content_type IN ('idea', 'social_post', 'video_prompt', 'hashtags', 'summary')),
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
    session_token TEXT UNIQUE NOT NULL,    -- Secure session token
    
    -- Session Data
    session_data TEXT,                     -- JSON: session information
    ip_address TEXT,                       -- Client IP address
    user_agent TEXT,                       -- Client user agent
    
    -- Session Lifecycle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,         -- Session expiration
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Foreign Key Constraints
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Check Constraints
    CONSTRAINT session_expires_future CHECK (expires_at > created_at)
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- User table indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Campaign table indexes
CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_type ON campaigns(campaign_type);
CREATE INDEX idx_campaigns_created_at ON campaigns(created_at);
CREATE INDEX idx_campaigns_updated_at ON campaigns(updated_at);

-- Generated content indexes
CREATE INDEX idx_content_campaign_id ON generated_content(campaign_id);
CREATE INDEX idx_content_type ON generated_content(content_type);
CREATE INDEX idx_content_platform ON generated_content(platform);
CREATE INDEX idx_content_selected ON generated_content(is_selected);
CREATE INDEX idx_content_published ON generated_content(is_published);
CREATE INDEX idx_content_created_at ON generated_content(created_at);

-- Uploaded files indexes
CREATE INDEX idx_files_campaign_id ON uploaded_files(campaign_id);
CREATE INDEX idx_files_user_id ON uploaded_files(user_id);
CREATE INDEX idx_files_category ON uploaded_files(file_category);
CREATE INDEX idx_files_analysis_status ON uploaded_files(analysis_status);
CREATE INDEX idx_files_created_at ON uploaded_files(created_at);

-- Campaign templates indexes
CREATE INDEX idx_templates_category ON campaign_templates(category);
CREATE INDEX idx_templates_public ON campaign_templates(is_public);
CREATE INDEX idx_templates_created_by ON campaign_templates(created_by);
CREATE INDEX idx_templates_usage ON campaign_templates(usage_count);

-- Session indexes
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_sessions_active ON user_sessions(is_active);
CREATE INDEX idx_sessions_last_activity ON user_sessions(last_activity);

-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Insert default campaign templates
INSERT INTO campaign_templates (
    id, name, description, category, template_data, default_settings, 
    prompt_templates, is_public, created_by
) VALUES 
(
    'template-product-launch-001',
    'Product Launch Campaign',
    'Comprehensive template for launching new products with social media content generation',
    'product_launch',
    '{"sections": ["business_context", "product_details", "target_audience", "key_messages"], "required_fields": ["product_name", "launch_date", "key_features"]}',
    '{"creativity_level": 7, "platforms": ["linkedin", "twitter", "instagram"], "content_types": ["social_post", "hashtags"]}',
    '{"business_analysis": "Analyze this product launch focusing on unique value proposition and market positioning", "content_generation": "Create engaging social media content for {product_name} launch targeting {target_audience}"}',
    TRUE,
    NULL
),
(
    'template-brand-awareness-001',
    'Brand Awareness Campaign',
    'Build brand recognition and engagement across social platforms',
    'brand_awareness',
    '{"sections": ["brand_story", "values", "target_audience", "brand_voice"], "required_fields": ["brand_name", "core_values", "brand_personality"]}',
    '{"creativity_level": 6, "platforms": ["linkedin", "twitter", "instagram", "facebook"], "content_types": ["social_post", "hashtags"]}',
    '{"business_analysis": "Analyze brand positioning and unique differentiators for {brand_name}", "content_generation": "Create brand awareness content that showcases {brand_name} values and personality"}',
    TRUE,
    NULL
),
(
    'template-event-promotion-001',
    'Event Promotion Campaign',
    'Promote events, webinars, and conferences with targeted content',
    'event_promotion',
    '{"sections": ["event_details", "speakers", "agenda", "target_audience"], "required_fields": ["event_name", "event_date", "event_type"]}',
    '{"creativity_level": 8, "platforms": ["linkedin", "twitter", "facebook"], "content_types": ["social_post", "hashtags"]}',
    '{"business_analysis": "Analyze event value proposition and attendee benefits for {event_name}", "content_generation": "Create compelling event promotion content for {event_name} targeting {target_audience}"}',
    TRUE,
    NULL
);

-- ============================================================================
-- DATABASE VERSION TRACKING
-- ============================================================================
CREATE TABLE schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES 
('1.0.0', 'Initial database schema with core tables and indexes');

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
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
    u.first_name,
    u.last_name,
    COUNT(gc.id) as content_count,
    COUNT(CASE WHEN gc.is_selected = TRUE THEN 1 END) as selected_content_count
FROM campaigns c
JOIN users u ON c.user_id = u.id
LEFT JOIN generated_content gc ON c.id = gc.campaign_id
GROUP BY c.id, c.name, c.campaign_type, c.status, c.created_at, c.updated_at, 
         u.username, u.first_name, u.last_name;

-- User activity summary view
CREATE VIEW user_activity_summary AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.created_at as user_since,
    u.last_login,
    COUNT(c.id) as total_campaigns,
    COUNT(CASE WHEN c.status = 'active' THEN 1 END) as active_campaigns,
    COUNT(CASE WHEN c.status = 'completed' THEN 1 END) as completed_campaigns,
    COUNT(gc.id) as total_content_generated
FROM users u
LEFT JOIN campaigns c ON u.id = c.user_id
LEFT JOIN generated_content gc ON c.id = gc.campaign_id
WHERE u.is_active = TRUE
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
JOIN users u ON c.user_id = u.id
ORDER BY gc.created_at DESC; 