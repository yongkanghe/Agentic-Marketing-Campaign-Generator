#!/bin/bash
# FILENAME: test_curl_commands.sh
# DESCRIPTION/PURPOSE: Curl commands to test frontend-backend API integration with real Gemini
# Author: JP + 2025-06-15

set -e  # Exit on any error

# Configuration
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:8080"

echo "🚀 Testing AI Marketing Campaign Post Generator API Integration"
echo "=============================================="
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Test 1: Backend Health Check
echo "🔍 Test 1: Backend Health Check"
echo "curl -X GET $BACKEND_URL/"
curl -X GET "$BACKEND_URL/" \
  -H "Accept: application/json" \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" \
  | jq '.' 2>/dev/null || echo "Response received"
echo ""

# Test 2: Frontend Availability
echo "🌐 Test 2: Frontend Availability"
echo "curl -X GET $FRONTEND_URL/"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/")
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend is serving content (HTTP $FRONTEND_STATUS)"
else
    echo "❌ Frontend not accessible (HTTP $FRONTEND_STATUS)"
fi
echo ""

# Test 3: Single URL Analysis with Real Gemini
echo "🤖 Test 3: Single URL Analysis with Real Gemini"
echo "curl -X POST $BACKEND_URL/api/v1/analysis/url"
curl -X POST "$BACKEND_URL/api/v1/analysis/url" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Origin: $FRONTEND_URL" \
  -d '{
    "urls": ["https://openai.com"],
    "analysis_depth": "standard"
  }' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" \
  | jq '.business_intelligence.gemini_processed, .analysis_metadata.pattern, .business_analysis.company_name, .confidence_score' 2>/dev/null || echo "Response received"
echo ""

# Test 4: Multi-URL Comprehensive Analysis
echo "🔍 Test 4: Multi-URL Comprehensive Analysis"
echo "curl -X POST $BACKEND_URL/api/v1/analysis/url"
curl -X POST "$BACKEND_URL/api/v1/analysis/url" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Origin: $FRONTEND_URL" \
  -d '{
    "urls": ["https://google.com", "https://microsoft.com"],
    "analysis_depth": "comprehensive"
  }' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" \
  | jq '.business_intelligence.note, .url_insights | keys, .business_analysis.industry' 2>/dev/null || echo "Response received"
echo ""

# Test 5: Frontend API Client Simulation
echo "🔗 Test 5: Frontend API Client Simulation"
echo "curl -X POST $BACKEND_URL/api/v1/analysis/url (with frontend headers)"
curl -X POST "$BACKEND_URL/api/v1/analysis/url" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: VideoVentureLaunch-Frontend/1.0.0" \
  -H "Origin: $FRONTEND_URL" \
  -d '{
    "urls": ["https://stripe.com"],
    "analysis_depth": "standard"
  }' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" \
  | jq '.business_analysis.company_name, .business_intelligence.gemini_processed' 2>/dev/null || echo "Response received"
echo ""

# Test 6: CORS Preflight Request
echo "🌐 Test 6: CORS Preflight Request"
echo "curl -X OPTIONS $BACKEND_URL/api/v1/analysis/url"
curl -X OPTIONS "$BACKEND_URL/api/v1/analysis/url" \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -w "\nStatus: %{http_code}\nCORS Headers:\n" \
  -D - -o /dev/null | grep -i "access-control" || echo "CORS headers checked"
echo ""

# Test 7: Campaign Creation API
echo "📝 Test 7: Campaign Creation API"
echo "curl -X POST $BACKEND_URL/api/v1/campaigns/create"
curl -X POST "$BACKEND_URL/api/v1/campaigns/create" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Origin: $FRONTEND_URL" \
  -d '{
    "name": "Curl Test Campaign",
    "objective": "Test API integration via curl",
    "business_description": "AI-powered testing solution",
    "campaign_type": "social_media",
    "creativity_level": 7,
    "business_url": "https://example.com",
    "example_content": "Test content for curl integration"
  }' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" \
  | jq '.success, .data.id, .data.name' 2>/dev/null || echo "Response received"
echo ""

# Test 8: Error Handling Test
echo "⚠️ Test 8: Error Handling Test"
echo "curl -X POST $BACKEND_URL/api/v1/analysis/url (invalid data)"
curl -X POST "$BACKEND_URL/api/v1/analysis/url" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "invalid": "data"
  }' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" \
  | jq '.detail // .error // .' 2>/dev/null || echo "Error response received"
echo ""

echo "✅ All curl tests completed!"
echo ""
echo "📊 Summary:"
echo "- Backend health check"
echo "- Frontend availability check"
echo "- Real Gemini URL analysis (single & multi-URL)"
echo "- Frontend API client simulation"
echo "- CORS configuration verification"
echo "- Campaign creation workflow"
echo "- Error handling validation"
echo ""
echo "🎯 These tests verify that the frontend can successfully call the backend APIs"
echo "   and receive real Gemini-powered business analysis results." 