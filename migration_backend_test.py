import requests
import sys
import json
import time
from datetime import datetime
from pathlib import Path

class ApigeeMigrationTester:
    def __init__(self, base_url="https://proxy-zip-support.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.created_resources = {
            'credentials': [],
            'analyses': [],
            'migrations': []
        }

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
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

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

    def test_credentials_save(self):
        """Test saving Apigee credentials"""
        test_credential = {
            "name": "Test Migration Credentials",
            "edge_org": "test-edge-org",
            "edge_env": "prod",
            "edge_username": "test@example.com",
            "edge_password": "test-password",
            "apigee_x_project": "test-apigee-x-project",
            "apigee_x_env": "eval",
            "apigee_x_service_account": '{"type": "service_account", "project_id": "test-project"}'
        }
        
        success, response = self.run_test(
            "Save Credentials",
            "POST",
            "credentials",
            200,
            data=test_credential
        )
        
        if success and 'id' in response:
            self.created_resources['credentials'].append(response['id'])
            return success, response
        
        return success, response

    def test_credentials_list(self):
        """Test listing credentials"""
        success, response = self.run_test(
            "List Credentials",
            "GET",
            "credentials",
            200
        )
        
        if success:
            # Validate response structure
            if isinstance(response, list):
                self.log_test("Credentials List Structure", True)
                # Check if our test credential is in the list
                if len(response) > 0:
                    required_fields = ['id', 'name', 'edge_org', 'apigee_x_project']
                    first_cred = response[0]
                    missing_fields = [field for field in required_fields if field not in first_cred]
                    if missing_fields:
                        self.log_test("Credentials Fields Validation", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("Credentials Fields Validation", True)
                        # Check that sensitive data is not exposed
                        if 'edge_password' in first_cred or 'apigee_x_service_account' in first_cred:
                            self.log_test("Credentials Security Check", False, "Sensitive data exposed in list")
                        else:
                            self.log_test("Credentials Security Check", True)
            else:
                self.log_test("Credentials List Structure", False, "Response is not a list")
        
        return success, response

    def test_credentials_delete(self, cred_id):
        """Test deleting credentials"""
        success, response = self.run_test(
            "Delete Credentials",
            "DELETE",
            f"credentials/{cred_id}",
            200
        )
        
        if success:
            # Remove from our tracking
            if cred_id in self.created_resources['credentials']:
                self.created_resources['credentials'].remove(cred_id)
        
        return success, response

    def setup_test_data(self):
        """Setup test data for migration testing"""
        print("\n🔧 Setting up test data...")
        
        # First, we need to upload and analyze a proxy
        sample_file_path = Path("/app/sample-proxy.xml")
        if not sample_file_path.exists():
            # Create a sample proxy file
            sample_proxy_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy revision="1" name="test-migration-proxy">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <CreatedAt>1234567890000</CreatedAt>
    <CreatedBy>test@example.com</CreatedBy>
    <Description>Test proxy for migration</Description>
    <DisplayName>Test Migration Proxy</DisplayName>
    <LastModifiedAt>1234567890000</LastModifiedAt>
    <LastModifiedBy>test@example.com</LastModifiedBy>
    <Policies>
        <Policy>OAuth2</Policy>
        <Policy>SpikeArrest</Policy>
        <Policy>Quota</Policy>
    </Policies>
    <ProxyEndpoints>
        <ProxyEndpoint>default</ProxyEndpoint>
    </ProxyEndpoints>
    <Resources/>
    <TargetEndpoints>
        <TargetEndpoint>default</TargetEndpoint>
    </TargetEndpoints>
</APIProxy>'''
            with open(sample_file_path, 'w') as f:
                f.write(sample_proxy_xml)
        
        # Upload proxy
        with open(sample_file_path, 'rb') as f:
            files = {'file': ('test-migration-proxy.xml', f, 'text/xml')}
            success, upload_response = self.run_test(
                "Setup: Upload Test Proxy",
                "POST",
                "upload-proxy",
                200,
                files=files
            )
        
        if not success:
            return None, None
        
        proxy_id = upload_response.get('proxy_id')
        if not proxy_id:
            self.log_test("Setup: Proxy Upload", False, "No proxy_id in response")
            return None, None
        
        # Analyze proxy
        success, analysis_response = self.run_test(
            "Setup: Analyze Test Proxy",
            "POST",
            f"analyze-proxy/{proxy_id}",
            200
        )
        
        if success:
            analysis_id = analysis_response.get('id')
            self.created_resources['analyses'].append(analysis_id)
            print(f"   ✅ Test analysis created: {analysis_id}")
            # Wait for AI analysis to complete
            time.sleep(3)
            return analysis_id, analysis_response
        
        return None, None

    def test_migration_start(self, analysis_id, credentials_id):
        """Test starting migration"""
        migration_request = {
            "proxy_analysis_ids": [analysis_id],
            "credentials_id": credentials_id,
            "target_environment": "development",
            "auto_deploy": True
        }
        
        success, response = self.run_test(
            "Start Migration",
            "POST",
            "migrate",
            200,
            data=migration_request
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            migration = response[0]
            if 'id' in migration:
                self.created_resources['migrations'].append(migration['id'])
                self.log_test("Migration Response Structure", True)
                
                # Validate migration structure
                required_fields = ['id', 'proxy_analysis_id', 'proxy_name', 'credentials_id', 'status', 'progress']
                missing_fields = [field for field in required_fields if field not in migration]
                if missing_fields:
                    self.log_test("Migration Fields Validation", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_test("Migration Fields Validation", True)
                
                return success, migration
            else:
                self.log_test("Migration Response Structure", False, "No migration ID in response")
        
        return success, response

    def test_migrations_list(self):
        """Test listing all migrations"""
        success, response = self.run_test(
            "List Migrations",
            "GET",
            "migrations",
            200
        )
        
        if success:
            if isinstance(response, list):
                self.log_test("Migrations List Structure", True)
                if len(response) > 0:
                    # Validate migration structure
                    migration = response[0]
                    required_fields = ['id', 'proxy_name', 'status', 'progress', 'current_step']
                    missing_fields = [field for field in required_fields if field not in migration]
                    if missing_fields:
                        self.log_test("Migration List Fields", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("Migration List Fields", True)
            else:
                self.log_test("Migrations List Structure", False, "Response is not a list")
        
        return success, response

    def test_migration_status(self, migration_id):
        """Test getting specific migration status"""
        success, response = self.run_test(
            "Get Migration Status",
            "GET",
            f"migration/{migration_id}",
            200
        )
        
        if success:
            # Validate migration status response
            required_fields = ['id', 'status', 'progress', 'current_step', 'migration_log']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                self.log_test("Migration Status Fields", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Migration Status Fields", True)
                
                # Check status values
                valid_statuses = ['pending', 'preparing', 'converting', 'validating', 'deploying', 'completed', 'failed']
                if response['status'] in valid_statuses:
                    self.log_test("Migration Status Values", True)
                else:
                    self.log_test("Migration Status Values", False, f"Invalid status: {response['status']}")
                
                # Check progress range
                if 0 <= response['progress'] <= 100:
                    self.log_test("Migration Progress Range", True)
                else:
                    self.log_test("Migration Progress Range", False, f"Invalid progress: {response['progress']}")
        
        return success, response

    def test_migration_real_time_updates(self, migration_id):
        """Test real-time migration status updates"""
        print(f"\n🔄 Testing real-time migration updates for {migration_id}...")
        
        # Poll migration status multiple times to check for updates
        previous_status = None
        previous_progress = None
        updates_detected = False
        
        for i in range(6):  # Poll 6 times over 15 seconds
            success, response = self.run_test(
                f"Real-time Update Check {i+1}",
                "GET",
                f"migration/{migration_id}",
                200
            )
            
            if success:
                current_status = response.get('status')
                current_progress = response.get('progress')
                current_step = response.get('current_step', '')
                
                print(f"   Status: {current_status}, Progress: {current_progress}%, Step: {current_step}")
                
                if previous_status and (current_status != previous_status or current_progress != previous_progress):
                    updates_detected = True
                    print(f"   📈 Update detected: {previous_status}({previous_progress}%) → {current_status}({current_progress}%)")
                
                previous_status = current_status
                previous_progress = current_progress
                
                # If migration is completed or failed, break
                if current_status in ['completed', 'failed']:
                    break
            
            time.sleep(2.5)  # Wait 2.5 seconds between polls
        
        if updates_detected:
            self.log_test("Real-time Migration Updates", True)
        else:
            self.log_test("Real-time Migration Updates", False, "No status updates detected during polling")
        
        return updates_detected

    def test_migration_cancel(self, migration_id):
        """Test cancelling a migration"""
        # First check if migration is still cancellable
        success, status_response = self.run_test(
            "Pre-cancel Status Check",
            "GET",
            f"migration/{migration_id}",
            200
        )
        
        if success:
            current_status = status_response.get('status')
            cancellable_statuses = ['pending', 'preparing', 'converting', 'validating']
            
            if current_status in cancellable_statuses:
                success, response = self.run_test(
                    "Cancel Migration",
                    "DELETE",
                    f"migration/{migration_id}",
                    200
                )
                
                if success:
                    # Verify cancellation worked
                    time.sleep(1)
                    success, verify_response = self.run_test(
                        "Verify Migration Cancelled",
                        "GET",
                        f"migration/{migration_id}",
                        200
                    )
                    
                    if success and verify_response.get('status') == 'failed':
                        self.log_test("Migration Cancellation Verification", True)
                    else:
                        self.log_test("Migration Cancellation Verification", False, "Migration not properly cancelled")
                
                return success, response
            else:
                self.log_test("Migration Cancel", False, f"Migration not cancellable (status: {current_status})")
                return False, {"error": "Migration not cancellable"}
        
        return False, {"error": "Could not check migration status"}

    def run_migration_test_suite(self):
        """Run complete migration test suite"""
        print("🚀 Starting Apigee Migration Tool - Migration Backend Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 70)

        # Test 1: Credentials Management
        print("\n📋 TESTING CREDENTIALS MANAGEMENT")
        print("-" * 40)
        
        # Save credentials
        success, cred_response = self.test_credentials_save()
        if not success:
            print("❌ Credentials save failed - stopping tests")
            return self.generate_report()
        
        credentials_id = cred_response.get('id')
        
        # List credentials
        self.test_credentials_list()
        
        # Test 2: Setup test data
        print("\n🔧 SETTING UP TEST DATA")
        print("-" * 40)
        
        analysis_id, analysis_data = self.setup_test_data()
        if not analysis_id:
            print("❌ Test data setup failed - stopping tests")
            return self.generate_report()
        
        # Test 3: Migration Execution
        print("\n🚀 TESTING MIGRATION EXECUTION")
        print("-" * 40)
        
        # Start migration
        success, migration_response = self.test_migration_start(analysis_id, credentials_id)
        if not success:
            print("❌ Migration start failed - stopping tests")
            return self.generate_report()
        
        migration_id = migration_response.get('id')
        
        # Test 4: Migration Status Tracking
        print("\n📊 TESTING MIGRATION STATUS TRACKING")
        print("-" * 40)
        
        # List migrations
        self.test_migrations_list()
        
        # Get specific migration status
        self.test_migration_status(migration_id)
        
        # Test real-time updates
        self.test_migration_real_time_updates(migration_id)
        
        # Test 5: Migration Cancellation (if still possible)
        print("\n🛑 TESTING MIGRATION CANCELLATION")
        print("-" * 40)
        
        # We'll start another migration to test cancellation
        success, cancel_migration_response = self.test_migration_start(analysis_id, credentials_id)
        if success:
            cancel_migration_id = cancel_migration_response.get('id')
            time.sleep(1)  # Give it a moment to start
            self.test_migration_cancel(cancel_migration_id)
        
        # Test 6: Cleanup
        print("\n🧹 CLEANUP")
        print("-" * 40)
        
        # Delete test credentials
        if credentials_id:
            self.test_credentials_delete(credentials_id)
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 70)
        print("📊 MIGRATION BACKEND TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Categorize results
        categories = {
            'Credentials': [],
            'Migration Execution': [],
            'Status Tracking': [],
            'Real-time Updates': [],
            'Cancellation': [],
            'Setup/Cleanup': []
        }
        
        for result in self.test_results:
            test_name = result['test_name']
            if 'Credential' in test_name:
                categories['Credentials'].append(result)
            elif 'Migration' in test_name and ('Start' in test_name or 'Fields' in test_name):
                categories['Migration Execution'].append(result)
            elif 'Status' in test_name or 'List' in test_name:
                categories['Status Tracking'].append(result)
            elif 'Real-time' in test_name or 'Update' in test_name:
                categories['Real-time Updates'].append(result)
            elif 'Cancel' in test_name:
                categories['Cancellation'].append(result)
            else:
                categories['Setup/Cleanup'].append(result)
        
        print("\n📋 Results by Category:")
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r['success'])
                total = len(results)
                print(f"  {category}: {passed}/{total} passed")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL MIGRATION TESTS PASSED!")
            return 0
        else:
            print("\n❌ SOME MIGRATION TESTS FAILED")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
            return 1

def main():
    tester = ApigeeMigrationTester()
    return tester.run_migration_test_suite()

if __name__ == "__main__":
    sys.exit(main())