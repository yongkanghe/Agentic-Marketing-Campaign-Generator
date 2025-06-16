#!/usr/bin/env python3
"""
FILENAME: test_complete_stack.py
DESCRIPTION/PURPOSE: Comprehensive full-stack validation script for Video Venture Launch
Author: JP + 2025-06-16

This script provides complete validation of the Video Venture Launch application:
- Environment validation
- Database setup and testing
- Backend API testing
- Frontend accessibility testing
- Integration testing
- End-to-end workflow testing

Usage:
    python test_complete_stack.py [--setup] [--verbose]
    
    --setup: Automatically setup database and environment
    --verbose: Show detailed output
"""

import requests
import json
import time
import sqlite3
import os
import sys
import subprocess
import signal
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configuration
FRONTEND_URL = "http://localhost:8080"
BACKEND_URL = "http://localhost:8000"
BACKEND_DIR = Path("backend")
DATABASE_PATH = BACKEND_DIR / "database" / "data" / "database.db"

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class StackValidator:
    """Comprehensive stack validation and testing."""
    
    def __init__(self, verbose: bool = False, auto_setup: bool = False):
        self.verbose = verbose
        self.auto_setup = auto_setup
        self.test_results = {
            'environment': [],
            'database': [],
            'backend': [],
            'frontend': [],
            'integration': [],
            'e2e': []
        }
        self.start_time = time.time()
        self.backend_process = None
        self.frontend_process = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with color coding."""
        color = Colors.WHITE
        if level == "SUCCESS":
            color = Colors.GREEN
        elif level == "ERROR":
            color = Colors.RED
        elif level == "WARNING":
            color = Colors.YELLOW
        elif level == "INFO":
            color = Colors.BLUE
        
        print(f"{color}{message}{Colors.END}")
        
    def log_test(self, category: str, test_name: str, status: str, details: str = ""):
        """Log test result with formatting."""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results[category].append(result)
        
        if status == "PASS":
            emoji = "✅"
            color = Colors.GREEN
        elif status == "FAIL":
            emoji = "❌"
            color = Colors.RED
        else:
            emoji = "⚠️"
            color = Colors.YELLOW
        
        print(f"  {emoji} {color}{test_name}: {status}{Colors.END}")
        if details and status != "PASS" and self.verbose:
            print(f"     {Colors.YELLOW}Details: {details}{Colors.END}")
    
    def check_environment(self) -> bool:
        """Check environment prerequisites."""
        self.log(f"\n{Colors.PURPLE}🔍 Checking Environment Prerequisites...{Colors.END}")
        self.log("=" * 50)
        
        success_count = 0
        total_tests = 5
        
        # Check Python
        try:
            python_version = sys.version.split()[0]
            if python_version >= "3.9":
                self.log_test('environment', 'Python Version', 'PASS', f'Python {python_version}')
                success_count += 1
            else:
                self.log_test('environment', 'Python Version', 'FAIL', f'Python {python_version} < 3.9')
        except Exception as e:
            self.log_test('environment', 'Python Version', 'FAIL', str(e))
        
        # Check Node.js/Bun
        node_available = False
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                node_available = True
                self.log_test('environment', 'Node.js Available', 'PASS', result.stdout.strip())
                success_count += 1
        except:
            try:
                result = subprocess.run(['bun', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    node_available = True
                    self.log_test('environment', 'Bun Available', 'PASS', result.stdout.strip())
                    success_count += 1
            except:
                pass
        
        if not node_available:
            self.log_test('environment', 'JavaScript Runtime', 'FAIL', 'Neither Node.js nor Bun found')
        
        # Check backend directory
        if BACKEND_DIR.exists():
            self.log_test('environment', 'Backend Directory', 'PASS')
            success_count += 1
        else:
            self.log_test('environment', 'Backend Directory', 'FAIL', f'Not found: {BACKEND_DIR}')
        
        # Check requirements.txt
        requirements_path = BACKEND_DIR / "requirements.txt"
        if requirements_path.exists():
            self.log_test('environment', 'Requirements File', 'PASS')
            success_count += 1
        else:
            self.log_test('environment', 'Requirements File', 'FAIL', f'Not found: {requirements_path}')
        
        # Check package.json
        package_json = Path("package.json")
        if package_json.exists():
            self.log_test('environment', 'Package.json', 'PASS')
            success_count += 1
        else:
            self.log_test('environment', 'Package.json', 'FAIL', 'Not found: package.json')
        
        self.log(f"\n📊 Environment: {success_count}/{total_tests} checks passed")
        return success_count >= 3  # Minimum viable environment
    
    def setup_database(self) -> bool:
        """Setup the database."""
        self.log(f"\n{Colors.PURPLE}🗄️ Setting Up Database...{Colors.END}")
        self.log("=" * 50)
        
        try:
            # Ensure database directory exists
            db_dir = DATABASE_PATH.parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Run database setup
            result = subprocess.run([
                'python3', '-c',
                'import os; os.chdir("backend"); from database.database import init_database; init_database()'
            ], capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode == 0:
                self.log_test('database', 'Database Setup', 'PASS')
                return True
            else:
                self.log_test('database', 'Database Setup', 'FAIL', result.stderr)
                return False
                
        except Exception as e:
            self.log_test('database', 'Database Setup', 'FAIL', str(e))
            return False
    
    def test_database(self) -> bool:
        """Test database functionality."""
        self.log(f"\n{Colors.PURPLE}🗄️ Testing Database Layer...{Colors.END}")
        self.log("=" * 50)
        
        success_count = 0
        total_tests = 3
        
        # Test database file exists
        if DATABASE_PATH.exists():
            self.log_test('database', 'Database File Exists', 'PASS')
            success_count += 1
        else:
            self.log_test('database', 'Database File Exists', 'FAIL', f'Not found: {DATABASE_PATH}')
            if self.auto_setup:
                self.log("🔧 Auto-setup enabled, creating database...")
                if self.setup_database():
                    success_count += 1
        
        # Test database connectivity
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            if tables:
                self.log_test('database', 'Database Connectivity', 'PASS', f'{len(tables)} tables found')
                success_count += 1
            else:
                self.log_test('database', 'Database Connectivity', 'FAIL', 'No tables found')
        except Exception as e:
            self.log_test('database', 'Database Connectivity', 'FAIL', str(e))
        
        # Test basic operations
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Test insert/select/delete
            test_id = f"test_{int(time.time())}"
            cursor.execute("INSERT OR REPLACE INTO users (id, email, created_at, updated_at) VALUES (?, ?, datetime('now'), datetime('now'))", 
                         (test_id, f"{test_id}@test.com"))
            cursor.execute("SELECT id FROM users WHERE id = ?", (test_id,))
            result = cursor.fetchone()
            cursor.execute("DELETE FROM users WHERE id = ?", (test_id,))
            
            conn.commit()
            conn.close()
            
            if result:
                self.log_test('database', 'Basic CRUD Operations', 'PASS')
                success_count += 1
            else:
                self.log_test('database', 'Basic CRUD Operations', 'FAIL', 'CRUD test failed')
        except Exception as e:
            self.log_test('database', 'Basic CRUD Operations', 'FAIL', str(e))
        
        self.log(f"\n📊 Database: {success_count}/{total_tests} tests passed")
        return success_count >= 2
    
    def start_backend(self) -> bool:
        """Start the backend server."""
        try:
            self.log("🔧 Starting backend server...")
            
            # Start backend in background
            self.backend_process = subprocess.Popen([
                'python3', '-m', 'uvicorn', 'api.main:app', 
                '--host', '0.0.0.0', '--port', '8000'
            ], cwd=BACKEND_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for backend to start
            for i in range(10):
                try:
                    response = requests.get(f"{BACKEND_URL}/", timeout=2)
                    if response.status_code == 200:
                        self.log("✅ Backend server started successfully")
                        return True
                except:
                    time.sleep(1)
            
            self.log("❌ Backend server failed to start")
            return False
            
        except Exception as e:
            self.log(f"❌ Failed to start backend: {e}")
            return False
    
    def test_backend(self) -> bool:
        """Test backend API functionality."""
        self.log(f"\n{Colors.PURPLE}🔌 Testing Backend API Layer...{Colors.END}")
        self.log("=" * 50)
        
        success_count = 0
        total_tests = 4
        
        # Test server running
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                self.log_test('backend', 'Server Running', 'PASS')
                success_count += 1
            else:
                self.log_test('backend', 'Server Running', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('backend', 'Server Running', 'FAIL', str(e))
            if self.auto_setup and not self.backend_process:
                self.log("🔧 Auto-setup enabled, starting backend...")
                if self.start_backend():
                    success_count += 1
        
        # Test health endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log_test('backend', 'Health Endpoint', 'PASS')
                success_count += 1
            else:
                self.log_test('backend', 'Health Endpoint', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('backend', 'Health Endpoint', 'FAIL', str(e))
        
        # Test URL analysis
        try:
            response = requests.post(f"{BACKEND_URL}/api/v1/analysis/url", 
                                   json={"urls": ["https://example.com"], "analysis_depth": "standard"}, 
                                   timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "business_intelligence" in data:
                    self.log_test('backend', 'URL Analysis API', 'PASS')
                    success_count += 1
                else:
                    self.log_test('backend', 'URL Analysis API', 'FAIL', 'Missing response fields')
            else:
                self.log_test('backend', 'URL Analysis API', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('backend', 'URL Analysis API', 'FAIL', str(e))
        
        # Test campaign creation
        try:
            campaign_data = {
                "name": "Test Campaign",
                "objective": "Test API",
                "business_description": "Testing solution",
                "campaign_type": "product",
                "target_audience": "Developers",
                "creativity_level": 7
            }
            response = requests.post(f"{BACKEND_URL}/api/v1/campaigns/create", json=campaign_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.campaign_id = data["data"]["id"]
                    self.log_test('backend', 'Campaign Creation API', 'PASS')
                    success_count += 1
                else:
                    self.log_test('backend', 'Campaign Creation API', 'FAIL', 'Invalid response')
            else:
                self.log_test('backend', 'Campaign Creation API', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('backend', 'Campaign Creation API', 'FAIL', str(e))
        
        self.log(f"\n📊 Backend: {success_count}/{total_tests} tests passed")
        return success_count >= 3
    
    def test_integration(self) -> bool:
        """Test integration capabilities."""
        self.log(f"\n{Colors.PURPLE}🔗 Testing Integration Layer...{Colors.END}")
        self.log("=" * 50)
        
        success_count = 0
        total_tests = 2
        
        # Test API communication
        try:
            response = requests.post(f"{BACKEND_URL}/api/v1/analysis/url",
                                   json={"urls": ["https://example.com"], "analysis_depth": "standard"},
                                   headers={"Content-Type": "application/json"},
                                   timeout=15)
            if response.status_code == 200:
                self.log_test('integration', 'API Communication', 'PASS')
                success_count += 1
            else:
                self.log_test('integration', 'API Communication', 'FAIL', f'Status: {response.status_code}')
        except Exception as e:
            self.log_test('integration', 'API Communication', 'FAIL', str(e))
        
        # Test error handling
        try:
            response = requests.post(f"{BACKEND_URL}/api/v1/campaigns/create",
                                   json={"invalid": "data"},
                                   timeout=10)
            if response.status_code == 422:  # Validation error expected
                self.log_test('integration', 'Error Handling', 'PASS')
                success_count += 1
            else:
                self.log_test('integration', 'Error Handling', 'FAIL', f'Expected 422, got {response.status_code}')
        except Exception as e:
            self.log_test('integration', 'Error Handling', 'FAIL', str(e))
        
        self.log(f"\n📊 Integration: {success_count}/{total_tests} tests passed")
        return success_count >= 1
    
    def test_e2e_workflow(self) -> bool:
        """Test end-to-end workflow."""
        self.log(f"\n{Colors.PURPLE}🎯 Testing End-to-End Workflow...{Colors.END}")
        self.log("=" * 50)
        
        try:
            # Step 1: URL Analysis
            self.log("    🔍 Step 1: URL Analysis...")
            analysis_response = requests.post(f"{BACKEND_URL}/api/v1/analysis/url",
                                            json={"urls": ["https://example.com"], "analysis_depth": "standard"},
                                            timeout=15)
            if analysis_response.status_code != 200:
                raise Exception(f"URL analysis failed: {analysis_response.status_code}")
            
            # Step 2: Campaign Creation
            self.log("    📝 Step 2: Campaign Creation...")
            campaign_data = {
                "name": "E2E Test Campaign",
                "objective": "Test complete workflow",
                "business_description": "End-to-end testing solution",
                "campaign_type": "product",
                "target_audience": "QA Engineers",
                "creativity_level": 7
            }
            campaign_response = requests.post(f"{BACKEND_URL}/api/v1/campaigns/create", json=campaign_data, timeout=10)
            if campaign_response.status_code != 200:
                raise Exception(f"Campaign creation failed: {campaign_response.status_code}")
            
            campaign_id = campaign_response.json()["data"]["id"]
            
            # Step 3: Content Generation
            self.log("    🎨 Step 3: Content Generation...")
            content_data = {
                "campaign_id": campaign_id,
                "platforms": ["twitter", "linkedin"],
                "post_count": 2,
                "creativity_level": 6,
                "include_hashtags": True,
                "business_context": {
                    "industry": "Technology",
                    "target_audience": "QA Engineers",
                    "brand_voice": "Professional"
                },
                "campaign_objective": "Test complete workflow"
            }
            content_response = requests.post(f"{BACKEND_URL}/api/v1/content/generate", json=content_data, timeout=20)
            if content_response.status_code != 200:
                raise Exception(f"Content generation failed: {content_response.status_code}")
            
            self.log_test('e2e', 'Complete Workflow', 'PASS', 'All steps completed successfully')
            return True
            
        except Exception as e:
            self.log_test('e2e', 'Complete Workflow', 'FAIL', str(e))
            return False
    
    def cleanup(self):
        """Cleanup running processes."""
        if self.backend_process:
            self.log("🛑 Stopping backend server...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            self.log("🛑 Stopping frontend server...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_time = time.time() - self.start_time
        
        # Calculate statistics
        stats = {}
        total_tests = 0
        total_passed = 0
        
        for category, tests in self.test_results.items():
            passed = len([t for t in tests if t['status'] == 'PASS'])
            failed = len([t for t in tests if t['status'] == 'FAIL'])
            skipped = len([t for t in tests if t['status'] == 'SKIP'])
            
            stats[category] = {
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'total': len(tests),
                'success_rate': (passed / len(tests) * 100) if tests else 0
            }
            
            total_tests += len(tests)
            total_passed += passed
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'duration': f"{total_time:.2f}s",
            'overall_success_rate': f"{overall_success_rate:.1f}%",
            'total_tests': total_tests,
            'total_passed': total_passed,
            'statistics': stats,
            'detailed_results': self.test_results
        }
    
    def run_validation(self) -> bool:
        """Run complete stack validation."""
        self.log(f"{Colors.BOLD}{Colors.CYAN}🧪 Video Venture Launch - Complete Stack Validation{Colors.END}")
        self.log("=" * 60)
        self.log(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run validation steps
            env_ok = self.check_environment()
            db_ok = self.test_database()
            backend_ok = self.test_backend()
            integration_ok = self.test_integration()
            e2e_ok = self.test_e2e_workflow()
            
            # Generate report
            report = self.generate_report()
            
            # Display summary
            self.log(f"\n{Colors.BOLD}📊 VALIDATION SUMMARY{Colors.END}")
            self.log("=" * 60)
            self.log(f"⏱️  Duration: {report['duration']}")
            self.log(f"📈 Success Rate: {report['overall_success_rate']}")
            self.log(f"🧪 Tests: {report['total_passed']}/{report['total_tests']} passed")
            self.log("")
            
            for category, stats in report['statistics'].items():
                if stats['success_rate'] >= 80:
                    color = Colors.GREEN
                    emoji = "✅"
                elif stats['success_rate'] >= 50:
                    color = Colors.YELLOW
                    emoji = "⚠️"
                else:
                    color = Colors.RED
                    emoji = "❌"
                
                self.log(f"{emoji} {color}{category.title()}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1f}%){Colors.END}")
            
            self.log("")
            
            # Overall assessment
            critical_passed = env_ok and db_ok and backend_ok
            if critical_passed and integration_ok and e2e_ok:
                self.log(f"{Colors.GREEN}🎉 VALIDATION COMPLETE: ALL SYSTEMS OPERATIONAL{Colors.END}")
                self.log(f"{Colors.GREEN}✅ Application is ready for development and testing{Colors.END}")
                return True
            elif critical_passed:
                self.log(f"{Colors.YELLOW}⚠️  VALIDATION PARTIAL: CORE SYSTEMS OPERATIONAL{Colors.END}")
                self.log(f"{Colors.YELLOW}✅ Basic functionality working, some features need attention{Colors.END}")
                return True
            else:
                self.log(f"{Colors.RED}❌ VALIDATION FAILED: CRITICAL ISSUES DETECTED{Colors.END}")
                self.log(f"{Colors.RED}🔧 Application requires fixes before use{Colors.END}")
                return False
                
        except KeyboardInterrupt:
            self.log(f"\n{Colors.YELLOW}⚠️  Validation interrupted by user{Colors.END}")
            return False
        except Exception as e:
            self.log(f"\n{Colors.RED}❌ Validation failed with error: {e}{Colors.END}")
            return False
        finally:
            self.cleanup()

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Video Venture Launch - Complete Stack Validation")
    parser.add_argument('--setup', action='store_true', help='Automatically setup missing components')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    # Handle interrupt gracefully
    def signal_handler(sig, frame):
        print(f"\n{Colors.YELLOW}⚠️  Validation interrupted{Colors.END}")
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run validation
    validator = StackValidator(verbose=args.verbose, auto_setup=args.setup)
    success = validator.run_validation()
    
    # Save report
    report = validator.generate_report()
    with open('stack_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: stack_validation_report.json")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 