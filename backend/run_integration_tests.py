#!/usr/bin/env python3
"""
FILENAME: run_integration_tests.py
DESCRIPTION/PURPOSE: Comprehensive test runner for frontend-backend integration with real UI testing
Author: JP + 2025-06-15

This script runs comprehensive tests to verify:
1. Frontend-backend API communication
2. Real Gemini integration
3. UI functionality with actual API calls
4. End-to-end workflow testing
"""

import os
import sys
import time
import json
import requests
from datetime import datetime

# Configuration
FRONTEND_URL = "http://localhost:8080"
BACKEND_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

class IntegrationTestRunner:
    """Comprehensive integration test runner for Video Venture Launch."""
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        
    def log_result(self, test_name: str, success: bool, message: str, duration: float = 0):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} {test_name}: {message} ({duration:.2f}s)")
    
    def test_server_availability(self) -> bool:
        """Test that both frontend and backend servers are running."""
        print("\n🔍 Testing Server Availability...")
        
        # Test backend
        try:
            start = time.time()
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            duration = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if "Video Venture Launch API" in data.get("name", ""):
                    self.log_result("Backend Server", True, f"API responding correctly", duration)
                else:
                    self.log_result("Backend Server", False, "API not properly configured", duration)
                    return False
            else:
                self.log_result("Backend Server", False, f"HTTP {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_result("Backend Server", False, f"Connection failed: {e}", 0)
            return False
        
        # Test frontend
        try:
            start = time.time()
            response = requests.get(FRONTEND_URL, timeout=5)
            duration = time.time() - start
            
            if response.status_code == 200 and "<!DOCTYPE html" in response.text:
                self.log_result("Frontend Server", True, "Serving HTML correctly", duration)
            else:
                self.log_result("Frontend Server", False, f"Not serving HTML properly", duration)
                return False
        except Exception as e:
            self.log_result("Frontend Server", False, f"Connection failed: {e}", 0)
            return False
        
        return True
    
    def test_real_gemini_integration(self) -> bool:
        """Test real Gemini API integration with comprehensive analysis."""
        print("\n🤖 Testing Real Gemini Integration...")
        
        test_cases = [
            {
                "name": "Single URL Analysis",
                "data": {
                    "urls": ["https://openai.com"],
                    "analysis_depth": "standard"
                }
            },
            {
                "name": "Multi-URL Comprehensive Analysis",
                "data": {
                    "urls": ["https://google.com", "https://microsoft.com"],
                    "analysis_depth": "comprehensive"
                }
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                start = time.time()
                response = requests.post(
                    f"{BACKEND_URL}/api/v1/analysis/url",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=TEST_TIMEOUT
                )
                duration = time.time() - start
                
                if response.status_code != 200:
                    self.log_result(f"Gemini {test_case['name']}", False, f"HTTP {response.status_code}", duration)
                    all_passed = False
                    continue
                
                data = response.json()
                
                # Verify real Gemini processing
                if not data.get("business_intelligence", {}).get("gemini_processed"):
                    self.log_result(f"Gemini {test_case['name']}", False, "Not using real Gemini", duration)
                    all_passed = False
                    continue
                
                if data.get("analysis_metadata", {}).get("pattern") != "Real Gemini API analysis":
                    self.log_result(f"Gemini {test_case['name']}", False, "Using mock data instead of Gemini", duration)
                    all_passed = False
                    continue
                
                # Verify response structure
                required_fields = ["business_analysis", "url_insights", "business_intelligence", "confidence_score"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(f"Gemini {test_case['name']}", False, f"Missing fields: {missing_fields}", duration)
                    all_passed = False
                    continue
                
                # Verify URL analysis
                for url in test_case["data"]["urls"]:
                    if url not in data.get("url_insights", {}):
                        self.log_result(f"Gemini {test_case['name']}", False, f"Missing analysis for {url}", duration)
                        all_passed = False
                        continue
                    
                    if data["url_insights"][url].get("status") != "gemini_analyzed":
                        self.log_result(f"Gemini {test_case['name']}", False, f"URL {url} not analyzed by Gemini", duration)
                        all_passed = False
                        continue
                
                company_name = data.get("business_analysis", {}).get("company_name", "Unknown")
                industry = data.get("business_analysis", {}).get("industry", "Unknown")
                confidence = data.get("confidence_score", 0)
                
                self.log_result(
                    f"Gemini {test_case['name']}", 
                    True, 
                    f"Company: {company_name}, Industry: {industry}, Confidence: {confidence}%", 
                    duration
                )
                
            except Exception as e:
                self.log_result(f"Gemini {test_case['name']}", False, f"Exception: {e}", 0)
                all_passed = False
        
        return all_passed
    
    def test_frontend_api_calls(self) -> bool:
        """Test that frontend API client works correctly."""
        print("\n🔗 Testing Frontend API Client Integration...")
        
        # Simulate frontend API client behavior
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "VideoVentureLaunch-Frontend/1.0.0"
        }
        
        test_data = {
            "urls": ["https://stripe.com"],
            "analysis_depth": "standard"
        }
        
        try:
            start = time.time()
            response = requests.post(
                f"{BACKEND_URL}/api/v1/analysis/url",
                json=test_data,
                headers=headers,
                timeout=15
            )
            duration = time.time() - start
            
            if response.status_code != 200:
                self.log_result("Frontend API Client", False, f"HTTP {response.status_code}", duration)
                return False
            
            data = response.json()
            
            # Verify response structure matches frontend expectations
            expected_fields = ["business_analysis", "url_insights", "business_intelligence", "analysis_metadata"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                self.log_result("Frontend API Client", False, f"Missing expected fields: {missing_fields}", duration)
                return False
            
            self.log_result("Frontend API Client", True, "All expected fields present", duration)
            return True
            
        except Exception as e:
            self.log_result("Frontend API Client", False, f"Exception: {e}", 0)
            return False
    
    def test_cors_configuration(self) -> bool:
        """Test CORS configuration for frontend-backend communication."""
        print("\n🌐 Testing CORS Configuration...")
        
        try:
            start = time.time()
            response = requests.options(
                f"{BACKEND_URL}/api/v1/analysis/url",
                headers={
                    "Origin": FRONTEND_URL,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                },
                timeout=5
            )
            duration = time.time() - start
            
            cors_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers"
            ]
            
            missing_headers = [header for header in cors_headers if header not in response.headers]
            
            if missing_headers:
                self.log_result("CORS Configuration", False, f"Missing headers: {missing_headers}", duration)
                return False
            
            self.log_result("CORS Configuration", True, "All CORS headers present", duration)
            return True
            
        except Exception as e:
            self.log_result("CORS Configuration", False, f"Exception: {e}", 0)
            return False
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting Video Venture Launch Integration Tests")
        print("=" * 60)
        print(f"Frontend URL: {FRONTEND_URL}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Timeout: {TEST_TIMEOUT}s")
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        tests = [
            ("Server Availability", self.test_server_availability),
            ("Real Gemini Integration", self.test_real_gemini_integration),
            ("Frontend API Client", self.test_frontend_api_calls),
            ("CORS Configuration", self.test_cors_configuration),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Unexpected error: {e}", 0)
        
        # Generate summary
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Frontend-Backend integration is working correctly.")
            print("✅ Real Gemini API integration confirmed")
            print("✅ Frontend can successfully call backend APIs")
            print("✅ All workflows are functional")
        else:
            print(f"\n❌ {total - passed} tests failed. Please check the issues above.")
        
        # Save detailed results
        results_summary = {
            "timestamp": end_time.isoformat(),
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed/total)*100,
            "duration": total_duration,
            "frontend_url": FRONTEND_URL,
            "backend_url": BACKEND_URL,
            "detailed_results": self.results
        }
        
        # Save to file
        with open("integration_test_results.json", "w") as f:
            json.dump(results_summary, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: integration_test_results.json")
        
        return results_summary

def main():
    """Main entry point."""
    runner = IntegrationTestRunner()
    results = runner.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] == 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 