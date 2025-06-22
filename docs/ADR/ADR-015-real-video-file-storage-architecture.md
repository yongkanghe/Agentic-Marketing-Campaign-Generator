# ADR-015: Real Video File Storage Architecture - Mirroring Image Storage Pattern

**Author:** JP + 2025-06-22  
**Status:** Implemented  
**Date:** 2025-06-22  
**Context:** Google ADK Hackathon - AI Marketing Campaign Post Generator  

## Context

The video generation system was initially implemented with mock URLs and JSON placeholders. However, the solution intent requires **REAL video generation** with actual MP4 files downloaded and stored locally, exactly mirroring the successful image storage architecture. Videos must be playable in the frontend, cached with `curr_` prefixes, and regeneratable while preserving the current video state.

## Problem Statement

1. **Mock Videos Not Sufficient**: Current implementation returns JSON placeholders instead of actual video files
2. **No Real File Storage**: Videos need to be downloaded and stored as actual MP4 files
3. **Cache Inconsistency**: Video caching doesn't follow the proven `curr_` prefix pattern used for images
4. **Frontend Playback Failure**: Video elements can't play JSON responses
5. **Regeneration Issues**: Need to preserve current videos while allowing regeneration like images

## Decision

### 1. Real Video File Storage Architecture

#### **File Storage Pattern (Mirroring Images)**
```
data/
├── videos/
│   ├── generated/
│   │   └── <campaign_id>/
│   │       ├── curr_<videohash>_<index>.mp4     # Current videos (persist across regeneration)
│   │       ├── <videohash>_<index>.mp4          # Historical videos (cleaned up)
│   │       └── thumb_<videohash>_<index>.jpg    # Video thumbnails
│   └── cache/
│       └── <campaign_id>/
│           ├── curr_<hash>.json                 # Current video metadata
│           └── <hash>.json                      # Historical metadata
```

#### **Current Video Management (`curr_` Prefix)**
- **Current Videos**: `curr_<videohash>_<index>.mp4` - Persist across app restarts
- **Historical Videos**: `<videohash>_<index>.mp4` - Cleaned up on regeneration
- **Cache Metadata**: `curr_<hash>.json` - Points to current video files
- **Regeneration**: New videos replace historical, current videos become historical

### 2. Real Veo 2.0 Integration

#### **Video Generation Flow**
```python
async def _generate_real_video(self, enhanced_prompt: str, index: int, campaign_id: str, business_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate real video using Veo 2.0 API and store as MP4 file."""
    
    # 1. Check cache first (curr_ prefixed)
    cached_video = self.cache.get_cached_video(enhanced_prompt, self.video_model, campaign_id)
    if cached_video:
        return cached_video_response
    
    # 2. Generate with Veo 2.0
    config = GenerateVideosConfig(
        prompt=veo_prompt,
        duration_seconds=8,
        aspect_ratio="16:9",
        fps=24,
        quality="standard"
    )
    
    response = await self.client.aio.models.generate_videos(
        model=self.video_model,
        config=config
    )
    
    # 3. Download and store as actual MP4 file
    video_filename = f"curr_{video_hash}_{index}.mp4"
    video_path = self.video_storage_dir / campaign_id / video_filename
    
    # Save video bytes to file
    with open(video_path, 'wb') as f:
        f.write(video_bytes)
    
    # 4. Create HTTP URL for frontend
    video_url = f"http://localhost:8000/api/v1/content/videos/{campaign_id}/{video_filename}"
    
    # 5. Cache metadata with curr_ prefix
    self.cache.cache_video(enhanced_prompt, self.video_model, campaign_id, video_url, is_current=True)
    
    return video_response
```

#### **Video Serving Endpoint**
```python
@router.get("/videos/{campaign_id}/{filename}")
async def serve_generated_video(campaign_id: str, filename: str):
    """Serve actual MP4 files with proper video headers."""
    video_path = Path(f"data/videos/generated/{campaign_id}/{filename}")
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Accept-Ranges": "bytes",  # Enable video seeking
            "Content-Disposition": f"inline; filename={filename}"
        }
    )
```

### 3. Cache Management Strategy

#### **Current Video Preservation**
```python
def _generate_current_cache_key(self, prompt: str, model: str, campaign_id: str) -> str:
    """Generate current cache key with curr_ prefix."""
    base_key = self._generate_cache_key(prompt, model, campaign_id)
    return f"curr_{base_key}"

def preserve_current_videos(self, campaign_id: str):
    """Move current videos to historical before regeneration."""
    campaign_dir = self._get_campaign_cache_dir(campaign_id)
    
    # Move curr_*.json to regular *.json
    for curr_file in campaign_dir.glob("curr_*.json"):
        historical_file = campaign_dir / curr_file.name.replace("curr_", "")
        curr_file.rename(historical_file)
    
    # Move curr_*.mp4 to regular *.mp4 in generated directory
    video_dir = Path(f"data/videos/generated/{campaign_id}")
    for curr_video in video_dir.glob("curr_*.mp4"):
        historical_video = video_dir / curr_video.name.replace("curr_", "")
        curr_video.rename(historical_video)
```

#### **Cleanup Strategy**
```python
def cleanup_old_videos(self):
    """Clean up historical videos, keep current videos."""
    for campaign_dir in self.cache_base_dir.iterdir():
        if campaign_dir.is_dir():
            # Remove historical cache files (keep curr_*)
            for cache_file in campaign_dir.glob("*.json"):
                if not cache_file.name.startswith("curr_"):
                    cache_file.unlink()
            
            # Remove historical video files (keep curr_*)
            video_dir = Path(f"data/videos/generated/{campaign_dir.name}")
            if video_dir.exists():
                for video_file in video_dir.glob("*.mp4"):
                    if not video_file.name.startswith("curr_"):
                        video_file.unlink()
```

### 4. Frontend Integration

#### **Real Video Playback**
```tsx
{post.content.videoUrl && (
  <div className="relative rounded-lg overflow-hidden bg-gray-800">
    <video 
      src={post.content.videoUrl}  // Real MP4 URL
      className="w-full h-48 object-cover"
      controls
      preload="metadata"
      muted
      playsInline
      onLoadedData={() => {
        console.log(`✅ REAL_VIDEO_LOADED: ${post.id} - MP4 file loaded successfully`);
      }}
      onError={(e) => {
        console.error(`❌ VIDEO_ERROR: Failed to load MP4 file:`, e);
        // Show error fallback
      }}
    />
    {/* Debug overlay showing file type */}
    <div className="absolute top-1 right-1 bg-black/50 text-white text-xs px-1 rounded">
      {post.content.videoUrl?.includes('curr_') ? 'Current MP4' : 'MP4'}
    </div>
  </div>
)}
```

### 5. Regeneration Workflow

#### **Video Regeneration Process**
1. **Preserve Current**: Move `curr_*.mp4` to `<hash>_*.mp4` (historical)
2. **Generate New**: Create new videos with Veo 2.0
3. **Store as Current**: Save new videos as `curr_<newhash>_*.mp4`
4. **Update Cache**: Update `curr_*.json` to point to new files
5. **Cleanup Historical**: Remove old historical files
6. **Frontend Update**: New URLs automatically refresh in frontend

#### **Cache Wipe on Restart**
```python
# In Makefile setup-logging target
@echo "🗑️ Cleaning up old cached videos (keeping current videos)..."
@python3 -c "from backend.agents.visual_content_agent import CampaignVideoCache; cache = CampaignVideoCache(); cache.cleanup_old_videos()" 2>/dev/null || echo "   Video cache cleanup skipped"
```

## Implementation Details

### 1. Veo 2.0 Configuration
```python
# Real video generation with proper quality settings
config = GenerateVideosConfig(
    prompt=enhanced_marketing_prompt,
    duration_seconds=8,  # Social media optimized
    aspect_ratio="16:9",  # Standard video format
    fps=24,  # Smooth playback
    quality="standard",  # Balance quality/cost
    safety_settings={
        "block_none": False,
        "block_few": True,
        "block_some": True,
        "block_most": True
    }
)
```

### 2. File Naming Convention
```python
def generate_video_filename(self, campaign_id: str, prompt: str, index: int, is_current: bool = True) -> str:
    """Generate consistent video filename."""
    video_hash = hashlib.md5(f"{campaign_id}_{prompt}_{time.time()}".encode()).hexdigest()[:8]
    prefix = "curr_" if is_current else ""
    return f"{prefix}{video_hash}_{index}.mp4"
```

### 3. Cost Control
- **Max Videos**: 4 videos per campaign (configurable)
- **Cache First**: Always check cache before generating
- **8-Second Duration**: Optimized for social media and cost
- **Standard Quality**: Balance between quality and generation cost

## Benefits

### 1. **Real Video Files**
- Actual MP4 files that play in browsers
- Proper video seeking and controls
- Professional video quality from Veo 2.0

### 2. **Consistent Architecture**
- Mirrors proven image storage pattern
- `curr_` prefix system for current state management
- Predictable file organization

### 3. **Efficient Regeneration**
- Preserve current videos during regeneration
- Clean historical files automatically
- Seamless frontend updates

### 4. **Production Ready**
- Local file storage for development
- HTTP serving with proper video headers
- Cloud storage migration ready

### 5. **Cost Optimization**
- Cache-first approach reduces API calls
- Cleanup prevents storage bloat
- Configurable generation limits

## Testing Strategy

### 1. **Video Generation Tests**
```python
def test_real_video_generation():
    """Test actual MP4 file creation and storage."""
    # Generate video
    # Verify MP4 file exists
    # Verify file size > 0
    # Verify HTTP URL works
    # Verify frontend can play video
```

### 2. **Cache Management Tests**
```python
def test_curr_prefix_management():
    """Test current video preservation and regeneration."""
    # Generate initial videos (curr_*.mp4)
    # Regenerate videos
    # Verify old videos moved to historical
    # Verify new videos have curr_ prefix
    # Verify cache consistency
```

### 3. **Frontend Integration Tests**
```python
def test_video_playback():
    """Test actual video playback in frontend."""
    # Generate real MP4 files
    # Load in video element
    # Verify playback works
    # Verify controls function
    # Verify error handling
```

## Future Enhancements

### 1. **Google Cloud Storage Migration**
```python
def upload_to_cloud_storage(self, video_path: Path, campaign_id: str) -> str:
    """Upload MP4 to Google Cloud Storage for production."""
    bucket_name = "video-venture-videos"
    blob_path = f"campaigns/{campaign_id}/{video_path.name}"
    # Upload file
    return f"https://storage.googleapis.com/{bucket_name}/{blob_path}"
```

### 2. **Video Thumbnails**
```python
def generate_video_thumbnail(self, video_path: Path) -> Path:
    """Generate thumbnail from video first frame."""
    # Extract first frame as JPEG
    # Save as thumb_<videohash>_<index>.jpg
    # Return thumbnail path
```

### 3. **Video Analytics**
- Video engagement tracking
- Playback completion rates
- A/B testing for video styles

## Conclusion

This architecture provides **real video generation and storage** that:
- **Generates Actual MP4 Files**: Using Veo 2.0 API with proper video download and storage
- **Mirrors Image Architecture**: Consistent `curr_` prefix pattern for state management
- **Enables Real Playback**: Frontend can play actual video files with full controls
- **Supports Regeneration**: Preserve current videos while generating new ones
- **Production Ready**: Local storage with cloud migration path

The implementation addresses the core requirement: **REAL video generation with actual downloadable/storable MP4 files** that play properly in the frontend, following the proven architectural patterns established for images. 