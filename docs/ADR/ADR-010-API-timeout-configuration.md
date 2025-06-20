# ADR-010: API Timeout Configuration for AI Operations

**Date:** 2025-06-20  
**Status:** Accepted  
**Author:** JP  

## Context

The AI Marketing Campaign Post Generator frontend was experiencing timeout errors when generating content, particularly for image and video generation operations. Users reported:

1. **Timeout Errors**: "API Error: timeout of 30000ms exceeded" when generating content
2. **UI Flickering**: Buttons would flicker due to rapid timeout and state reset
3. **Multiple Clicks**: Users could click generation buttons multiple times due to quick timeouts
4. **Failed Operations**: AI content generation was failing prematurely

Analysis revealed that AI operations, especially those involving:
- Gemini text generation (5-15 seconds)
- Imagen image generation (15-30 seconds) 
- Veo video generation (20-45 seconds)
- Business analysis with multiple URLs (10-20 seconds)

Were exceeding the 30-second timeout limit, causing premature failures.

## Decision

**Increase API timeout from 30 seconds to 60 seconds** for all AI operations.

### Rationale

1. **AI Processing Time**: Real AI model inference can take 30-60 seconds
2. **User Experience**: Prevents premature timeouts and UI flickering
3. **Cost Control**: Reduces wasted API calls from timeout retries
4. **Production Readiness**: Aligns with Google Cloud AI service SLAs

### Implementation

```typescript
// src/lib/api.ts
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds timeout for AI operations
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## Consequences

### Positive
- ✅ Eliminates premature timeout errors
- ✅ Improves user experience with proper loading states
- ✅ Reduces wasted API calls and costs
- ✅ Aligns with AI service processing times
- ✅ Prevents UI flickering and multiple clicks

### Negative
- ⚠️ Longer wait time for genuine network failures
- ⚠️ Users may wait longer for actual errors

### Mitigations
- Implement proper loading indicators with progress feedback
- Add cancel functionality for long-running operations
- Monitor actual processing times and adjust if needed
- Implement circuit breaker pattern for repeated failures

## Alternatives Considered

1. **Keep 30 seconds**: Would continue causing timeout issues
2. **Increase to 120 seconds**: Too long for user experience
3. **Dynamic timeouts**: More complex, not needed for MVP
4. **Retry logic**: Would increase costs and complexity

## Implementation Status

- [x] Updated API client timeout configuration
- [x] Fixed button loading states to prevent multiple clicks
- [x] Added proper error handling for timeout scenarios
- [x] Updated documentation

## Monitoring

Track these metrics post-implementation:
- API timeout error rates
- Average AI operation completion times
- User retry behavior
- Cost impact from reduced failed requests

## References

- Google Gemini API documentation: Processing times 5-30 seconds
- Google Imagen API documentation: Generation times 15-45 seconds  
- Google Veo API documentation: Generation times 20-60 seconds
- Frontend timeout error logs and user feedback 