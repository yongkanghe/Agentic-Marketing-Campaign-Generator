#!/usr/bin/env python3
"""
Quick Test Runner for AI Marketing Campaign Post Generator
Fast validation of core functionality with 10-second timeouts
"""

import requests
import json
import time
import unittest
import subprocess
from typing import Dict, Any

class QuickTestRunner(unittest.TestCase):
    """Quick test runner with fast timeouts and comprehensive validation"""
    
    def setUp(self):
        self.base_url = "http://localhost:8000"
        self.timeout = 10  # Fast timeout for quick tests
        self.start_time = time.time()
        
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            print("\n🏥 Testing Backend Health...")
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            print("   ✅ Backend health check passed")
            return True
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT: Backend health check took longer than {self.timeout}s")
            return False
        except requests.exceptions.ConnectionError:
            print("   🔌 CONNECTION ERROR: Could not connect to backend")
            return False
        except Exception as e:
            print(f"   ❌ ERROR: Backend health check failed: {str(e)}")
            return False
    
    def test_visual_content_generation(self):
        """Test visual content generation with image URL validation"""
        try:
            print("\n🎨 Testing Visual Content Generation...")
            
            # Test data for visual content generation
            visual_payload = {
                "social_posts": [
                    {
                        "id": "visual-test-1",
                        "type": "text_image",  # This should generate an image
                        "content": "Test post for visual content validation",
                        "platform": "instagram",
                        "hashtags": ["#test", "#validation"]
                    }
                ],
                "business_context": {
                    "business_name": "Visual Test Company",
                    "industry": "Technology",
                    "objective": "test visual content generation",
                    "target_audience": "developers"
                },
                "campaign_objective": "validate visual content URLs",
                "target_platforms": ["instagram"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/content/generate-visuals",
                json=visual_payload,
                timeout=120  # Longer timeout for image generation
            )
            
            # CRITICAL: Validate response structure
            self.assertEqual(response.status_code, 200, f"Visual content generation failed: {response.text}")
            data = response.json()
            
            # REGRESSION DETECTION: Validate response structure
            self.assertIn('posts_with_visuals', data, "Missing posts_with_visuals in response")
            posts_with_visuals = data['posts_with_visuals']
            self.assertIsInstance(posts_with_visuals, list, "posts_with_visuals should be a list")
            self.assertEqual(len(posts_with_visuals), 1, f"Expected 1 post, got {len(posts_with_visuals)}")
            
            # DETAILED IMAGE URL VALIDATION
            image_post = posts_with_visuals[0]
            self.assertIsInstance(image_post, dict, "Post should be a dictionary")
            self.assertIn('id', image_post, "Post missing ID")
            self.assertIn('type', image_post, "Post missing type")
            
            print(f"   📸 Validating image post: {image_post['id']}")
            
            # CRITICAL REGRESSION CHECK: Image URL must be present
            self.assertIn('image_url', image_post, "Image post missing image_url field")
            image_url = image_post['image_url']
            
            if image_url:
                print(f"   ✅ IMAGE URL PRESENT: {len(image_url)} characters")
                print(f"   ✅ STDOUT_IMAGE_VALIDATION: Post {image_post['id']} has image_url ({len(image_url)} chars)")
                self.assertIsInstance(image_url, str, "image_url should be a string")
                self.assertGreater(len(image_url), 100, "image_url seems too short (likely not base64)")
                
                # Validate base64 image format
                if image_url.startswith('data:image/'):
                    print(f"   ✅ VALID BASE64 IMAGE FORMAT")
                else:
                    print(f"   ⚠️ WARNING: image_url doesn't appear to be base64 format")
            else:
                print(f"   ❌ CRITICAL REGRESSION: IMAGE URL IS NULL/EMPTY!")
                self.fail(f"Image post {image_post['id']} has null/empty image_url - REGRESSION DETECTED!")
                
            print("   ✅ Visual content generation validation passed")
            return True
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT: Visual content generation took longer than 120s")
            return False
        except requests.exceptions.ConnectionError:
            print("   🔌 CONNECTION ERROR: Could not connect to visual content endpoint")
            return False
        except Exception as e:
            print(f"   ❌ ERROR: Visual content generation failed: {str(e)}")
            return False

    def test_content_generation(self):
        """Test basic content generation"""
        try:
            print("\n📝 Testing Content Generation...")
            
            payload = {
                "campaign_objective": "test campaign",
                "business_context": {
                    "business_name": "Test Company",
                    "industry": "Technology"
                },
                "target_platforms": ["linkedin"],
                "post_types": ["text_url"],
                "num_posts": 1
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/content/generate",
                json=payload,
                timeout=self.timeout
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('posts', data)
            print("   ✅ Content generation passed")
            return True
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT: Content generation took longer than {self.timeout}s")
            return False
        except requests.exceptions.ConnectionError:
            print("   🔌 CONNECTION ERROR: Could not connect to content generation endpoint")
            return False
        except Exception as e:
            print(f"   ❌ ERROR: Content generation failed: {str(e)}")
            return False

def run_quick_tests():
    """Run quick tests with proper error handling"""
    print("🚀 Starting Quick Test Suite...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(QuickTestRunner('test_backend_health'))
    suite.addTest(QuickTestRunner('test_content_generation'))
    suite.addTest(QuickTestRunner('test_visual_content_generation'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
    result = runner.run(suite)
    
    # Print summary
    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests
    
    print(f"\n📊 Test Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("   🎉 All tests passed!")
        return True
    else:
        print("   ⚠️ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_quick_tests()
    exit(0 if success else 1) 