# Video Content Generation Feature Documentation
# FILENAME: Video-Content-Generation.md
# DESCRIPTION/PURPOSE: Documentation of video content generation feature requirements and implementation
# Author: JP + 2025-06-23

## Feature Overview

**Purpose**: Generate AI-powered video content for social media marketing campaigns with inline preview functionality similar to YouTube thumbnails.

**Current Status**: ❌ **BROKEN** - Videos are generating but not displaying properly in the UI

**Priority**: **CRITICAL** - Core premium feature for hackathon demo

## Intended User Experience

### Expected Behavior (YouTube-Style Video Previews)

1. **User clicks "Generate Text + Video Posts" button**
2. **AI generates marketing videos using Veo 2.0 model**
3. **Videos appear as inline thumbnails in each post card**
4. **Videos should auto-play on hover (like YouTube)**
5. **Videos should have play/pause controls**
6. **Videos should be immediately viewable without downloads**
7. **Videos should load quickly with proper caching**

### Current Broken Behavior

1. **User clicks "Generate Text + Video Posts" button** ✅
2. **AI generates marketing videos successfully** ✅ (Backend working)
3. **Videos show "Video Preview Unavailable" message** ❌ **BROKEN**
4. **Users must click "Download Video" to see content** ❌ **BROKEN**
5. **No inline preview functionality** ❌ **BROKEN**
6. **Poor user experience** ❌ **BROKEN**

## Technical Requirements

### Video Generation (Backend) ✅ WORKING

**API Endpoint**: `POST /api/v1/content/generate-visuals`
**Video Model**: Veo 2.0 (Google's AI video generation)
**Video Specs**:
- Format: MP4
- Duration: 5-15 seconds
- Resolution: 720p minimum
- Aspect Ratio: 16:9 or 9:16 (social media optimized)
- File Size: 2-5MB typical

**Current Status**: ✅ **WORKING CORRECTLY**
```bash
# Test shows videos are being generated successfully
curl -s http://localhost:8000/api/v1/content/videos/51c99b72/curr_04c0e5b1_0.mp4 -I
# Returns: HTTP/1.1 200 OK, content-type: video/mp4, content-length: 2287684
```

### Video Display (Frontend) ❌ BROKEN

**Location**: `src/pages/IdeationPage.tsx` (lines ~1500-1600)
**Component**: Video preview in post cards
**Required Features**:

1. **Inline Video Player**
   ```html
   <video 
     src={post.content.videoUrl}
     className="w-full h-48 object-cover"
     controls
     autoPlay={false}
     muted
     loop
   />
   ```

2. **YouTube-Style Thumbnails**
   - Poster image for preview
   - Play button overlay
   - Hover effects
   - Loading states

3. **Responsive Design**
   - Mobile-friendly controls
   - Proper aspect ratios
   - Touch-friendly interface

4. **Performance Optimization**
   - Lazy loading
   - Video caching
   - Preload metadata only

## Current Implementation Issues

### 1. Video URL Mapping Problem

**Location**: `src/pages/IdeationPage.tsx` - `generateColumnPosts()` function

**Issue**: Backend returns `video_url` but frontend expects `videoUrl`

```typescript
// CURRENT BROKEN MAPPING:
transformedPosts = transformedPosts.map(post => {
  const visualPost = visualData.posts_with_visuals.find((vp: any) => vp.id === post.id);
  if (visualPost) {
    return {
      ...post,
      content: {
        ...post.content,
        // ❌ ISSUE: Backend field mapping
        videoUrl: visualPost.video_url || post.content.videoUrl  // May be undefined
      }
    };
  }
  return post;
});
```

**Root Cause**: Inconsistent field naming between backend and frontend

### 2. Video Loading Error Handling

**Location**: `src/pages/IdeationPage.tsx` (lines ~1550-1600)

**Current Error Handler**:
```typescript
onError={(e) => {
  console.error(`❌ VIDEO_ERROR: Post ${post.id} video failed to load:`, e);
  // Shows "Video Preview Unavailable" fallback
  // This is triggering incorrectly for valid videos
}}
```

**Problem**: Error handler is firing even for valid video URLs, causing fallback UI to show

### 3. CORS and Content-Type Issues

**Potential Issue**: Browser may be blocking video playback due to:
- CORS headers not properly configured
- Content-Type not set correctly
- Missing video codec support
- Security restrictions on localhost

### 4. Video Format Compatibility

**Browser Compatibility**:
- Chrome: MP4 (H.264) ✅
- Firefox: MP4 (H.264) ✅  
- Safari: MP4 (H.264) ✅
- Mobile: MP4 (H.264) ✅

**Current Backend Output**: MP4 with H.264 codec ✅ (Should work)

## Debugging Information

### Backend Video Generation Working ✅

```bash
# Video generation API test
curl -X POST http://localhost:8000/api/v1/content/generate-visuals \
  -H "Content-Type: application/json" \
  -d '{"social_posts": [{"id": "test", "type": "text_video", "content": "test"}]}'

# Response shows successful video generation:
{
  "posts_with_visuals": [{
    "video_url": "http://localhost:8000/api/v1/content/videos/51c99b72/curr_04c0e5b1_0.mp4",
    "video_metadata": {
      "model": "veo-2.0-generate-001",
      "duration": "5s",
      "format": "mp4",
      "resolution": "720p",
      "file_size_mb": 2.18
    }
  }]
}
```

### Frontend Video Display Broken ❌

**Console Errors** (Expected):
```
❌ VIDEO_ERROR: Post test-video-1 video failed to load
🔍 Video URL: http://localhost:8000/api/v1/content/videos/51c99b72/curr_04c0e5b1_0.mp4
```

**UI Result**: "Video Preview Unavailable" fallback shown instead of video player

## Required Fixes

### 1. HIGH PRIORITY: Fix Video URL Mapping

**File**: `src/pages/IdeationPage.tsx`
**Function**: `generateColumnPosts()`

```typescript
// FIXED MAPPING:
transformedPosts = transformedPosts.map(post => {
  const visualPost = visualData.posts_with_visuals.find((vp: any) => vp.id === post.id);
  if (visualPost && visualPost.video_url) {
    console.log(`🎬 MAPPING VIDEO: ${visualPost.video_url}`);
    return {
      ...post,
      content: {
        ...post.content,
        videoUrl: visualPost.video_url  // Ensure proper mapping
      }
    };
  }
  return post;
});
```

### 2. HIGH PRIORITY: Fix Video Loading Logic

**File**: `src/pages/IdeationPage.tsx`
**Component**: Video player component

```typescript
// IMPROVED VIDEO COMPONENT:
{post.content.videoUrl && (
  <div className="relative rounded-lg overflow-hidden bg-gray-800">
    <video 
      src={post.content.videoUrl}
      className="w-full h-48 object-cover"
      controls
      muted
      preload="metadata"
      onLoadStart={() => {
        console.log(`🎬 VIDEO_LOAD_START: ${post.id}`);
      }}
      onCanPlay={() => {
        console.log(`✅ VIDEO_CAN_PLAY: ${post.id}`);
      }}
      onError={(e) => {
        console.error(`❌ VIDEO_ERROR: ${post.id}`, e);
        // Only show fallback after confirming URL is invalid
      }}
    />
  </div>
)}
```

### 3. MEDIUM PRIORITY: Add YouTube-Style Features

**Features to Add**:
- Hover-to-play functionality
- Custom play button overlay
- Progress bar styling
- Thumbnail poster images
- Smooth loading animations

### 4. LOW PRIORITY: Performance Optimization

**Optimizations**:
- Lazy loading for videos below fold
- Video preloading strategies
- Caching improvements
- Bandwidth-aware loading

## Testing Strategy

### 1. Backend Video Generation Testing

```bash
# Test video generation
curl -X POST http://localhost:8000/api/v1/content/generate-visuals \
  -H "Content-Type: application/json" \
  -d '{"social_posts": [{"id": "test", "type": "text_video"}]}'

# Test video accessibility
curl -I http://localhost:8000/api/v1/content/videos/{campaign_id}/{filename}

# Verify video file validity
curl -s {video_url} -o test.mp4 && file test.mp4
```

### 2. Frontend Video Display Testing

**Test Cases**:
1. Generate text+video posts
2. Verify video URLs are properly mapped
3. Confirm videos load without errors
4. Test video controls functionality
5. Verify responsive behavior
6. Test error handling for invalid videos

### 3. Browser Compatibility Testing

**Test Matrix**:
- Chrome Desktop ✅
- Firefox Desktop ✅
- Safari Desktop ✅
- Chrome Mobile ✅
- Safari Mobile ✅

## Success Criteria

- [ ] Videos generate successfully (Backend) ✅ **ALREADY WORKING**
- [ ] Videos display as inline thumbnails (Frontend) ❌ **NEEDS FIX**
- [ ] Videos play with standard HTML5 controls ❌ **NEEDS FIX**
- [ ] No "Video Preview Unavailable" errors ❌ **NEEDS FIX**
- [ ] YouTube-style hover effects ❌ **FUTURE ENHANCEMENT**
- [ ] Mobile-responsive video players ❌ **NEEDS FIX**
- [ ] Proper loading states and error handling ❌ **NEEDS FIX**

## Demo Requirements for Hackathon

**Critical for Demo Success**:
1. **Videos must play inline** - Core premium feature
2. **Professional appearance** - YouTube-quality preview experience
3. **No technical errors** - Must work flawlessly during presentation
4. **Mobile compatibility** - Judges may test on mobile devices

**Demo Script Requirements**:
1. Show text+video generation in action
2. Demonstrate video quality and relevance
3. Highlight AI-powered video creation
4. Show professional social media ready content

## Implementation Timeline

**Immediate (Next 2 hours)**:
- [ ] Fix video URL mapping issue
- [ ] Resolve video loading errors
- [ ] Test video playback functionality
- [ ] Verify cross-browser compatibility

**Before Demo (Next 4 hours)**:
- [ ] Add YouTube-style thumbnails
- [ ] Implement hover effects
- [ ] Polish video player UI
- [ ] Test on mobile devices

**Post-Demo (Future)**:
- [ ] Advanced video controls
- [ ] Video editing capabilities
- [ ] Multiple video format support
- [ ] Advanced caching strategies

---

**Status**: Documented - Ready for Implementation
**Priority**: CRITICAL - Demo Blocker
**Estimated Fix Time**: 2-3 hours
**Last Updated**: 2025-06-23 