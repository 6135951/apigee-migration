import requests
import sys
import json
import time
import yaml
from datetime import datetime
from pathlib import Path

class APIDocumentationTester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.uploaded_specs = []

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

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        if headers is None:
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

    def test_upload_swagger_json(self):
        """Test uploading BOOMI Orders Swagger JSON file"""
        sample_file_path = Path("/app/tests/sample_data/boomi-orders-swagger.json")
        
        if not sample_file_path.exists():
            self.log_test("Upload Swagger JSON", False, "Sample swagger file not found")
            return False, {}
        
        with open(sample_file_path, 'rb') as f:
            files = {'file': ('boomi-orders-swagger.json', f, 'application/json')}
            success, response = self.run_test(
                "Upload BOOMI Orders Swagger JSON", 
                "POST", 
                "upload-swagger", 
                200, 
                files=files
            )
        
        if success and 'specId' in response:
            self.uploaded_specs.append({
                'id': response['specId'],
                'filename': 'boomi-orders-swagger.json',
                'type': 'swagger_2.0'
            })
        
        return success, response

    def test_upload_openapi_yaml(self):
        """Test uploading Customer API OpenAPI YAML file"""
        sample_file_path = Path("/app/tests/sample_data/customer-api-openapi.yaml")
        
        if not sample_file_path.exists():
            self.log_test("Upload OpenAPI YAML", False, "Sample OpenAPI file not found")
            return False, {}
        
        with open(sample_file_path, 'rb') as f:
            files = {'file': ('customer-api-openapi.yaml', f, 'application/x-yaml')}
            success, response = self.run_test(
                "Upload Customer API OpenAPI YAML", 
                "POST", 
                "upload-swagger", 
                200, 
                files=files
            )
        
        if success and 'specId' in response:
            self.uploaded_specs.append({
                'id': response['specId'],
                'filename': 'customer-api-openapi.yaml',
                'type': 'openapi_3.0'
            })
        
        return success, response

    def test_file_size_validation(self):
        """Test file size validation (should reject files > 10MB)"""
        # Create a large dummy JSON file content
        large_content = {
            "swagger": "2.0",
            "info": {"title": "Large API", "version": "1.0.0"},
            "paths": {},
            "definitions": {}
        }
        
        # Add large data to exceed 10MB
        large_data = "x" * (11 * 1024 * 1024)  # 11MB of data
        large_content["definitions"]["LargeData"] = {"type": "string", "example": large_data}
        
        large_json = json.dumps(large_content).encode('utf-8')
        
        # Create a temporary file-like object
        from io import BytesIO
        large_file = BytesIO(large_json)
        
        files = {'file': ('large-swagger.json', large_file, 'application/json')}
        success, response = self.run_test(
            "File Size Validation (>10MB)", 
            "POST", 
            "upload-swagger", 
            413,  # Expect 413 Payload Too Large
            files=files
        )
        
        return success, response

    def test_invalid_file_format(self):
        """Test invalid file format handling"""
        # Create a text file that's not JSON/YAML
        invalid_content = "This is not a valid JSON or YAML file"
        
        from io import BytesIO
        invalid_file = BytesIO(invalid_content.encode('utf-8'))
        
        files = {'file': ('invalid.txt', invalid_file, 'text/plain')}
        success, response = self.run_test(
            "Invalid File Format Validation", 
            "POST", 
            "upload-swagger", 
            400,  # Expect 400 Bad Request
            files=files
        )
        
        return success, response

    def test_malformed_json(self):
        """Test malformed JSON handling"""
        malformed_json = '{"swagger": "2.0", "info": {"title": "Test"'  # Missing closing braces
        
        from io import BytesIO
        malformed_file = BytesIO(malformed_json.encode('utf-8'))
        
        files = {'file': ('malformed.json', malformed_file, 'application/json')}
        success, response = self.run_test(
            "Malformed JSON Validation", 
            "POST", 
            "upload-swagger", 
            400,  # Expect 400 Bad Request
            files=files
        )
        
        return success, response

    def test_invalid_swagger_spec(self):
        """Test invalid Swagger/OpenAPI specification"""
        invalid_spec = {
            "title": "Not a swagger spec",
            "version": "1.0.0"
        }
        
        invalid_json = json.dumps(invalid_spec).encode('utf-8')
        
        from io import BytesIO
        invalid_file = BytesIO(invalid_json)
        
        files = {'file': ('invalid-spec.json', invalid_file, 'application/json')}
        success, response = self.run_test(
            "Invalid Swagger Spec Validation", 
            "POST", 
            "upload-swagger", 
            400,  # Expect 400 Bad Request
            files=files
        )
        
        return success, response

    def test_convert_swagger_to_apigee_x(self, spec_id, spec_type):
        """Test Swagger to Apigee X conversion"""
        print(f"   Converting spec ID: {spec_id} (Type: {spec_type})")
        success, response = self.run_test(
            f"Convert {spec_type} to Apigee X", 
            "POST", 
            f"convert-swagger/{spec_id}", 
            200
        )
        
        if success:
            # Wait a bit for AI conversion to complete
            print("   Waiting for AI conversion to complete...")
            time.sleep(2)
            
            # Validate conversion response
            if 'convertedSpec' in response:
                converted_spec = response['convertedSpec']
                
                # Check if it's a valid OpenAPI 3.0+ spec
                if 'openapi' in converted_spec:
                    openapi_version = converted_spec['openapi']
                    if openapi_version.startswith('3.'):
                        self.log_test(f"Conversion Output Validation ({spec_type})", True)
                    else:
                        self.log_test(f"Conversion Output Validation ({spec_type})", False, f"Invalid OpenAPI version: {openapi_version}")
                else:
                    self.log_test(f"Conversion Output Validation ({spec_type})", False, "Converted spec missing 'openapi' field")
                
                # Check for Apigee X specific extensions
                if 'x-google-management' in converted_spec:
                    self.log_test(f"Apigee X Extensions Validation ({spec_type})", True)
                else:
                    self.log_test(f"Apigee X Extensions Validation ({spec_type})", False, "Missing Apigee X extensions")
                
                # Check for security schemes
                if 'components' in converted_spec and 'securitySchemes' in converted_spec['components']:
                    security_schemes = converted_spec['components']['securitySchemes']
                    # Check for any API key or OAuth2 type security schemes
                    has_api_key = any(scheme.get('type') == 'apiKey' for scheme in security_schemes.values())
                    has_oauth2 = any(scheme.get('type') == 'oauth2' for scheme in security_schemes.values())
                    has_http = any(scheme.get('type') == 'http' for scheme in security_schemes.values())
                    
                    if has_api_key or has_oauth2 or has_http:
                        self.log_test(f"Security Schemes Validation ({spec_type})", True)
                    else:
                        self.log_test(f"Security Schemes Validation ({spec_type})", False, f"No recognized security schemes found. Available: {list(security_schemes.keys())}")
                else:
                    self.log_test(f"Security Schemes Validation ({spec_type})", False, "Missing security schemes")
            else:
                self.log_test(f"Conversion Response Validation ({spec_type})", False, "Missing 'convertedSpec' in response")
        
        return success, response

    def test_convert_nonexistent_spec(self):
        """Test conversion with non-existent spec ID"""
        fake_spec_id = "non-existent-spec-id-12345"
        success, response = self.run_test(
            "Convert Non-existent Spec", 
            "POST", 
            f"convert-swagger/{fake_spec_id}", 
            404  # Expect 404 Not Found
        )
        
        return success, response

    def validate_upload_response(self, response, expected_filename):
        """Validate upload response structure"""
        required_fields = ['specId', 'message', 'originalSpec']
        
        missing_fields = []
        for field in required_fields:
            if field not in response:
                missing_fields.append(field)
        
        if missing_fields:
            self.log_test(f"Upload Response Validation ({expected_filename})", False, f"Missing fields: {missing_fields}")
            return False
        
        # Validate spec ID format (should be UUID)
        spec_id = response['specId']
        if len(spec_id) != 36 or spec_id.count('-') != 4:
            self.log_test(f"Upload Response Validation ({expected_filename})", False, "Invalid spec ID format")
            return False
        
        # Validate original spec structure (should be JSON string)
        original_spec = response['originalSpec']
        if not isinstance(original_spec, str):
            self.log_test(f"Upload Response Validation ({expected_filename})", False, "Original spec should be a JSON string")
            return False
        
        # Try to parse the JSON string to validate it's valid JSON
        try:
            parsed_spec = json.loads(original_spec)
            if not isinstance(parsed_spec, dict):
                self.log_test(f"Upload Response Validation ({expected_filename})", False, "Parsed original spec should be a dictionary")
                return False
        except json.JSONDecodeError:
            self.log_test(f"Upload Response Validation ({expected_filename})", False, "Original spec is not valid JSON")
            return False
        
        self.log_test(f"Upload Response Validation ({expected_filename})", True)
        return True

    def run_full_test_suite(self):
        """Run complete API Documentation test suite"""
        print("🚀 Starting API Documentation & Testing Backend Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 70)

        # Test 1: Upload BOOMI Orders Swagger JSON
        print("\n📄 Testing Swagger JSON Upload...")
        success, upload_response = self.test_upload_swagger_json()
        if success:
            self.validate_upload_response(upload_response, "boomi-orders-swagger.json")

        # Test 2: Upload Customer API OpenAPI YAML
        print("\n📄 Testing OpenAPI YAML Upload...")
        success, upload_response = self.test_upload_openapi_yaml()
        if success:
            self.validate_upload_response(upload_response, "customer-api-openapi.yaml")

        # Test 3: File size validation
        print("\n📏 Testing File Size Validation...")
        self.test_file_size_validation()

        # Test 4: Invalid file format
        print("\n🚫 Testing Invalid File Format...")
        self.test_invalid_file_format()

        # Test 5: Malformed JSON
        print("\n🚫 Testing Malformed JSON...")
        self.test_malformed_json()

        # Test 6: Invalid Swagger spec
        print("\n🚫 Testing Invalid Swagger Spec...")
        self.test_invalid_swagger_spec()

        # Test 7: AI Conversion for uploaded specs
        print("\n🤖 Testing AI Conversion...")
        for spec in self.uploaded_specs:
            self.test_convert_swagger_to_apigee_x(spec['id'], spec['type'])

        # Test 8: Convert non-existent spec
        print("\n🚫 Testing Non-existent Spec Conversion...")
        self.test_convert_nonexistent_spec()

        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 70)
        print("📊 API DOCUMENTATION TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        print(f"\nUploaded Specifications: {len(self.uploaded_specs)}")
        for spec in self.uploaded_specs:
            print(f"  - {spec['filename']} (ID: {spec['id'][:8]}..., Type: {spec['type']})")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL API DOCUMENTATION TESTS PASSED!")
            return 0
        else:
            print("\n❌ SOME API DOCUMENTATION TESTS FAILED")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
            return 1

def main():
    tester = APIDocumentationTester()
    return tester.run_full_test_suite()

if __name__ == "__main__":
    sys.exit(main())