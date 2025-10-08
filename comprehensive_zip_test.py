import requests
import sys
import json
import time
import zipfile
import tempfile
import os
import random
from datetime import datetime
from pathlib import Path
from io import BytesIO

class ComprehensiveZipTester:
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

    def create_sample_xml_file(self):
        """Create a sample XML proxy file for testing"""
        xml_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy revision="1" name="sample-xml-proxy">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <CreatedAt>1234567890000</CreatedAt>
    <CreatedBy>test@example.com</CreatedBy>
    <Description>Sample XML proxy for testing</Description>
    <DisplayName>Sample XML Proxy</DisplayName>
    <LastModifiedAt>1234567890000</LastModifiedAt>
    <LastModifiedBy>test@example.com</LastModifiedBy>
    <Policies>
        <Policy>VerifyAPIKey</Policy>
        <Policy>Quota</Policy>
        <Policy>SpikeArrest</Policy>
    </Policies>
    <ProxyEndpoints>
        <ProxyEndpoint>default</ProxyEndpoint>
    </ProxyEndpoints>
    <Resources/>
    <TargetEndpoints>
        <TargetEndpoint>default</TargetEndpoint>
    </TargetEndpoints>
</APIProxy>'''
        return xml_content

    def create_sample_json_file(self):
        """Create a sample JSON proxy file for testing"""
        json_content = {
            "name": "sample-json-proxy",
            "displayName": "Sample JSON Proxy",
            "description": "Sample JSON proxy for testing",
            "policies": ["VerifyAPIKey", "Quota", "RaiseFault"],
            "proxyEndpoints": ["default"],
            "targetEndpoints": ["default"],
            "resources": []
        }
        return json.dumps(json_content, indent=2)

    def create_valid_zip_bundle(self):
        """Create a valid Apigee proxy ZIP bundle for testing"""
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Create main apiproxy.xml
            apiproxy_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy revision="1" name="comprehensive-test-proxy">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <CreatedAt>1234567890000</CreatedAt>
    <CreatedBy>test@example.com</CreatedBy>
    <Description>Comprehensive test ZIP proxy bundle</Description>
    <DisplayName>Comprehensive Test ZIP Proxy</DisplayName>
    <LastModifiedAt>1234567890000</LastModifiedAt>
    <LastModifiedBy>test@example.com</LastModifiedBy>
    <Policies>
        <Policy>VerifyAPIKey-1</Policy>
        <Policy>Quota-1</Policy>
        <Policy>JavaScript-1</Policy>
        <Policy>OAuth2-1</Policy>
        <Policy>SpikeArrest-1</Policy>
    </Policies>
    <ProxyEndpoints>
        <ProxyEndpoint>default</ProxyEndpoint>
    </ProxyEndpoints>
    <Resources>
        <Resource>jsc://test-script.js</Resource>
        <Resource>py://test-script.py</Resource>
    </Resources>
    <TargetEndpoints>
        <TargetEndpoint>default</TargetEndpoint>
    </TargetEndpoints>
</APIProxy>'''
            zip_file.writestr('apiproxy/apiproxy.xml', apiproxy_xml)
            
            # Create multiple policies
            policies = {
                'VerifyAPIKey-1': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<VerifyAPIKey async="false" continueOnError="false" enabled="true" name="VerifyAPIKey-1">
    <DisplayName>Verify API Key-1</DisplayName>
    <Properties/>
    <APIKey ref="request.queryparam.apikey"/>
</VerifyAPIKey>''',
                'Quota-1': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Quota async="false" continueOnError="false" enabled="true" name="Quota-1">
    <DisplayName>Quota-1</DisplayName>
    <Properties/>
    <Allow count="1000"/>
    <Interval>1</Interval>
    <TimeUnit>hour</TimeUnit>
    <Identifier ref="request.header.clientId"/>
</Quota>''',
                'JavaScript-1': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Javascript async="false" continueOnError="false" enabled="true" name="JavaScript-1">
    <DisplayName>JavaScript-1</DisplayName>
    <Properties/>
    <ResourceURL>jsc://test-script.js</ResourceURL>
</Javascript>''',
                'OAuth2-1': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<OAuthV2 async="false" continueOnError="false" enabled="true" name="OAuth2-1">
    <DisplayName>OAuth2-1</DisplayName>
    <Properties/>
    <Operation>VerifyAccessToken</Operation>
</OAuthV2>''',
                'SpikeArrest-1': '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<SpikeArrest async="false" continueOnError="false" enabled="true" name="SpikeArrest-1">
    <DisplayName>SpikeArrest-1</DisplayName>
    <Properties/>
    <Rate>100ps</Rate>
</SpikeArrest>'''
            }
            
            for policy_name, policy_content in policies.items():
                zip_file.writestr(f'apiproxy/policies/{policy_name}.xml', policy_content)
            
            # Create proxy endpoint
            proxy_endpoint = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ProxyEndpoint name="default">
    <Description/>
    <FaultRules/>
    <Flows>
        <Flow name="default">
            <Description/>
            <Request>
                <Step>
                    <FaultRules/>
                    <Name>VerifyAPIKey-1</Name>
                </Step>
                <Step>
                    <FaultRules/>
                    <Name>OAuth2-1</Name>
                </Step>
                <Step>
                    <FaultRules/>
                    <Name>SpikeArrest-1</Name>
                </Step>
                <Step>
                    <FaultRules/>
                    <Name>Quota-1</Name>
                </Step>
                <Step>
                    <FaultRules/>
                    <Name>JavaScript-1</Name>
                </Step>
            </Request>
            <Response/>
        </Flow>
    </Flows>
    <HTTPProxyConnection>
        <BasePath>/comprehensive-test-proxy</BasePath>
        <Properties/>
        <VirtualHost>default</VirtualHost>
    </HTTPProxyConnection>
    <RouteRule name="default">
        <TargetEndpoint>default</TargetEndpoint>
    </RouteRule>
</ProxyEndpoint>'''
            zip_file.writestr('apiproxy/proxies/default.xml', proxy_endpoint)
            
            # Create target endpoint
            target_endpoint = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<TargetEndpoint name="default">
    <Description/>
    <FaultRules/>
    <Flows/>
    <HTTPTargetConnection>
        <Properties/>
        <URL>https://httpbin.org</URL>
    </HTTPTargetConnection>
</TargetEndpoint>'''
            zip_file.writestr('apiproxy/targets/default.xml', target_endpoint)
            
            # Create JavaScript resource
            js_resource = '''// Comprehensive test JavaScript resource
var message = "Hello from comprehensive ZIP bundle test!";
var timestamp = new Date().toISOString();
context.setVariable("test.message", message);
context.setVariable("test.timestamp", timestamp);
print("JavaScript policy executed successfully at " + timestamp);

// Test some complex logic
var requestPath = context.getVariable("request.uri");
if (requestPath.indexOf("/test") !== -1) {
    context.setVariable("test.path.detected", true);
} else {
    context.setVariable("test.path.detected", false);
}'''
            zip_file.writestr('apiproxy/resources/jsc/test-script.js', js_resource)
            
            # Create Python resource
            py_resource = '''# Comprehensive test Python resource
import json
import datetime

def main():
    message = "Hello from comprehensive ZIP bundle Python test!"
    timestamp = datetime.datetime.now().isoformat()
    
    # Set flow variables
    flow.setVariable("test.python.message", message)
    flow.setVariable("test.python.timestamp", timestamp)
    
    print(f"Python policy executed successfully at {timestamp}")
    
    # Test some complex logic
    request_path = flow.getVariable("request.uri")
    if "/test" in request_path:
        flow.setVariable("test.python.path.detected", True)
    else:
        flow.setVariable("test.python.path.detected", False)

if __name__ == "__main__":
    main()'''
            zip_file.writestr('apiproxy/resources/py/test-script.py', py_resource)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def create_invalid_zip_bundle(self):
        """Create an invalid ZIP bundle (missing apiproxy.xml)"""
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Create only a policy file without main apiproxy.xml
            policy_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<VerifyAPIKey async="false" continueOnError="false" enabled="true" name="VerifyAPIKey-1">
    <DisplayName>Verify API Key-1</DisplayName>
    <Properties/>
    <APIKey ref="request.queryparam.apikey"/>
</VerifyAPIKey>'''
            zip_file.writestr('policies/VerifyAPIKey-1.xml', policy_xml)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def create_oversized_zip_bundle(self):
        """Create a ZIP bundle that exceeds 100MB"""
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_STORED) as zip_file:  # No compression
            # Add main apiproxy.xml
            apiproxy_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy revision="1" name="oversized-test-proxy">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <CreatedAt>1234567890000</CreatedAt>
    <CreatedBy>test@example.com</CreatedBy>
    <Description>Oversized test proxy bundle</Description>
    <DisplayName>Oversized Test Proxy</DisplayName>
    <LastModifiedAt>1234567890000</LastModifiedAt>
    <LastModifiedBy>test@example.com</LastModifiedBy>
    <Policies>
        <Policy>VerifyAPIKey-1</Policy>
    </Policies>
    <ProxyEndpoints>
        <ProxyEndpoint>default</ProxyEndpoint>
    </ProxyEndpoints>
    <Resources/>
    <TargetEndpoints>
        <TargetEndpoint>default</TargetEndpoint>
    </TargetEndpoints>
</APIProxy>'''
            zip_file.writestr('apiproxy/apiproxy.xml', apiproxy_xml)
            
            # Create random binary data that won't compress (101MB)
            chunk_size = 1024 * 1024  # 1MB chunks
            for i in range(101):
                random_data = bytes([random.randint(0, 255) for _ in range(chunk_size)])
                zip_file.writestr(f'large_data_{i}.bin', random_data)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def test_backward_compatibility_xml(self):
        """Test XML file upload backward compatibility"""
        xml_content = self.create_sample_xml_file()
        files = {'file': ('test-proxy.xml', xml_content.encode('utf-8'), 'text/xml')}
        
        try:
            response = requests.post(f"{self.api_url}/upload-proxy", files=files, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'proxy_id' in response_data:
                    self.log_test("XML Upload Backward Compatibility", True)
                    return True, response_data
                else:
                    self.log_test("XML Upload Backward Compatibility", False, "No proxy_id in response")
                    return False, {}
            else:
                error_msg = f"Status {response.status_code}: {response.text[:200]}"
                self.log_test("XML Upload Backward Compatibility", False, error_msg)
                return False, {}
                
        except Exception as e:
            self.log_test("XML Upload Backward Compatibility", False, f"Request error: {str(e)}")
            return False, {}

    def test_backward_compatibility_json(self):
        """Test JSON file upload backward compatibility"""
        json_content = self.create_sample_json_file()
        files = {'file': ('test-proxy.json', json_content.encode('utf-8'), 'application/json')}
        
        try:
            response = requests.post(f"{self.api_url}/upload-proxy", files=files, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'proxy_id' in response_data:
                    self.log_test("JSON Upload Backward Compatibility", True)
                    return True, response_data
                else:
                    self.log_test("JSON Upload Backward Compatibility", False, "No proxy_id in response")
                    return False, {}
            else:
                error_msg = f"Status {response.status_code}: {response.text[:200]}"
                self.log_test("JSON Upload Backward Compatibility", False, error_msg)
                return False, {}
                
        except Exception as e:
            self.log_test("JSON Upload Backward Compatibility", False, f"Request error: {str(e)}")
            return False, {}

    def test_valid_zip_upload(self):
        """Test successful ZIP file upload with valid Apigee proxy bundle"""
        zip_content = self.create_valid_zip_bundle()
        files = {'file': ('comprehensive-test-bundle.zip', zip_content, 'application/zip')}
        
        try:
            response = requests.post(f"{self.api_url}/upload-proxy", files=files, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'proxy_id' in response_data and 'ZIP proxy bundle uploaded' in response_data.get('message', ''):
                    self.log_test("Valid ZIP Upload", True)
                    return True, response_data
                else:
                    self.log_test("Valid ZIP Upload", False, "Invalid response format")
                    return False, {}
            else:
                error_msg = f"Status {response.status_code}: {response.text[:200]}"
                self.log_test("Valid ZIP Upload", False, error_msg)
                return False, {}
                
        except Exception as e:
            self.log_test("Valid ZIP Upload", False, f"Request error: {str(e)}")
            return False, {}

    def test_invalid_zip_upload(self):
        """Test ZIP file upload with invalid structure"""
        zip_content = self.create_invalid_zip_bundle()
        files = {'file': ('invalid-bundle.zip', zip_content, 'application/zip')}
        
        try:
            response = requests.post(f"{self.api_url}/upload-proxy", files=files, timeout=30)
            
            if response.status_code == 400:
                response_data = response.json()
                if 'apiproxy.xml' in response_data.get('detail', ''):
                    self.log_test("Invalid ZIP Structure Validation", True)
                    return True, response_data
                else:
                    self.log_test("Invalid ZIP Structure Validation", False, "Wrong error message")
                    return False, {}
            else:
                error_msg = f"Expected 400, got {response.status_code}: {response.text[:200]}"
                self.log_test("Invalid ZIP Structure Validation", False, error_msg)
                return False, {}
                
        except Exception as e:
            self.log_test("Invalid ZIP Structure Validation", False, f"Request error: {str(e)}")
            return False, {}

    def test_oversized_zip_upload(self):
        """Test ZIP file size validation (100MB limit)"""
        print("   Creating oversized ZIP file (this may take a moment)...")
        zip_content = self.create_oversized_zip_bundle()
        actual_size_mb = len(zip_content) / (1024 * 1024)
        print(f"   Created file size: {actual_size_mb:.2f}MB")
        
        files = {'file': ('oversized-bundle.zip', zip_content, 'application/zip')}
        
        try:
            response = requests.post(f"{self.api_url}/upload-proxy", files=files, timeout=120)
            
            if response.status_code == 413:
                response_data = response.json()
                if '100MB' in response_data.get('detail', ''):
                    self.log_test("ZIP File Size Limit Validation", True)
                    return True, response_data
                else:
                    self.log_test("ZIP File Size Limit Validation", False, "Wrong error message")
                    return False, {}
            else:
                error_msg = f"Expected 413, got {response.status_code}: {response.text[:200]}"
                self.log_test("ZIP File Size Limit Validation", False, error_msg)
                return False, {}
                
        except Exception as e:
            self.log_test("ZIP File Size Limit Validation", False, f"Request error: {str(e)}")
            return False, {}

    def test_unsupported_file_format(self):
        """Test upload with unsupported file format"""
        text_content = "This is not a valid proxy file"
        files = {'file': ('test.txt', text_content.encode('utf-8'), 'text/plain')}
        
        try:
            response = requests.post(f"{self.api_url}/upload-proxy", files=files, timeout=30)
            
            if response.status_code == 400:
                response_data = response.json()
                if 'Unsupported file format' in response_data.get('detail', ''):
                    self.log_test("Unsupported File Format Validation", True)
                    return True, response_data
                else:
                    self.log_test("Unsupported File Format Validation", False, "Wrong error message")
                    return False, {}
            else:
                error_msg = f"Expected 400, got {response.status_code}: {response.text[:200]}"
                self.log_test("Unsupported File Format Validation", False, error_msg)
                return False, {}
                
        except Exception as e:
            self.log_test("Unsupported File Format Validation", False, f"Request error: {str(e)}")
            return False, {}

    def test_zip_analysis(self, proxy_id):
        """Test analysis of uploaded ZIP bundle"""
        try:
            response = requests.post(f"{self.api_url}/analyze-proxy/{proxy_id}", timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Validate analysis response structure
                required_fields = ['id', 'proxy_name', 'complexity_score', 'policy_count', 'policy_mappings']
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if missing_fields:
                    self.log_test("ZIP Bundle Analysis", False, f"Missing fields: {missing_fields}")
                    return False, {}
                
                # Validate that policies were extracted correctly
                policy_count = response_data.get('policy_count', 0)
                policy_mappings = response_data.get('policy_mappings', [])
                
                if policy_count > 0 and len(policy_mappings) > 0:
                    self.log_test("ZIP Bundle Analysis", True)
                    return True, response_data
                else:
                    self.log_test("ZIP Bundle Analysis", False, "No policies extracted from ZIP bundle")
                    return False, {}
            else:
                error_msg = f"Status {response.status_code}: {response.text[:200]}"
                self.log_test("ZIP Bundle Analysis", False, error_msg)
                return False, {}
                
        except Exception as e:
            self.log_test("ZIP Bundle Analysis", False, f"Request error: {str(e)}")
            return False, {}

    def run_comprehensive_tests(self):
        """Run comprehensive ZIP upload functionality tests"""
        print("🚀 Starting Comprehensive ZIP Upload Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 70)

        # Test 1: Backward compatibility - XML upload
        print("\n📋 Testing Backward Compatibility...")
        success, xml_response = self.test_backward_compatibility_xml()
        
        # Test 2: Backward compatibility - JSON upload
        success, json_response = self.test_backward_compatibility_json()
        
        # Test 3: Valid ZIP upload
        print("\n📦 Testing ZIP Upload Functionality...")
        success, zip_response = self.test_valid_zip_upload()
        zip_proxy_id = zip_response.get('proxy_id') if success else None
        
        # Test 4: Invalid ZIP upload
        success, _ = self.test_invalid_zip_upload()
        
        # Test 5: File size validation
        print("\n📏 Testing File Size Validation...")
        success, _ = self.test_oversized_zip_upload()
        
        # Test 6: Unsupported file format
        success, _ = self.test_unsupported_file_format()
        
        # Test 7: ZIP bundle analysis
        if zip_proxy_id:
            print("\n🔍 Testing ZIP Bundle Analysis...")
            success, analysis_response = self.test_zip_analysis(zip_proxy_id)
            
            if success:
                print(f"   ✅ Analysis completed for ZIP bundle")
                print(f"   📊 Proxy Name: {analysis_response.get('proxy_name', 'Unknown')}")
                print(f"   📊 Policy Count: {analysis_response.get('policy_count', 0)}")
                print(f"   📊 Complexity Score: {analysis_response.get('complexity_score', 0):.1f}")
                print(f"   📊 Complexity Level: {analysis_response.get('complexity_level', 'Unknown')}")
                
                # Show policy mappings
                policy_mappings = analysis_response.get('policy_mappings', [])
                if policy_mappings:
                    print(f"   📊 Policy Mappings Found:")
                    for mapping in policy_mappings[:5]:  # Show first 5
                        edge_policy = mapping.get('edge_policy', 'Unknown')
                        apigee_x = mapping.get('apigee_x_equivalent', 'Unknown')
                        complexity = mapping.get('complexity', 'Unknown')
                        print(f"      - {edge_policy} → {apigee_x} ({complexity})")
        
        return self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE ZIP UPLOAD TEST RESULTS")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Categorize results
        passed_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        if passed_tests:
            print(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
            for result in passed_tests:
                print(f"   - {result['test_name']}")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"   - {result['test_name']}: {result['details']}")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL COMPREHENSIVE ZIP UPLOAD TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  {len(failed_tests)} TEST(S) FAILED")
            return False

def main():
    tester = ComprehensiveZipTester()
    success = tester.run_comprehensive_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())