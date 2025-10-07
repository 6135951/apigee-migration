#!/usr/bin/env python3

import requests
import json
import sys
import time
from datetime import datetime

class EnhancedApigeeAPITester:
    def __init__(self, base_url="https://proxy-zip-support.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.proxy_id = None
        self.analysis_id = None
        self.credential_id = None
        self.migration_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n" + "="*50)
        print("TESTING BASIC API ENDPOINTS")
        print("="*50)
        
        # Test root endpoint
        self.run_test("API Root", "GET", "", 200)
        
        # Test dashboard stats
        self.run_test("Dashboard Stats", "GET", "dashboard-stats", 200)
        
        # Test get analyses (should work even if empty)
        self.run_test("Get All Analyses", "GET", "analyses", 200)

    def test_file_upload_and_analysis(self):
        """Test file upload and analysis functionality"""
        print("\n" + "="*50)
        print("TESTING FILE UPLOAD AND ANALYSIS")
        print("="*50)
        
        # Create a sample Apigee proxy XML for testing
        sample_proxy_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy revision="1" name="sample-proxy">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <CreatedAt>1640995200000</CreatedAt>
    <CreatedBy>developer@company.com</CreatedBy>
    <Description>Sample proxy for testing</Description>
    <DisplayName>Sample Proxy</DisplayName>
    <LastModifiedAt>1640995200000</LastModifiedAt>
    <LastModifiedBy>developer@company.com</LastModifiedBy>
    <Policies>
        <Policy>OAuth2-Verify-Token</Policy>
        <Policy>VerifyAPIKey-1</Policy>
        <Policy>SpikeArrest-1</Policy>
        <Policy>Quota-1</Policy>
        <Policy>JavaScript-ProcessRequest</Policy>
    </Policies>
    <ProxyEndpoints>
        <ProxyEndpoint>default</ProxyEndpoint>
    </ProxyEndpoints>
    <Resources>
        <Resource>jsc://process-request.js</Resource>
    </Resources>
    <TargetEndpoints>
        <TargetEndpoint>default</TargetEndpoint>
    </TargetEndpoints>
</APIProxy>'''

        # Test file upload using multipart form data
        try:
            files = {'file': ('sample-proxy.xml', sample_proxy_xml, 'application/xml')}
            response = requests.post(f"{self.api_url}/upload-proxy", files=files, timeout=30)
            
            if response.status_code == 200:
                self.tests_passed += 1
                print("✅ File Upload - Passed")
                result = response.json()
                self.proxy_id = result.get('proxy_id')
                print(f"   Proxy ID: {self.proxy_id}")
            else:
                print(f"❌ File Upload - Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ File Upload - Error: {str(e)}")
            return False
        
        self.tests_run += 1

        # Test proxy analysis
        if self.proxy_id:
            success, result = self.run_test(
                "Proxy Analysis", 
                "POST", 
                f"analyze-proxy/{self.proxy_id}", 
                200
            )
            if success and result:
                self.analysis_id = result.get('id')
                print(f"   Analysis ID: {self.analysis_id}")
                print(f"   Complexity Score: {result.get('complexity_score')}")
                print(f"   Policy Count: {result.get('policy_count')}")
                print(f"   Custom Policies: {result.get('custom_policies')}")
                
                # Verify policy mappings exist
                if result.get('policy_mappings'):
                    print(f"   Policy Mappings: {len(result.get('policy_mappings'))} found")
                    for mapping in result.get('policy_mappings', [])[:3]:  # Show first 3
                        print(f"     - {mapping.get('edge_policy')} → {mapping.get('apigee_x_equivalent')}")
                else:
                    print("   ⚠️  No policy mappings found")
                    
                return True
        
        return False

    def test_credentials_management(self):
        """Test credentials management APIs"""
        print("\n" + "="*50)
        print("TESTING CREDENTIALS MANAGEMENT")
        print("="*50)
        
        # Test save credentials
        test_credential = {
            "name": "Test Credentials",
            "edge_org": "test-edge-org",
            "edge_env": "test",
            "edge_username": "test@example.com",
            "edge_password": "test-password",
            "apigee_x_project": "test-apigee-project",
            "apigee_x_env": "eval",
            "apigee_x_service_account": '{"type": "service_account", "project_id": "test"}'
        }
        
        success, result = self.run_test(
            "Save Credentials",
            "POST",
            "credentials",
            200,
            data=test_credential
        )
        
        if success and result:
            self.credential_id = result.get('id')
            print(f"   Credential ID: {self.credential_id}")
        
        # Test get credentials
        success, result = self.run_test("Get Credentials", "GET", "credentials", 200)
        if success and result:
            print(f"   Found {len(result)} credentials")
            if result:
                cred = result[0]
                print(f"   First credential: {cred.get('name')} ({cred.get('edge_org')} → {cred.get('apigee_x_project')})")
        
        return success

    def test_migration_functionality(self):
        """Test migration execution and management"""
        print("\n" + "="*50)
        print("TESTING MIGRATION FUNCTIONALITY")
        print("="*50)
        
        if not self.analysis_id or not self.credential_id:
            print("❌ Cannot test migration - missing analysis_id or credential_id")
            return False
        
        # Test migration execution
        migration_request = {
            "proxy_analysis_ids": [self.analysis_id],
            "credentials_id": self.credential_id,
            "target_environment": "development",
            "auto_deploy": True
        }
        
        success, result = self.run_test(
            "Start Migration",
            "POST",
            "migrate",
            200,
            data=migration_request
        )
        
        if success and result:
            if isinstance(result, list) and len(result) > 0:
                self.migration_id = result[0].get('id')
                print(f"   Migration ID: {self.migration_id}")
                print(f"   Status: {result[0].get('status')}")
            
            # Wait a bit for migration to start
            time.sleep(2)
            
            # Test get migrations
            success, migrations = self.run_test("Get Migrations", "GET", "migrations", 200)
            if success and migrations:
                print(f"   Found {len(migrations)} migrations")
                if migrations:
                    migration = migrations[0]
                    print(f"   Latest migration: {migration.get('proxy_name')} - {migration.get('status')}")
                    print(f"   Progress: {migration.get('progress')}%")
            
            # Test get specific migration
            if self.migration_id:
                success, migration = self.run_test(
                    "Get Specific Migration",
                    "GET",
                    f"migration/{self.migration_id}",
                    200
                )
                if success and migration:
                    print(f"   Migration status: {migration.get('status')}")
                    print(f"   Current step: {migration.get('current_step')}")
                    print(f"   Progress: {migration.get('progress')}%")
        
        return success

    def test_enhanced_features(self):
        """Test enhanced enterprise features"""
        print("\n" + "="*50)
        print("TESTING ENHANCED ENTERPRISE FEATURES")
        print("="*50)
        
        # Test dashboard stats with migration data
        success, stats = self.run_test("Enhanced Dashboard Stats", "GET", "dashboard-stats", 200)
        if success and stats:
            print(f"   Total analyses: {stats.get('total_analyses')}")
            print(f"   Avg complexity: {stats.get('avg_complexity')}")
            print(f"   Complexity distribution: {stats.get('complexity_distribution')}")
            print(f"   Top policies: {len(stats.get('top_policies', []))}")
            print(f"   Recent analyses: {len(stats.get('recent_analyses', []))}")
        
        # Test get specific analysis (for policy details)
        if self.analysis_id:
            success, analysis = self.run_test(
                "Get Analysis Details",
                "GET",
                f"analysis/{self.analysis_id}",
                200
            )
            if success and analysis:
                print(f"   Analysis found: {analysis.get('proxy_name')}")
                print(f"   Policy mappings: {len(analysis.get('policy_mappings', []))}")
                
                # Check if policy mappings have required fields for enhanced features
                mappings = analysis.get('policy_mappings', [])
                if mappings:
                    mapping = mappings[0]
                    required_fields = ['edge_policy', 'apigee_x_equivalent', 'complexity', 'migration_notes']
                    has_all_fields = all(field in mapping for field in required_fields)
                    print(f"   Policy mapping completeness: {'✅' if has_all_fields else '❌'}")
                    if has_all_fields:
                        print(f"     Sample: {mapping['edge_policy']} → {mapping['apigee_x_equivalent']} ({mapping['complexity']})")
        
        return True

    def test_migration_controls(self):
        """Test enhanced migration controls"""
        print("\n" + "="*50)
        print("TESTING MIGRATION CONTROLS")
        print("="*50)
        
        if not self.migration_id:
            print("❌ Cannot test migration controls - no migration_id")
            return False
        
        # Wait a bit to ensure migration is in progress
        time.sleep(3)
        
        # Test migration cancellation
        success, result = self.run_test(
            "Cancel Migration",
            "DELETE",
            f"migration/{self.migration_id}",
            200
        )
        
        if success:
            print("   Migration cancellation successful")
            
            # Verify cancellation
            success, migration = self.run_test(
                "Verify Cancellation",
                "GET",
                f"migration/{self.migration_id}",
                200
            )
            if success and migration:
                status = migration.get('status')
                print(f"   Migration status after cancellation: {status}")
                if status == 'failed':
                    print("   ✅ Migration properly cancelled")
                else:
                    print(f"   ⚠️  Migration status is {status}, expected 'failed'")
        
        return success

    def cleanup(self):
        """Clean up test data"""
        print("\n" + "="*50)
        print("CLEANUP")
        print("="*50)
        
        # Delete test credentials
        if self.credential_id:
            success, _ = self.run_test(
                "Delete Test Credentials",
                "DELETE",
                f"credentials/{self.credential_id}",
                200
            )
            if success:
                print("   Test credentials deleted")

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Enhanced Apigee Migration Tool API Tests")
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        
        start_time = time.time()
        
        try:
            # Run test suites
            self.test_basic_endpoints()
            self.test_file_upload_and_analysis()
            self.test_credentials_management()
            self.test_migration_functionality()
            self.test_enhanced_features()
            self.test_migration_controls()
            
        except KeyboardInterrupt:
            print("\n⚠️  Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
        finally:
            self.cleanup()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print results
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"Duration: {duration:.1f} seconds")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed")
            return 1

def main():
    tester = EnhancedApigeeAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())