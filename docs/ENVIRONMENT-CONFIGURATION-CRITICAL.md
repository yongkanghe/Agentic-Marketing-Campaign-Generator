# CRITICAL: Environment Variable Configuration
**FILENAME**: ENVIRONMENT-CONFIGURATION-CRITICAL.md  
**DESCRIPTION/PURPOSE**: Critical configuration guidelines for environment variables  
**Author**: JP + 2025-06-18

## 🚨 CRITICAL ISSUE: NO QUOTES IN ENVIRONMENT VARIABLES

### Problem Overview
Environment variables with quotes cause **integer parsing errors** and **API failures** that result in:
- Content generation flickering and infinite "AI Processing..." loops
- `invalid literal for int() with base 10: '"4"'` errors
- Gemini API authentication failures
- Visual content generation timeouts

### ✅ CORRECT Environment Variable Format

```bash
# ✅ CORRECT - No quotes around values
GEMINI_API_KEY=AIzaSyBrT9zjpwyISoYik5VfOOiEuQE5YH47D9A
GEMINI_MODEL=gemini-2.5-flash
MAX_TEXT_IMAGE_POSTS=4
MAX_TEXT_VIDEO_POSTS=4
IMAGE_MODEL=imagen-3.0-generate-002
VIDEO_MODEL=veo-2
```

### ❌ INCORRECT Environment Variable Format

```bash
# ❌ INCORRECT - Quotes cause parsing errors
GEMINI_API_KEY="AIzaSyBrT9zjpwyISoYik5VfOOiEuQE5YH47D9A"
GEMINI_MODEL="gemini-2.5-flash"
MAX_TEXT_IMAGE_POSTS="4"
MAX_TEXT_VIDEO_POSTS="4"
IMAGE_MODEL="imagen-3.0-generate-002"
VIDEO_MODEL="veo-2"
```

## Environment Files to Check

### Root Directory: `.env`
```bash
# AI Configuration
GEMINI_API_KEY=AIzaSyBrT9zjpwyISoYik5VfOOiEuQE5YH47D9A
GEMINI_MODEL=gemini-2.5-flash

# Content Generation Limits
MAX_TEXT_IMAGE_POSTS=4
MAX_TEXT_VIDEO_POSTS=4

# Visual Content Models
IMAGE_MODEL=imagen-3.0-generate-002
VIDEO_MODEL=veo-2
```

### Backend Directory: `backend/.env`
```bash
# AI Configuration
GEMINI_API_KEY=AIzaSyBrT9zjpwyISoYik5VfOOiEuQE5YH47D9A
GEMINI_MODEL=gemini-2.5-flash

# Content Generation Limits
MAX_TEXT_IMAGE_POSTS=4
MAX_TEXT_VIDEO_POSTS=4

# Visual Content Models
IMAGE_MODEL=imagen-3.0-generate-002
VIDEO_MODEL=veo-2
```

## Validation Commands

### Check for Quoted Values
```bash
# Check root .env for quotes
grep -E '".*"' .env

# Check backend .env for quotes  
grep -E '".*"' backend/.env

# Should return no results if properly configured
```

### Fix Quoted Values
```bash
# Remove quotes from GEMINI_MODEL
sed -i '' 's/GEMINI_MODEL="gemini-2.5-flash"/GEMINI_MODEL=gemini-2.5-flash/' .env
sed -i '' 's/GEMINI_MODEL="gemini-2.5-flash"/GEMINI_MODEL=gemini-2.5-flash/' backend/.env

# Remove quotes from MAX_TEXT_IMAGE_POSTS
sed -i '' 's/MAX_TEXT_IMAGE_POSTS="4"/MAX_TEXT_IMAGE_POSTS=4/' .env
sed -i '' 's/MAX_TEXT_IMAGE_POSTS="4"/MAX_TEXT_IMAGE_POSTS=4/' backend/.env

# Remove quotes from MAX_TEXT_VIDEO_POSTS
sed -i '' 's/MAX_TEXT_VIDEO_POSTS="4"/MAX_TEXT_VIDEO_POSTS=4/' .env
sed -i '' 's/MAX_TEXT_VIDEO_POSTS="4"/MAX_TEXT_VIDEO_POSTS=4/' backend/.env

# Remove quotes from IMAGE_MODEL
sed -i '' 's/IMAGE_MODEL="imagen-3.0-generate-002"/IMAGE_MODEL=imagen-3.0-generate-002/' .env
sed -i '' 's/IMAGE_MODEL="imagen-3.0-generate-002"/IMAGE_MODEL=imagen-3.0-generate-002/' backend/.env

# Remove quotes from VIDEO_MODEL
sed -i '' 's/VIDEO_MODEL="veo-2"/VIDEO_MODEL=veo-2/' .env
sed -i '' 's/VIDEO_MODEL="veo-2"/VIDEO_MODEL=veo-2/' backend/.env
```

## Error Symptoms

### Integer Parsing Errors
```
ERROR:api.routes.content:Batch content generation failed: invalid literal for int() with base 10: '"4"'
```

### API Authentication Errors
```
ERROR:agents.visual_content_agent:"imagen-3.0-generate-002" generation failed: 400 BAD_REQUEST
```

### Frontend Symptoms
- Infinite "AI Processing..." state
- Content generation flickering
- Posts not generating properly
- "Failed to regenerate AI analysis" errors

## Testing Configuration

### Backend Health Check
```bash
curl -s http://localhost:8000/health | jq
```

Expected response:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "gemini_key_configured": true,
  "services": {
    "session_service": "in_memory",
    "artifact_service": "in_memory"
  }
}
```

### Content Generation Test
```bash
curl -X POST http://localhost:8000/api/v1/content/regenerate \
  -H "Content-Type: application/json" \
  -d '{
    "post_type": "text_url",
    "regenerate_count": 2,
    "business_context": {
      "company_name": "Test Company",
      "objective": "increase sales",
      "campaign_type": "service"
    }
  }'
```

## Development Workflow

### Before Starting Development
1. Verify environment variables have no quotes
2. Test backend health endpoint
3. Test content generation endpoint
4. Check logs for any parsing errors

### After Environment Changes
1. Restart all services: `make stop-all && make dev`
2. Verify health checks pass
3. Test content generation functionality
4. Monitor logs for errors

## Production Deployment

### Google Cloud Run Considerations
- Environment variables are automatically unquoted in Cloud Run
- Local development must match production behavior
- Use Cloud Run environment variable editor (no quotes needed)

### Heroku Considerations
- Environment variables are automatically unquoted in Heroku
- Use `heroku config:set VARIABLE=value` (no quotes)

## Troubleshooting

### Quick Fix for Quote Issues
```bash
# One-liner to remove all quotes from .env files
sed -i '' 's/="\([^"]*\)"/=\1/g' .env backend/.env
```

### Verify Fix
```bash
# Check that no quoted values remain
grep -E '=".*"' .env backend/.env
# Should return no results
```

### Restart Services
```bash
make stop-all
make dev
```

## Key Takeaways

1. **NEVER use quotes around environment variable values**
2. **Check both root `.env` and `backend/.env` files**
3. **Test after any environment changes**
4. **Monitor logs for integer parsing errors**
5. **Use validation commands to verify configuration**

This configuration is critical for proper AI agent functionality and content generation. 