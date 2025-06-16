"""
FILENAME: test_frontend_integration.py
DESCRIPTION/PURPOSE: Integration tests for frontend-backend API communication with real Gemini analysis
Author: JP + 2025-06-15
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any
from httpx import AsyncClient
import requests

# Test configuration
FRONTEND_URL = "http://localhost:8080"
BACKEND_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

class TestFrontendBackendIntegration:
    """Test suite for verifying frontend-backend API integration with real UI testing."""
    
    @pytest.fixture(scope="class")
    def event_loop(self):
        """Create an event loop for async tests."""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()
    
    def test_servers_are_running(self):
        """Verify both frontend and backend servers are accessible."""
        # Test frontend server
        try:
            frontend_response = requests.get(FRONTEND_URL, timeout=5)
            assert frontend_response.status_code == 200, f"Frontend server not responding: {frontend_response.status_code}"
            assert "<!DOCTYPE html" in frontend_response.text, "Frontend not serving HTML"
            print("✅ Frontend server is running and serving HTML")
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ Frontend server not accessible at {FRONTEND_URL}: {e}")
        
        # Test backend server
        try:
            backend_response = requests.get(f"{BACKEND_URL}/", timeout=5)
            assert backend_response.status_code == 200, f"Backend server not responding: {backend_response.status_code}"
            backend_data = backend_response.json()
            assert "AI Marketing Campaign Post Generator API" in backend_data.get("name", ""), "Backend API not properly configured"
            print("✅ Backend server is running and responding")
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ Backend server not accessible at {BACKEND_URL}: {e}")
    
    def test_cors_configuration(self):
        """Test that CORS is properly configured for frontend-backend communication."""
        try:
            # Test preflight request
            response = requests.options(
                f"{BACKEND_URL}/api/v1/analysis/url",
                headers={
                    "Origin": FRONTEND_URL,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                },
                timeout=5
            )
            
            # Check CORS headers
            assert "Access-Control-Allow-Origin" in response.headers, "CORS not configured"
            assert response.headers.get("Access-Control-Allow-Methods"), "CORS methods not configured"
            print("✅ CORS is properly configured")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ CORS test failed: {e}")
    
    def test_real_gemini_url_analysis_api(self):
        """Test the URL analysis API with real Gemini integration."""
        test_data = {
            "urls": ["https://openai.com", "https://google.com"],
            "analysis_depth": "comprehensive"
        }
        
        try:
            print("🔍 Testing real Gemini URL analysis...")
            start_time = time.time()
            
            response = requests.post(
                f"{BACKEND_URL}/api/v1/analysis/url",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=TEST_TIMEOUT
            )
            
            processing_time = time.time() - start_time
            
            # Verify response structure
            assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
            
            data = response.json()
            
            # Verify real Gemini processing
            assert "business_intelligence" in data, "Missing business_intelligence in response"
            assert data["business_intelligence"]["gemini_processed"] == True, "Gemini not actually processing"
            assert "Real Gemini analysis completed successfully" in data["business_intelligence"]["note"], "Not using real Gemini"
            
            # Verify analysis metadata
            assert data["analysis_metadata"]["pattern"] == "Real Gemini API analysis", "Not using real Gemini API"
            assert data["analysis_metadata"]["adk_agent_used"] == True, "ADK agent not used"
            
            # Verify business analysis structure
            assert "business_analysis" in data, "Missing business_analysis"
            assert "company_name" in data["business_analysis"], "Missing company_name"
            assert "industry" in data["business_analysis"], "Missing industry"
            
            # Verify URL insights
            assert "url_insights" in data, "Missing url_insights"
            for url in test_data["urls"]:
                assert url in data["url_insights"], f"Missing insights for {url}"
                assert data["url_insights"][url]["status"] == "gemini_analyzed", f"URL {url} not analyzed by Gemini"
            
            print(f"✅ Real Gemini URL analysis working (processed in {processing_time:.2f}s)")
            print(f"   Company: {data['business_analysis']['company_name']}")
            print(f"   Industry: {data['business_analysis']['industry']}")
            print(f"   Confidence: {data['confidence_score']}")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ URL analysis API test failed: {e}")
        except json.JSONDecodeError as e:
            pytest.fail(f"❌ Invalid JSON response from URL analysis API: {e}")
    
    def test_campaign_creation_api(self):
        """Test campaign creation API that frontend uses."""
        test_campaign = {
            "name": "Test Integration Campaign",
            "objective": "Test frontend-backend integration",
            "business_description": "AI-powered testing solution",
            "campaign_type": "social_media",
            "creativity_level": 7,
            "business_url": "https://example.com",
            "example_content": "Test content for integration"
        }
        
        try:
            print("📝 Testing campaign creation API...")
            
            response = requests.post(
                f"{BACKEND_URL}/api/v1/campaigns/create",
                json=test_campaign,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            assert response.status_code == 200, f"Campaign creation failed: {response.status_code} - {response.text}"
            
            data = response.json()
            assert "success" in data, "Missing success field"
            assert data["success"] == True, "Campaign creation not successful"
            assert "data" in data, "Missing campaign data"
            
            campaign_data = data["data"]
            assert campaign_data["name"] == test_campaign["name"], "Campaign name mismatch"
            assert campaign_data["objective"] == test_campaign["objective"], "Campaign objective mismatch"
            assert "id" in campaign_data, "Missing campaign ID"
            
            print(f"✅ Campaign creation API working")
            print(f"   Campaign ID: {campaign_data['id']}")
            print(f"   Name: {campaign_data['name']}")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ Campaign creation API test failed: {e}")
    
    def test_content_generation_api(self):
        """Test content generation API that frontend uses."""
        test_request = {
            "campaign_id": "test-campaign-123",
            "platforms": ["twitter", "linkedin", "instagram"],
            "post_count": 3,
            "creativity_level": 7,
            "include_hashtags": True,
            "business_context": "AI-powered marketing solutions"
        }
        
        try:
            print("🎨 Testing content generation API...")
            
            response = requests.post(
                f"{BACKEND_URL}/api/v1/content/generate",
                json=test_request,
                headers={"Content-Type": "application/json"},
                timeout=20
            )
            
            assert response.status_code == 200, f"Content generation failed: {response.status_code} - {response.text}"
            
            data = response.json()
            assert "success" in data, "Missing success field"
            assert data["success"] == True, "Content generation not successful"
            assert "data" in data, "Missing content data"
            
            content_data = data["data"]
            assert "posts" in content_data, "Missing posts in response"
            assert len(content_data["posts"]) > 0, "No posts generated"
            
            # Verify post structure
            first_post = content_data["posts"][0]
            assert "content" in first_post, "Missing content in post"
            assert "platform" in first_post, "Missing platform in post"
            assert "hashtags" in first_post, "Missing hashtags in post"
            
            print(f"✅ Content generation API working")
            print(f"   Generated {len(content_data['posts'])} posts")
            print(f"   First post: {first_post['content'][:50]}...")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ Content generation API test failed: {e}")
    
    def test_api_error_handling(self):
        """Test that API properly handles errors and returns appropriate responses."""
        # Test invalid URL analysis request
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/analysis/url",
                json={"invalid": "data"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            assert response.status_code in [400, 422], f"Expected validation error, got {response.status_code}"
            print("✅ API error handling working for invalid requests")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ API error handling test failed: {e}")
    
    def test_api_response_times(self):
        """Test that API responses are within acceptable time limits."""
        endpoints_to_test = [
            ("/", "GET", None, 2.0),  # Root endpoint should be fast
            ("/api/v1/analysis/url", "POST", {"urls": ["https://example.com"], "analysis_depth": "standard"}, 15.0),  # Analysis can be slower
        ]
        
        for endpoint, method, data, max_time in endpoints_to_test:
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=max_time)
                else:
                    response = requests.post(
                        f"{BACKEND_URL}{endpoint}",
                        json=data,
                        headers={"Content-Type": "application/json"},
                        timeout=max_time
                    )
                
                processing_time = time.time() - start_time
                
                assert response.status_code == 200, f"Endpoint {endpoint} failed: {response.status_code}"
                assert processing_time < max_time, f"Endpoint {endpoint} too slow: {processing_time:.2f}s > {max_time}s"
                
                print(f"✅ {method} {endpoint} responded in {processing_time:.2f}s")
                
            except requests.exceptions.RequestException as e:
                pytest.fail(f"❌ Performance test failed for {endpoint}: {e}")
    
    def test_frontend_api_client_integration(self):
        """Test that the frontend API client configuration works with the backend."""
        # This test simulates what the frontend API client does
        api_base_url = "http://localhost:8000"
        
        # Test with axios-like headers that frontend uses
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "VideoVentureLaunch-Frontend/1.0.0"
        }
        
        test_data = {
            "urls": ["https://microsoft.com"],
            "analysis_depth": "standard"
        }
        
        try:
            print("🔗 Testing frontend API client integration...")
            
            response = requests.post(
                f"{api_base_url}/api/v1/analysis/url",
                json=test_data,
                headers=headers,
                timeout=15
            )
            
            assert response.status_code == 200, f"Frontend API client simulation failed: {response.status_code}"
            
            data = response.json()
            
            # Verify the response structure matches what frontend expects
            expected_fields = ["business_analysis", "url_insights", "business_intelligence", "analysis_metadata"]
            for field in expected_fields:
                assert field in data, f"Missing expected field: {field}"
            
            print("✅ Frontend API client integration working")
            print(f"   Response contains all expected fields: {expected_fields}")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ Frontend API client integration test failed: {e}")

def run_integration_tests():
    """Run all integration tests and provide a summary."""
    print("🚀 Starting Frontend-Backend Integration Tests")
    print("=" * 60)
    
    # Run pytest with this file
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        __file__, 
        "-v", 
        "--tb=short",
        "--color=yes"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_integration_tests()
    if success:
        print("\n🎉 All integration tests passed!")
    else:
        print("\n❌ Some integration tests failed!")
        exit(1) 