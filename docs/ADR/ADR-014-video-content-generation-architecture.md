# ADR-014: Video Content Generation Architecture with Veo 2.0 Integration

**Author:** JP + 2025-06-22  
**Status:** Implemented  
**Date:** 2025-06-22  
**Context:** Google ADK Hackathon - AI Marketing Campaign Post Generator  

## Context

The AI Marketing Campaign Post Generator requires video content generation capabilities for social media marketing campaigns. Users reported issues with video playback, identical video content, and lack of real video generation. This ADR documents the comprehensive video generation architecture using Google Veo 2.0.

## Decision

### 1. Video Generation Architecture

#### **Veo 2.0 Integration**
- **Model**: `veo-2.0-generate-001` for production-ready video generation
- **Duration**: 8-second videos optimized for social media
- **Format**: MP4, 720p resolution, 16:9 aspect ratio
- **Quality**: Professional marketing-grade videos with cinematic elements

#### **Enhanced Prompt Engineering**
```python
def _create_veo_marketing_prompt(self, base_prompt: str, business_context: Dict[str, Any], index: int) -> str:
    """Create Veo 2.0 optimized marketing prompt following Google's best practices."""
    veo_prompt = f"""Cinematic marketing video for {company_name}: {base_prompt}. 
    Professional commercial style, smooth camera movements, tracking shot. 
    Soft professional lighting with warm tones, golden hour ambiance. 
    Dynamic yet smooth motion, showcasing product/service naturally. 
    High-quality commercial video, {industry} industry focus. 
    Targeting {target_audience} with professional appeal. 
    8-second engaging sequence optimized for social media. 
    720p resolution, cinematic depth of field, professional grade."""
```

### 2. File Storage Architecture

#### **Directory Structure**
```
data/
├── videos/
│   ├── generated/
│   │   └── <campaign_id>/
│   │       ├── vid_<timestamp>_<uuid>_<index>.mp4
│   │       └── thumb_<filename>.jpg
│   └── cache/
│       └── <campaign_id>/
│           ├── curr_<hash>.json (current videos)
│           └── <hash>.json (historical videos)
```

#### **URL Generation Strategy**
- **Real Videos**: `http://localhost:8000/api/v1/content/videos/{campaign_id}/{filename}`
- **Mock Videos**: `http://localhost:8000/api/v1/content/videos/{campaign_id}/mock_{hash}_{index}.mp4`
- **Thumbnails**: `http://localhost:8000/api/v1/content/videos/{campaign_id}/thumb_{filename}.jpg`

### 3. Caching Strategy

#### **Campaign-Specific Video Caching**
```python
class CampaignVideoCache:
    def _generate_current_cache_key(self, prompt: str, model: str, campaign_id: str) -> str:
        """Generate current cache key with curr_ prefix."""
        base_key = self._generate_cache_key(prompt, model, campaign_id)
        return f"curr_{base_key}"
```

#### **Cache Metadata Structure**
```json
{
  "video_url": "http://localhost:8000/api/v1/content/videos/campaign123/vid_123456_abc123_0.mp4",
  "prompt": "Enhanced marketing prompt with business context",
  "model": "veo-2.0-generate-001",
  "campaign_id": "campaign123",
  "cached_at": "2025-06-22T23:01:57Z",
  "is_current": true,
  "duration_seconds": 8,
  "format": "mp4",
  "resolution": "720p",
  "aspect_ratio": "16:9"
}
```

### 4. Frontend Video Playback Enhancement

#### **Enhanced Video Component**
```tsx
<video 
  src={post.content.videoUrl}
  className="w-full h-48 object-cover"
  controls
  preload="metadata"
  muted
  playsInline
  onLoadedData={() => console.log(`✅ VIDEO_LOADED: ${post.id}`)}
  onError={(e) => {
    // Graceful error handling with fallback UI
    container.innerHTML = `
      <div class="flex flex-col items-center justify-center h-48">
        <div class="text-4xl mb-2">🎬</div>
        <p class="text-sm text-gray-400">Video Preview Not Available</p>
        <a href="${videoUrl}" target="_blank">Open Video</a>
      </div>
    `;
  }}
/>
```

#### **Debug Overlays and Logging**
- **Video Type Indicators**: Mock, Local, External
- **Loading States**: Load start, loaded data, can play events
- **Error Handling**: Graceful fallback to download links
- **Play Button Overlay**: Enhanced user experience

### 5. API Endpoints

#### **Video Serving Endpoint**
```python
@router.get("/videos/{campaign_id}/{filename}")
async def serve_generated_video(campaign_id: str, filename: str):
    """Serve generated videos with proper headers and security validation."""
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Accept-Ranges": "bytes"  # Enable video seeking
        }
    )
```

#### **Cache Management Endpoints**
- `GET /api/v1/content/videos/cache/stats` - Video cache statistics
- `POST /api/v1/content/videos/cache/clear` - Clear video cache

### 6. Business Context Integration

#### **Industry-Specific Video Enhancement**
```python
def _enhance_video_prompt_with_context(self, base_prompt: str, business_context: Dict[str, Any]) -> str:
    if industry == 'furniture':
        enhanced_prompt += f", professional furniture showcase, lifestyle setting"
    elif industry == 'technology':
        enhanced_prompt += f", modern technology environment, innovation focus"
    elif industry == 'consulting':
        enhanced_prompt += f", professional business environment, corporate setting"
```

#### **Unique Video Generation Per Campaign**
- **Hash-Based Uniqueness**: `campaign_id + prompt + company_name + index`
- **Business Context Metadata**: Company name, industry, target audience
- **Marketing Optimization**: 8-second duration, social media aspect ratio

## Implementation Details

### 1. Veo 2.0 Configuration
```python
config = GenerateVideosConfig(
    prompt=veo_prompt,
    duration_seconds=8,
    aspect_ratio="16:9",
    fps=24,
    quality="standard",
    safety_settings={
        "block_none": False,
        "block_few": True,
        "block_some": True,
        "block_most": True
    }
)
```

### 2. Cost Control Strategy
- **Max Videos Limit**: 4 videos per campaign (configurable via `MAX_TEXT_VIDEO_POSTS`)
- **Cache-First Approach**: Check cache before generating new videos
- **Enhanced Mock Mode**: Fallback when Veo 2.0 unavailable

### 3. Error Handling Hierarchy
1. **Real Veo 2.0 Generation** → Success
2. **Enhanced Mock Generation** → Business context + unique URLs
3. **Fallback Generation** → Standard placeholder

## Benefits

### 1. **Unique Video Content**
- Each campaign generates unique videos based on business context
- No more identical videos across different campaigns
- Hash-based uniqueness ensures variety

### 2. **Professional Video Quality**
- 8-second duration optimized for social media
- Cinematic quality with professional lighting and movement
- Industry-specific context integration

### 3. **Efficient Caching**
- Campaign-specific caching prevents cross-contamination
- Current vs historical video management
- Metadata-only caching (no large file storage in JSON)

### 4. **Enhanced User Experience**
- Proper video playback with controls
- Graceful error handling with fallback UI
- Debug information for troubleshooting

### 5. **Production Readiness**
- File-based storage architecture
- HTTP serving with proper headers
- Security validation for filenames

## Future Enhancements

### 1. **Image-to-Video Integration**
```python
# Use generated images as input for video generation
def _integrate_generated_images(self, images: List[str], video_prompt: str) -> str:
    """Enhance video generation with previously generated images."""
    return f"{video_prompt} incorporating visual elements from: {images[0]}"
```

### 2. **Google Cloud Storage Migration**
```python
# Production deployment with Cloud Storage
def _upload_to_cloud_storage(self, video_path: Path, campaign_id: str) -> str:
    """Upload video to Google Cloud Storage for production."""
    bucket_name = "video-venture-videos"
    blob_path = f"campaigns/{campaign_id}/{video_path.name}"
    return f"https://storage.googleapis.com/{bucket_name}/{blob_path}"
```

### 3. **Advanced Video Analytics**
- Video engagement scoring
- Duration optimization based on platform
- A/B testing for video styles

## Testing Strategy

### 1. **Video Generation Tests**
- Mock video generation validation
- Cache hit/miss scenarios
- Error handling verification

### 2. **File Serving Tests**
- HTTP endpoint functionality
- Security validation
- Cache header verification

### 3. **Frontend Integration Tests**
- Video playback functionality
- Error state handling
- Debug overlay validation

## Conclusion

This architecture provides a comprehensive solution for video content generation with:
- **Real Veo 2.0 Integration**: Production-ready video generation
- **Efficient File Storage**: HTTP-based serving with proper caching
- **Business Context Integration**: Industry-specific video enhancement
- **Enhanced User Experience**: Professional video playback with error handling
- **Production Scalability**: Cloud-ready architecture with cost controls

The implementation addresses all user concerns about video playback, uniqueness, and quality while maintaining the system's hackathon submission timeline and production readiness goals. 