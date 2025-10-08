import requests
import sys
import json
import time
from datetime import datetime
from pathlib import Path

class ApigeeBackendTester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                self.log_test(name, False, error_msg)
                return False, {}

        except requests.exceptions.Timeout:
            self.log_test(name, False, "Request timeout (30s)")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Request error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_upload_proxy(self):
        """Test proxy upload with sample XML file"""
        # Read sample proxy file
        sample_file_path = Path("/app/sample-proxy.xml")
        if not sample_file_path.exists():
            self.log_test("Upload Proxy", False, "Sample proxy file not found")
            return False, {}
        
        with open(sample_file_path, 'rb') as f:
            files = {'file': ('sample-proxy.xml', f, 'text/xml')}
            success, response = self.run_test(
                "Upload Proxy", 
                "POST", 
                "upload-proxy", 
                200, 
                files=files
            )
        
        return success, response

    def test_analyze_proxy(self, proxy_id):
        """Test proxy analysis"""
        print(f"   Analyzing proxy ID: {proxy_id}")
        success, response = self.run_test(
            "Analyze Proxy", 
            "POST", 
            f"analyze-proxy/{proxy_id}", 
            200
        )
        
        if success:
            # Wait a bit for AI analysis to complete
            print("   Waiting for AI analysis to complete...")
            time.sleep(3)
        
        return success, response

    def test_get_analyses(self):
        """Test getting all analyses"""
        return self.run_test("Get All Analyses", "GET", "analyses", 200)

    def test_get_analysis_by_id(self, analysis_id):
        """Test getting specific analysis"""
        return self.run_test(
            "Get Analysis by ID", 
            "GET", 
            f"analysis/{analysis_id}", 
            200
        )

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        return self.run_test("Dashboard Stats", "GET", "dashboard-stats", 200)

    def validate_analysis_response(self, analysis_data):
        """Validate analysis response structure"""
        required_fields = [
            'id', 'proxy_id', 'proxy_name', 'complexity_score', 
            'complexity_level', 'policy_count', 'migration_effort', 
            'ai_recommendations', 'status'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in analysis_data:
                missing_fields.append(field)
        
        if missing_fields:
            self.log_test("Analysis Response Validation", False, f"Missing fields: {missing_fields}")
            return False
        
        # Validate data types and ranges
        if not isinstance(analysis_data['complexity_score'], (int, float)) or not (0 <= analysis_data['complexity_score'] <= 100):
            self.log_test("Analysis Response Validation", False, "Invalid complexity_score")
            return False
        
        if analysis_data['complexity_level'] not in ['simple', 'moderate', 'complex']:
            self.log_test("Analysis Response Validation", False, "Invalid complexity_level")
            return False
        
        self.log_test("Analysis Response Validation", True)
        return True

    def run_full_test_suite(self):
        """Run complete test suite"""
        print("🚀 Starting Apigee Migration Tool Backend Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 60)

        # Test 1: Root endpoint
        success, _ = self.test_root_endpoint()
        if not success:
            print("❌ Root endpoint failed - stopping tests")
            return self.generate_report()

        # Test 2: Upload proxy
        success, upload_response = self.test_upload_proxy()
        if not success:
            print("❌ Proxy upload failed - stopping tests")
            return self.generate_report()
        
        proxy_id = upload_response.get('proxy_id')
        if not proxy_id:
            self.log_test("Proxy Upload Response", False, "No proxy_id in response")
            return self.generate_report()

        # Test 3: Analyze proxy
        success, analysis_response = self.test_analyze_proxy(proxy_id)
        if not success:
            print("❌ Proxy analysis failed")
            return self.generate_report()
        
        # Validate analysis response
        if success:
            self.validate_analysis_response(analysis_response)
        
        analysis_id = analysis_response.get('id')

        # Test 4: Get all analyses
        success, analyses_response = self.test_get_analyses()
        if success and isinstance(analyses_response, list) and len(analyses_response) > 0:
            self.log_test("Analyses List Validation", True)
        elif success:
            self.log_test("Analyses List Validation", False, "Empty or invalid analyses list")

        # Test 5: Get specific analysis
        if analysis_id:
            success, _ = self.test_get_analysis_by_id(analysis_id)

        # Test 6: Dashboard stats
        success, stats_response = self.test_dashboard_stats()
        if success:
            required_stats = ['total_analyses', 'avg_complexity', 'complexity_distribution']
            missing_stats = [stat for stat in required_stats if stat not in stats_response]
            if missing_stats:
                self.log_test("Dashboard Stats Validation", False, f"Missing stats: {missing_stats}")
            else:
                self.log_test("Dashboard Stats Validation", True)

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return 0
        else:
            print("❌ SOME TESTS FAILED")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
            return 1

def main():
    tester = ApigeeBackendTester()
    return tester.run_full_test_suite()

if __name__ == "__main__":
    sys.exit(main())