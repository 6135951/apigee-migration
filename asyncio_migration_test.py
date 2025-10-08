#!/usr/bin/env python3
"""
Focused test for migration simulation functionality with asyncio error verification
"""

import requests
import sys
import json
import time
from datetime import datetime
from pathlib import Path

class AsyncioMigrationTester:
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

    def setup_migration_test_data(self):
        """Setup test data for migration testing"""
        print("\n🔧 Setting up migration test data...")
        
        # Create test credentials
        test_credential = {
            "name": "Asyncio Test Credentials",
            "edge_org": "test-asyncio-org",
            "edge_env": "prod",
            "edge_username": "asyncio-test@example.com",
            "edge_password": "test-password",
            "apigee_x_project": "test-asyncio-project",
            "apigee_x_env": "eval",
            "apigee_x_service_account": '{"type": "service_account", "project_id": "asyncio-test"}'
        }
        
        success, cred_response = self.run_test(
            "Setup: Save Test Credentials",
            "POST",
            "credentials",
            200,
            data=test_credential
        )
        
        if not success:
            return None, None
        
        credentials_id = cred_response.get('id')
        
        # Create sample proxy with complex policies that trigger asyncio calls
        sample_proxy_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy revision="1" name="asyncio-test-proxy">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <CreatedAt>1234567890000</CreatedAt>
    <CreatedBy>asyncio-test@example.com</CreatedBy>
    <Description>Complex proxy for asyncio migration testing</Description>
    <DisplayName>Asyncio Test Migration Proxy</DisplayName>
    <LastModifiedAt>1234567890000</LastModifiedAt>
    <LastModifiedBy>asyncio-test@example.com</LastModifiedBy>
    <Policies>
        <Policy>OAuth2</Policy>
        <Policy>SpikeArrest</Policy>
        <Policy>Quota</Policy>
        <Policy>JavaScript</Policy>
        <Policy>ServiceCallout</Policy>
        <Policy>XMLtoJSON</Policy>
        <Policy>JSONtoXML</Policy>
        <Policy>CustomPolicy</Policy>
    </Policies>
    <ProxyEndpoints>
        <ProxyEndpoint>default</ProxyEndpoint>
    </ProxyEndpoints>
    <Resources/>
    <TargetEndpoints>
        <TargetEndpoint>default</TargetEndpoint>
    </TargetEndpoints>
</APIProxy>'''
        
        # Write to temporary file
        test_proxy_path = Path("/tmp/asyncio-test-proxy.xml")
        with open(test_proxy_path, 'w') as f:
            f.write(sample_proxy_xml)
        
        # Upload proxy
        with open(test_proxy_path, 'rb') as f:
            files = {'file': ('asyncio-test-proxy.xml', f, 'text/xml')}
            success, upload_response = self.run_test(
                "Setup: Upload Asyncio Test Proxy",
                "POST",
                "upload-proxy",
                200,
                files=files
            )
        
        if not success:
            return None, None
        
        proxy_id = upload_response.get('proxy_id')
        
        # Analyze proxy
        success, analysis_response = self.run_test(
            "Setup: Analyze Asyncio Test Proxy",
            "POST",
            f"analyze-proxy/{proxy_id}",
            200
        )
        
        if success:
            analysis_id = analysis_response.get('id')
            print(f"   ✅ Asyncio test analysis created: {analysis_id}")
            # Wait for AI analysis to complete
            time.sleep(3)
            return analysis_id, credentials_id
        
        return None, None

    def test_migration_pipeline_asyncio(self, analysis_id, credentials_id):
        """Test the complete migration pipeline focusing on asyncio functionality"""
        print("\n🚀 Testing Migration Pipeline with Asyncio Focus")
        print("-" * 60)
        
        # Start migration
        migration_request = {
            "proxy_analysis_ids": [analysis_id],
            "credentials_id": credentials_id,
            "target_environment": "development",
            "auto_deploy": True
        }
        
        success, response = self.run_test(
            "Start Migration (Asyncio Test)",
            "POST",
            "migrate",
            200,
            data=migration_request
        )
        
        if not success:
            return False
        
        if not isinstance(response, list) or len(response) == 0:
            self.log_test("Migration Response Format", False, "Expected list with migration data")
            return False
        
        migration = response[0]
        migration_id = migration.get('id')
        
        if not migration_id:
            self.log_test("Migration ID Present", False, "No migration ID in response")
            return False
        
        self.log_test("Migration ID Present", True)
        
        # Test background task execution with asyncio
        print(f"\n🔄 Testing Background Task Execution (Migration ID: {migration_id})")
        
        # Poll migration status to verify background task is running
        asyncio_steps_detected = []
        error_detected = False
        
        for i in range(10):  # Poll for up to 25 seconds
            success, status_response = self.run_test(
                f"Background Task Status Check {i+1}",
                "GET",
                f"migration/{migration_id}",
                200
            )
            
            if success:
                current_status = status_response.get('status')
                current_progress = status_response.get('progress', 0)
                current_step = status_response.get('current_step', '')
                migration_log = status_response.get('migration_log', [])
                error_message = status_response.get('error_message')
                
                print(f"   Status: {current_status}, Progress: {current_progress}%, Step: {current_step}")
                
                # Check for asyncio-related errors
                if error_message and 'asyncio' in error_message.lower():
                    self.log_test("Asyncio Error Detection", False, f"Asyncio error found: {error_message}")
                    error_detected = True
                    break
                
                # Track steps that use asyncio
                asyncio_related_steps = [
                    "Validating source proxy",
                    "Converting policies to Apigee X format", 
                    "Generating Apigee X bundle with AI",
                    "Validating Apigee X bundle",
                    "Deploying to Apigee X"
                ]
                
                if current_step in asyncio_related_steps and current_step not in asyncio_steps_detected:
                    asyncio_steps_detected.append(current_step)
                    print(f"   ✅ Asyncio step detected: {current_step}")
                
                # Check migration log for asyncio errors
                for log_entry in migration_log:
                    if 'asyncio' in log_entry.lower() and 'not defined' in log_entry.lower():
                        self.log_test("Migration Log Asyncio Error", False, f"Asyncio error in log: {log_entry}")
                        error_detected = True
                        break
                
                # If migration completed or failed, break
                if current_status in ['completed', 'failed']:
                    if current_status == 'failed' and not error_detected:
                        # Check if failure was due to asyncio
                        if error_message and 'asyncio' in error_message.lower():
                            self.log_test("Migration Completion", False, f"Migration failed with asyncio error: {error_message}")
                            error_detected = True
                        else:
                            self.log_test("Migration Completion", False, f"Migration failed: {error_message}")
                    elif current_status == 'completed':
                        self.log_test("Migration Completion", True, "Migration completed successfully")
                    break
            
            time.sleep(2.5)
        
        # Verify no asyncio errors were detected
        if not error_detected:
            self.log_test("No Asyncio Errors Detected", True, "Migration completed without asyncio errors")
        
        # Verify asyncio steps were executed
        if len(asyncio_steps_detected) >= 3:
            self.log_test("Asyncio Steps Execution", True, f"Successfully executed {len(asyncio_steps_detected)} asyncio-dependent steps")
        else:
            self.log_test("Asyncio Steps Execution", False, f"Only {len(asyncio_steps_detected)} asyncio steps detected")
        
        return not error_detected

    def test_migration_status_updates(self, analysis_id, credentials_id):
        """Test migration status updates work correctly during simulation"""
        print("\n📊 Testing Migration Status Updates")
        print("-" * 40)
        
        # Start another migration for status testing
        migration_request = {
            "proxy_analysis_ids": [analysis_id],
            "credentials_id": credentials_id,
            "target_environment": "staging",
            "auto_deploy": False
        }
        
        success, response = self.run_test(
            "Start Status Test Migration",
            "POST",
            "migrate",
            200,
            data=migration_request
        )
        
        if not success:
            return False
        
        migration = response[0]
        migration_id = migration.get('id')
        
        # Track status updates
        status_updates = []
        progress_updates = []
        
        for i in range(8):
            success, status_response = self.run_test(
                f"Status Update Check {i+1}",
                "GET",
                f"migration/{migration_id}",
                200
            )
            
            if success:
                status = status_response.get('status')
                progress = status_response.get('progress', 0)
                
                if status not in [s['status'] for s in status_updates]:
                    status_updates.append({
                        'status': status,
                        'progress': progress,
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"   📈 Status update: {status} ({progress}%)")
                
                if progress not in progress_updates:
                    progress_updates.append(progress)
                
                if status in ['completed', 'failed']:
                    break
            
            time.sleep(2)
        
        # Validate status updates
        if len(status_updates) >= 3:
            self.log_test("Status Updates Frequency", True, f"Detected {len(status_updates)} status changes")
        else:
            self.log_test("Status Updates Frequency", False, f"Only {len(status_updates)} status changes detected")
        
        if len(progress_updates) >= 4:
            self.log_test("Progress Updates", True, f"Progress updated {len(progress_updates)} times")
        else:
            self.log_test("Progress Updates", False, f"Progress only updated {len(progress_updates)} times")
        
        return True

    def test_migration_log_entries(self, analysis_id, credentials_id):
        """Test that migration log entries are created properly"""
        print("\n📝 Testing Migration Log Entries")
        print("-" * 40)
        
        # Start migration for log testing
        migration_request = {
            "proxy_analysis_ids": [analysis_id],
            "credentials_id": credentials_id,
            "target_environment": "production",
            "auto_deploy": False
        }
        
        success, response = self.run_test(
            "Start Log Test Migration",
            "POST",
            "migrate",
            200,
            data=migration_request
        )
        
        if not success:
            return False
        
        migration = response[0]
        migration_id = migration.get('id')
        
        # Wait for migration to progress and collect logs
        time.sleep(8)
        
        success, final_status = self.run_test(
            "Get Final Migration Status",
            "GET",
            f"migration/{migration_id}",
            200
        )
        
        if success:
            migration_log = final_status.get('migration_log', [])
            steps_completed = final_status.get('steps_completed', [])
            
            # Validate log entries
            if len(migration_log) >= 5:
                self.log_test("Migration Log Entries", True, f"Generated {len(migration_log)} log entries")
            else:
                self.log_test("Migration Log Entries", False, f"Only {len(migration_log)} log entries found")
            
            # Check for specific log patterns
            expected_log_patterns = [
                "Starting:",
                "Completed:",
                "Migration completed successfully"
            ]
            
            patterns_found = 0
            for pattern in expected_log_patterns:
                if any(pattern in log_entry for log_entry in migration_log):
                    patterns_found += 1
            
            if patterns_found >= 2:
                self.log_test("Log Entry Patterns", True, f"Found {patterns_found}/{len(expected_log_patterns)} expected patterns")
            else:
                self.log_test("Log Entry Patterns", False, f"Only found {patterns_found}/{len(expected_log_patterns)} expected patterns")
            
            # Validate steps completed
            if len(steps_completed) >= 3:
                self.log_test("Steps Completed Tracking", True, f"Tracked {len(steps_completed)} completed steps")
            else:
                self.log_test("Steps Completed Tracking", False, f"Only tracked {len(steps_completed)} completed steps")
        
        return True

    def cleanup_test_data(self, credentials_id):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        if credentials_id:
            success, _ = self.run_test(
                "Cleanup: Delete Test Credentials",
                "DELETE",
                f"credentials/{credentials_id}",
                200
            )

    def run_asyncio_migration_tests(self):
        """Run focused asyncio migration tests"""
        print("🚀 Starting Asyncio Migration Functionality Tests")
        print(f"   Base URL: {self.base_url}")
        print("   Focus: Migration simulation pipeline with asyncio error verification")
        print("=" * 80)

        # Setup test data
        analysis_id, credentials_id = self.setup_migration_test_data()
        if not analysis_id or not credentials_id:
            print("❌ Test data setup failed - stopping tests")
            return self.generate_report()

        try:
            # Test 1: Migration Pipeline with Asyncio Focus
            self.test_migration_pipeline_asyncio(analysis_id, credentials_id)
            
            # Test 2: Migration Status Updates
            self.test_migration_status_updates(analysis_id, credentials_id)
            
            # Test 3: Migration Log Entries
            self.test_migration_log_entries(analysis_id, credentials_id)
            
        finally:
            # Cleanup
            self.cleanup_test_data(credentials_id)

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 80)
        print("📊 ASYNCIO MIGRATION TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Categorize results
        asyncio_tests = [r for r in self.test_results if 'asyncio' in r['test_name'].lower() or 'migration' in r['test_name'].lower()]
        setup_tests = [r for r in self.test_results if 'setup' in r['test_name'].lower() or 'cleanup' in r['test_name'].lower()]
        
        print(f"\n📋 Asyncio-specific tests: {sum(1 for r in asyncio_tests if r['success'])}/{len(asyncio_tests)} passed")
        print(f"📋 Setup/cleanup tests: {sum(1 for r in setup_tests if r['success'])}/{len(setup_tests)} passed")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL ASYNCIO MIGRATION TESTS PASSED!")
            print("✅ No 'asyncio not defined' errors detected")
            print("✅ Migration simulation pipeline working correctly")
            print("✅ Background task execution functioning properly")
            print("✅ Status updates working as expected")
            print("✅ Migration logs populated correctly")
            return 0
        else:
            print("\n❌ SOME ASYNCIO MIGRATION TESTS FAILED")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
            return 1

def main():
    tester = AsyncioMigrationTester()
    return tester.run_asyncio_migration_tests()

if __name__ == "__main__":
    sys.exit(main())