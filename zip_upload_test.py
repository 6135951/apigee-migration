import requests
import sys
import json
import time
import zipfile
import tempfile
import os
from datetime import datetime
from pathlib import Path
from io import BytesIO

class ZipUploadTester:
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
<APIProxy revision="1" name="sample-proxy">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <CreatedAt>1234567890000</CreatedAt>
    <CreatedBy>test@example.com</CreatedBy>
    <Description>Sample proxy for testing</Description>
    <DisplayName>Sample Proxy</DisplayName>
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
<APIProxy revision="1" name="test-zip-proxy">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <CreatedAt>1234567890000</CreatedAt>
    <CreatedBy>test@example.com</CreatedBy>
    <Description>Test ZIP proxy bundle</Description>
    <DisplayName>Test ZIP Proxy</DisplayName>
    <LastModifiedAt>1234567890000</LastModifiedAt>
    <LastModifiedBy>test@example.com</LastModifiedBy>
    <Policies>
        <Policy>VerifyAPIKey-1</Policy>
        <Policy>Quota-1</Policy>
        <Policy>JavaScript-1</Policy>
    </Policies>
    <ProxyEndpoints>
        <ProxyEndpoint>default</ProxyEndpoint>
    </ProxyEndpoints>
    <Resources>
        <Resource>jsc://test-script.js</Resource>
    </Resources>
    <TargetEndpoints>
        <TargetEndpoint>default</TargetEndpoint>
    </TargetEndpoints>
</APIProxy>'''
            zip_file.writestr('apiproxy/apiproxy.xml', apiproxy_xml)
            
            # Create policies
            verify_api_key_policy = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<VerifyAPIKey async="false" continueOnError="false" enabled="true" name="VerifyAPIKey-1">
    <DisplayName>Verify API Key-1</DisplayName>
    <Properties/>
    <APIKey ref="request.queryparam.apikey"/>
</VerifyAPIKey>'''
            zip_file.writestr('apiproxy/policies/VerifyAPIKey-1.xml', verify_api_key_policy)
            
            quota_policy = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Quota async="false" continueOnError="false" enabled="true" name="Quota-1">
    <DisplayName>Quota-1</DisplayName>
    <Properties/>
    <Allow count="1000"/>
    <Interval>1</Interval>
    <TimeUnit>hour</TimeUnit>
    <Identifier ref="request.header.clientId"/>
</Quota>'''
            zip_file.writestr('apiproxy/policies/Quota-1.xml', quota_policy)
            
            javascript_policy = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Javascript async="false" continueOnError="false" enabled="true" name="JavaScript-1">
    <DisplayName>JavaScript-1</DisplayName>
    <Properties/>
    <ResourceURL>jsc://test-script.js</ResourceURL>
</Javascript>'''
            zip_file.writestr('apiproxy/policies/JavaScript-1.xml', javascript_policy)
            
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
        <BasePath>/test-zip-proxy</BasePath>
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
            js_resource = '''// Test JavaScript resource
var message = "Hello from ZIP bundle test!";
context.setVariable("test.message", message);
print("JavaScript policy executed successfully");'''
            zip_file.writestr('apiproxy/resources/jsc/test-script.js', js_resource)
        
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

    def create_oversized_file(self):
        """Create a file larger than 100MB for size limit testing"""
        # Create a 101MB file (just over the limit)
        size_mb = 101
        content = "A" * (1024 * 1024)  # 1MB of 'A' characters
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add the main apiproxy.xml
            zip_file.writestr('apiproxy/apiproxy.xml', self.create_sample_xml_file())
            
            # Add large files to exceed 100MB
            for i in range(size_mb):
                zip_file.writestr(f'large_file_{i}.txt', content)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def test_xml_upload_backward_compatibility(self):
        """Test that XML file uploads still work (backward compatibility)"""
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

    def test_json_upload_backward_compatibility(self):
        """Test that JSON file uploads still work (backward compatibility)"""
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
        
        files = {'file': ('test-proxy-bundle.zip', zip_content, 'application/zip')}
        
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
        """Test ZIP file upload with invalid structure (missing apiproxy.xml)"""
        zip_content = self.create_invalid_zip_bundle()
        
        files = {'file': ('invalid-proxy-bundle.zip', zip_content, 'application/zip')}
        
        try:
            response = requests.post(f"{self.api_url}/upload-proxy", files=files, timeout=30)
            
            # Should return 400 error for invalid ZIP structure
            if response.status_code == 400:
                response_data = response.json()
                if 'apiproxy.xml' in response_data.get('detail', ''):
                    self.log_test("Invalid ZIP Upload Validation", True)
                    return True, response_data
                else:
                    self.log_test("Invalid ZIP Upload Validation", False, "Wrong error message")
                    return False, {}
            else:
                error_msg = f"Expected 400, got {response.status_code}: {response.text[:200]}"
                self.log_test("Invalid ZIP Upload Validation", False, error_msg)
                return False, {}
                
        except Exception as e:
            self.log_test("Invalid ZIP Upload Validation", False, f"Request error: {str(e)}")
            return False, {}

    def test_oversized_file_upload(self):
        """Test file size validation (100MB limit)"""
        print("   Creating oversized file (this may take a moment)...")
        zip_content = self.create_oversized_file()
        
        files = {'file': ('oversized-proxy-bundle.zip', zip_content, 'application/zip')}
        
        try:
            response = requests.post(f"{self.api_url}/upload-proxy", files=files, timeout=60)
            
            # Should return 413 error for file too large
            if response.status_code == 413:
                response_data = response.json()
                if '100MB' in response_data.get('detail', ''):
                    self.log_test("File Size Limit Validation", True)
                    return True, response_data
                else:
                    self.log_test("File Size Limit Validation", False, "Wrong error message")
                    return False, {}
            else:
                error_msg = f"Expected 413, got {response.status_code}: {response.text[:200]}"
                self.log_test("File Size Limit Validation", False, error_msg)
                return False, {}
                
        except Exception as e:
            self.log_test("File Size Limit Validation", False, f"Request error: {str(e)}")
            return False, {}

    def test_unsupported_file_format(self):
        """Test upload with unsupported file format"""
        # Create a text file
        text_content = "This is not a valid proxy file"
        
        files = {'file': ('test.txt', text_content.encode('utf-8'), 'text/plain')}
        
        try:
            response = requests.post(f"{self.api_url}/upload-proxy", files=files, timeout=30)
            
            # Should return 400 error for unsupported format
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
                
                # Validate that analysis worked for ZIP bundle
                required_fields = ['id', 'proxy_name', 'complexity_score', 'policy_count', 'policy_mappings']
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if missing_fields:
                    self.log_test("ZIP Bundle Analysis", False, f"Missing fields: {missing_fields}")
                    return False, {}
                
                # Check if policies were extracted correctly
                if response_data.get('policy_count', 0) > 0:
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

    def run_zip_upload_tests(self):
        """Run comprehensive ZIP upload functionality tests"""
        print("🚀 Starting ZIP Upload Functionality Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 60)

        # Test 1: Backward compatibility - XML upload
        print("\n📋 Testing Backward Compatibility...")
        success, xml_response = self.test_xml_upload_backward_compatibility()
        
        # Test 2: Backward compatibility - JSON upload
        success, json_response = self.test_json_upload_backward_compatibility()
        
        # Test 3: Valid ZIP upload
        print("\n📦 Testing ZIP Upload Functionality...")
        success, zip_response = self.test_valid_zip_upload()
        zip_proxy_id = zip_response.get('proxy_id') if success else None
        
        # Test 4: Invalid ZIP upload (missing apiproxy.xml)
        success, _ = self.test_invalid_zip_upload()
        
        # Test 5: File size validation
        print("\n📏 Testing File Size Validation...")
        success, _ = self.test_oversized_file_upload()
        
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
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 ZIP UPLOAD TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL ZIP UPLOAD TESTS PASSED!")
            return True
        else:
            print("❌ SOME ZIP UPLOAD TESTS FAILED")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
            return False

def main():
    tester = ZipUploadTester()
    success = tester.run_zip_upload_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())