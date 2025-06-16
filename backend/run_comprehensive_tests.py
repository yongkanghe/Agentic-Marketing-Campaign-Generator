#!/usr/bin/env python3
"""
FILENAME: run_comprehensive_tests.py
DESCRIPTION/PURPOSE: Comprehensive test runner for database, API, and Gemini integration
Author: JP + 2025-06-15

This script runs comprehensive tests to verify:
1. SQLite database operations and data integrity
2. API endpoint functionality and validation
3. Real Gemini integration and agent workflows
4. End-to-end user journeys with database persistence
5. Performance benchmarks and regression testing
6. Data consistency across the entire stack
"""

import os
import sys
import time
import json
import subprocess
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configuration
TEST_DATABASE_PATH = "data/test_video_venture_launch.db"
MAIN_DATABASE_PATH = "data/video_venture_launch.db"
TEST_RESULTS_FILE = "backend/comprehensive_test_results.json"

class ComprehensiveTestRunner:
    """Comprehensive test runner for AI Marketing Campaign Post Generator."""
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        self.test_categories = {
            "database": [],
            "api": [],
            "gemini": [],
            "integration": [],
            "performance": [],
            "regression": []
        }
        
    def log_result(self, category: str, test_name: str, success: bool, 
                   message: str, duration: float = 0, details: Optional[Dict] = None):
        """Log test result with categorization."""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "category": category,
            "test": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.results.append(result)
        self.test_categories[category].append(result)
        
        print(f"{status} [{category.upper()}] {test_name}: {message} ({duration:.2f}s)")
    
    def setup_test_environment(self) -> bool:
        """Set up test environment and database."""
        print("\n🔧 Setting up test environment...")
        
        try:
            # Ensure test database directory exists
            os.makedirs("data", exist_ok=True)
            
            # Initialize test database
            if os.path.exists(TEST_DATABASE_PATH):
                os.remove(TEST_DATABASE_PATH)
            
            start = time.time()
            result = subprocess.run([
                "make", "db-init", f"DATABASE_PATH={TEST_DATABASE_PATH}"
            ], capture_output=True, text=True, timeout=30)
            duration = time.time() - start
            
            if result.returncode == 0:
                self.log_result("setup", "Test Database Initialization", True, 
                              "Test database created successfully", duration)
                return True
            else:
                self.log_result("setup", "Test Database Initialization", False, 
                              f"Failed: {result.stderr}", duration)
                return False
                
        except Exception as e:
            self.log_result("setup", "Test Environment Setup", False, f"Exception: {e}", 0)
            return False
    
    def test_database_operations(self) -> bool:
        """Test database operations and data integrity."""
        print("\n🗄️  Testing Database Operations...")
        
        all_passed = True
        
        # Test database schema integrity
        try:
            start = time.time()
            with sqlite3.connect(TEST_DATABASE_PATH) as conn:
                cursor = conn.cursor()
                
                # Test table existence
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = [
                    'campaign_templates', 'campaigns', 'generated_content',
                    'schema_version', 'uploaded_files', 'user_sessions', 'users'
                ]
                
                missing_tables = set(expected_tables) - set(tables)
                if missing_tables:
                    raise Exception(f"Missing tables: {missing_tables}")
                
                # Test views
                cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
                views = [row[0] for row in cursor.fetchall()]
                expected_views = ['campaign_summary', 'content_performance', 'user_activity_summary']
                
                missing_views = set(expected_views) - set(views)
                if missing_views:
                    raise Exception(f"Missing views: {missing_views}")
                
                # Test indexes
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
                indexes = cursor.fetchall()
                
                duration = time.time() - start
                self.log_result("database", "Schema Integrity", True, 
                              f"All tables, views, and {len(indexes)} indexes present", duration,
                              {"tables": len(tables), "views": len(views), "indexes": len(indexes)})
                
        except Exception as e:
            duration = time.time() - start
            self.log_result("database", "Schema Integrity", False, str(e), duration)
            all_passed = False
        
        # Test CRUD operations
        try:
            start = time.time()
            with sqlite3.connect(TEST_DATABASE_PATH) as conn:
                cursor = conn.cursor()
                
                # Test user creation
                user_data = {
                    'id': 'test-user-crud',
                    'email': 'crud@test.com',
                    'username': 'cruduser',
                    'full_name': 'CRUD Test User',
                    'is_active': True,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                cursor.execute("""
                    INSERT INTO users (id, email, username, full_name, is_active, created_at, updated_at)
                    VALUES (:id, :email, :username, :full_name, :is_active, :created_at, :updated_at)
                """, user_data)
                
                # Test campaign creation
                campaign_data = {
                    'id': 'test-campaign-crud',
                    'user_id': user_data['id'],
                    'name': 'CRUD Test Campaign',
                    'campaign_type': 'product',
                    'status': 'draft',
                    'creativity_level': 7,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                cursor.execute("""
                    INSERT INTO campaigns (
                        id, user_id, name, campaign_type, status, creativity_level,
                        created_at, updated_at
                    ) VALUES (
                        :id, :user_id, :name, :campaign_type, :status, :creativity_level,
                        :created_at, :updated_at
                    )
                """, campaign_data)
                
                # Test content creation
                cursor.execute("""
                    INSERT INTO generated_content (
                        id, campaign_id, content_type, platform, content_data,
                        user_rating, is_selected, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    'test-content-crud', campaign_data['id'], 'text_image', 'instagram',
                    '{"text": "CRUD test content"}', 8, True,
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
                
                conn.commit()
                
                # Verify data integrity
                cursor.execute("""
                    SELECT u.username, c.name, gc.content_type
                    FROM users u
                    JOIN campaigns c ON u.id = c.user_id
                    JOIN generated_content gc ON c.id = gc.campaign_id
                    WHERE u.id = ?
                """, (user_data['id'],))
                
                result = cursor.fetchone()
                if not result:
                    raise Exception("CRUD operations failed - no joined data found")
                
                duration = time.time() - start
                self.log_result("database", "CRUD Operations", True, 
                              "User, campaign, and content CRUD successful", duration)
                
        except Exception as e:
            duration = time.time() - start
            self.log_result("database", "CRUD Operations", False, str(e), duration)
            all_passed = False
        
        # Test constraints and data integrity
        try:
            start = time.time()
            with sqlite3.connect(TEST_DATABASE_PATH) as conn:
                cursor = conn.cursor()
                
                # Test unique constraint
                try:
                    cursor.execute("""
                        INSERT INTO users (id, email, username, full_name, is_active, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, ('test-user-2', 'crud@test.com', 'cruduser2', 'Test User 2', True,
                          datetime.now().isoformat(), datetime.now().isoformat()))
                    conn.commit()
                    raise Exception("Unique constraint not enforced")
                except sqlite3.IntegrityError:
                    # Expected behavior
                    pass
                
                # Test check constraint
                try:
                    cursor.execute("""
                        INSERT INTO campaigns (
                            id, user_id, name, campaign_type, status, creativity_level,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, ('test-campaign-invalid', 'test-user-crud', 'Invalid Campaign', 
                          'product', 'draft', 15,  # Invalid creativity level
                          datetime.now().isoformat(), datetime.now().isoformat()))
                    conn.commit()
                    raise Exception("Check constraint not enforced")
                except sqlite3.IntegrityError:
                    # Expected behavior
                    pass
                
                duration = time.time() - start
                self.log_result("database", "Constraints & Integrity", True, 
                              "All constraints properly enforced", duration)
                
        except Exception as e:
            duration = time.time() - start
            self.log_result("database", "Constraints & Integrity", False, str(e), duration)
            all_passed = False
        
        return all_passed
    
    def test_api_endpoints(self) -> bool:
        """Test API endpoints functionality."""
        print("\n🌐 Testing API Endpoints...")
        
        all_passed = True
        
        # Test basic API health
        try:
            start = time.time()
            result = subprocess.run([
                "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                "http://localhost:8000/"
            ], capture_output=True, text=True, timeout=10)
            duration = time.time() - start
            
            if result.stdout.strip() == "200":
                self.log_result("api", "Health Check", True, "API responding correctly", duration)
            else:
                self.log_result("api", "Health Check", False, f"HTTP {result.stdout.strip()}", duration)
                all_passed = False
                
        except Exception as e:
            self.log_result("api", "Health Check", False, f"Exception: {e}", 0)
            all_passed = False
        
        # Test pytest API tests
        try:
            start = time.time()
            result = subprocess.run([
                "python", "-m", "pytest", "backend/tests/test_api_*.py", "-v", "--tb=short"
            ], capture_output=True, text=True, timeout=120)
            duration = time.time() - start
            
            if result.returncode == 0:
                # Parse pytest output for test count
                output_lines = result.stdout.split('\n')
                test_summary = [line for line in output_lines if 'passed' in line and 'failed' in line]
                summary = test_summary[-1] if test_summary else "Tests completed"
                
                self.log_result("api", "Pytest API Tests", True, summary, duration)
            else:
                self.log_result("api", "Pytest API Tests", False, 
                              f"Tests failed: {result.stderr[:200]}", duration)
                all_passed = False
                
        except Exception as e:
            self.log_result("api", "Pytest API Tests", False, f"Exception: {e}", 0)
            all_passed = False
        
        return all_passed
    
    def test_gemini_integration(self) -> bool:
        """Test Gemini integration and agent functionality."""
        print("\n🤖 Testing Gemini Integration...")
        
        all_passed = True
        
        # Check Gemini configuration
        try:
            start = time.time()
            has_api_key = bool(os.getenv("GOOGLE_API_KEY"))
            has_vertex_config = bool(os.getenv("GOOGLE_CLOUD_PROJECT") and os.getenv("GOOGLE_CLOUD_LOCATION"))
            duration = time.time() - start
            
            if has_api_key or has_vertex_config:
                config_type = "API Key" if has_api_key else "Vertex AI"
                self.log_result("gemini", "Configuration Check", True, 
                              f"{config_type} configuration found", duration)
            else:
                self.log_result("gemini", "Configuration Check", False, 
                              "No Gemini configuration found", duration)
                all_passed = False
                
        except Exception as e:
            self.log_result("gemini", "Configuration Check", False, f"Exception: {e}", 0)
            all_passed = False
        
        # Test Gemini integration tests if configuration is available
        if os.getenv("GOOGLE_API_KEY") or (os.getenv("GOOGLE_CLOUD_PROJECT") and os.getenv("GOOGLE_CLOUD_LOCATION")):
            try:
                start = time.time()
                result = subprocess.run([
                    "python", "-m", "pytest", "backend/tests/test_gemini_*.py", 
                    "-v", "--tb=short", "-m", "integration"
                ], capture_output=True, text=True, timeout=180)
                duration = time.time() - start
                
                if result.returncode == 0:
                    output_lines = result.stdout.split('\n')
                    test_summary = [line for line in output_lines if 'passed' in line or 'skipped' in line]
                    summary = test_summary[-1] if test_summary else "Gemini tests completed"
                    
                    self.log_result("gemini", "Integration Tests", True, summary, duration)
                else:
                    self.log_result("gemini", "Integration Tests", False, 
                                  f"Tests failed: {result.stderr[:200]}", duration)
                    all_passed = False
                    
            except Exception as e:
                self.log_result("gemini", "Integration Tests", False, f"Exception: {e}", 0)
                all_passed = False
        else:
            self.log_result("gemini", "Integration Tests", True, 
                          "Skipped - no Gemini configuration", 0)
        
        return all_passed
    
    def test_database_integration(self) -> bool:
        """Test database integration tests."""
        print("\n🔗 Testing Database Integration...")
        
        try:
            start = time.time()
            result = subprocess.run([
                "python", "-m", "pytest", "backend/tests/test_database_integration.py", 
                "-v", "--tb=short"
            ], capture_output=True, text=True, timeout=120)
            duration = time.time() - start
            
            if result.returncode == 0:
                output_lines = result.stdout.split('\n')
                test_summary = [line for line in output_lines if 'passed' in line and 'failed' in line]
                summary = test_summary[-1] if test_summary else "Database integration tests completed"
                
                self.log_result("integration", "Database Integration", True, summary, duration)
                return True
            else:
                self.log_result("integration", "Database Integration", False, 
                              f"Tests failed: {result.stderr[:200]}", duration)
                return False
                
        except Exception as e:
            self.log_result("integration", "Database Integration", False, f"Exception: {e}", 0)
            return False
    
    def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks."""
        print("\n⏱️  Testing Performance Benchmarks...")
        
        try:
            start = time.time()
            result = subprocess.run([
                "python", "-m", "pytest", "backend/tests/", 
                "-v", "--tb=short", "-m", "performance"
            ], capture_output=True, text=True, timeout=300)
            duration = time.time() - start
            
            if result.returncode == 0:
                output_lines = result.stdout.split('\n')
                test_summary = [line for line in output_lines if 'passed' in line or 'skipped' in line]
                summary = test_summary[-1] if test_summary else "Performance tests completed"
                
                self.log_result("performance", "Performance Benchmarks", True, summary, duration)
                return True
            else:
                # Performance tests may fail due to timing - log but don't fail overall
                self.log_result("performance", "Performance Benchmarks", False, 
                              f"Some benchmarks failed: {result.stderr[:200]}", duration)
                return True  # Don't fail overall test suite for performance
                
        except Exception as e:
            self.log_result("performance", "Performance Benchmarks", False, f"Exception: {e}", 0)
            return True  # Don't fail overall test suite for performance
    
    def test_regression_suite(self) -> bool:
        """Test regression test suite."""
        print("\n🔄 Testing Regression Suite...")
        
        try:
            start = time.time()
            result = subprocess.run([
                "python", "-m", "pytest", "backend/tests/", 
                "-v", "--tb=short", "-m", "regression"
            ], capture_output=True, text=True, timeout=180)
            duration = time.time() - start
            
            if result.returncode == 0:
                output_lines = result.stdout.split('\n')
                test_summary = [line for line in output_lines if 'passed' in line and 'failed' in line]
                summary = test_summary[-1] if test_summary else "Regression tests completed"
                
                self.log_result("regression", "Regression Suite", True, summary, duration)
                return True
            else:
                self.log_result("regression", "Regression Suite", False, 
                              f"Tests failed: {result.stderr[:200]}", duration)
                return False
                
        except Exception as e:
            self.log_result("regression", "Regression Suite", False, f"Exception: {e}", 0)
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n📊 Generating Test Report...")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        # Category summary
        category_summary = {}
        for category, tests in self.test_categories.items():
            if tests:
                category_summary[category] = {
                    "total": len(tests),
                    "passed": sum(1 for t in tests if t['success']),
                    "failed": sum(1 for t in tests if not t['success']),
                    "duration": sum(t['duration'] for t in tests)
                }
        
        report = {
            "test_run": {
                "timestamp": self.start_time.isoformat(),
                "duration": total_duration,
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "categories": category_summary,
            "detailed_results": self.results
        }
        
        # Save report to file
        try:
            with open(TEST_RESULTS_FILE, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Test report saved to {TEST_RESULTS_FILE}")
        except Exception as e:
            print(f"❌ Failed to save test report: {e}")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"🎯 COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {passed_tests / total_tests * 100:.1f}%" if total_tests > 0 else "No tests run")
        print(f"Total Duration: {total_duration:.2f}s")
        
        print(f"\n📋 Category Breakdown:")
        for category, summary in category_summary.items():
            if summary['total'] > 0:
                success_rate = summary['passed'] / summary['total'] * 100
                print(f"  {category.upper()}: {summary['passed']}/{summary['total']} ({success_rate:.1f}%) - {summary['duration']:.2f}s")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  [{result['category'].upper()}] {result['test']}: {result['message']}")
        
        return passed_tests == total_tests
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        print("\n🧹 Cleaning up test environment...")
        
        try:
            if os.path.exists(TEST_DATABASE_PATH):
                os.remove(TEST_DATABASE_PATH)
                print("✅ Test database cleaned up")
        except Exception as e:
            print(f"⚠️  Failed to clean up test database: {e}")
    
    def run_all_tests(self) -> bool:
        """Run all comprehensive tests."""
        print("🚀 Starting Comprehensive Test Suite for AI Marketing Campaign Post Generator")
        print(f"⏰ Start time: {self.start_time}")
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Test environment setup failed. Aborting.")
            return False
        
        # Run test categories
        test_results = []
        
        test_results.append(self.test_database_operations())
        test_results.append(self.test_api_endpoints())
        test_results.append(self.test_gemini_integration())
        test_results.append(self.test_database_integration())
        test_results.append(self.test_performance_benchmarks())
        test_results.append(self.test_regression_suite())
        
        # Generate report
        overall_success = self.generate_test_report()
        
        # Cleanup
        self.cleanup_test_environment()
        
        return overall_success


def main():
    """Main entry point for comprehensive test runner."""
    runner = ComprehensiveTestRunner()
    
    try:
        success = runner.run_all_tests()
        exit_code = 0 if success else 1
        
        print(f"\n🏁 Test suite completed with exit code: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test suite interrupted by user")
        runner.cleanup_test_environment()
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test suite failed with exception: {e}")
        runner.cleanup_test_environment()
        sys.exit(1)


if __name__ == "__main__":
    main() 