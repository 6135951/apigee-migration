import requests
import json
import yaml
import tempfile
import os
from pathlib import Path
import time
import sys
from datetime import datetime

# Import configuration system
try:
    from config import config
except ImportError:
    # Fallback if config not available
    class SimpleConfig:
        base_url = "http://localhost:3000"
        api_timeout = 30
        max_swagger_file_size_mb = 10
        
        @property
        def api_url(self):
            return f"{self.base_url}/api"
    
    config = SimpleConfig()

class ApiDocumentationTester:
    def __init__(self, base_url=None):
        self.base_url = base_url or config.base_url
        self.api_url = f"{self.base_url}/api"
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

    def create_sample_swagger_json(self):
        """Create sample Swagger 2.0 JSON specification"""
        swagger_spec = {
            "swagger": "2.0",
            "info": {
                "title": "BOOMI Order Management API",
                "description": "Sample API for testing migration functionality",
                "version": "1.0.0"
            },
            "host": "api.boomi-orders.example.com",
            "basePath": "/v1",
            "schemes": ["https"],
            "consumes": ["application/json"],
            "produces": ["application/json"],
            "securityDefinitions": {
                "BasicAuth": {
                    "type": "basic"
                },
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            },
            "security": [
                {"BasicAuth": []},
                {"ApiKeyAuth": []}
            ],
            "paths": {
                "/orders": {
                    "get": {
                        "summary": "Get all orders",
                        "description": "Retrieve a list of all orders",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "type": "integer",
                                "description": "Number of orders to return",
                                "default": 10
                            },
                            {
                                "name": "offset",
                                "in": "query",
                                "type": "integer",
                                "description": "Offset for pagination",
                                "default": 0
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "List of orders",
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/definitions/Order"}
                                }
                            },
                            "401": {"description": "Unauthorized"},
                            "500": {"description": "Internal Server Error"}
                        },
                        "security": [{"ApiKeyAuth": []}]
                    },
                    "post": {
                        "summary": "Create a new order",
                        "description": "Create a new order in the system",
                        "parameters": [
                            {
                                "name": "order",
                                "in": "body",
                                "required": True,
                                "schema": {"$ref": "#/definitions/NewOrder"}
                            }
                        ],
                        "responses": {
                            "201": {
                                "description": "Order created successfully",
                                "schema": {"$ref": "#/definitions/Order"}
                            },
                            "400": {"description": "Bad Request"},
                            "401": {"description": "Unauthorized"}
                        }
                    }
                },
                "/orders/{orderId}": {
                    "get": {
                        "summary": "Get order by ID",
                        "parameters": [
                            {
                                "name": "orderId",
                                "in": "path",
                                "required": True,
                                "type": "string",
                                "description": "Order ID"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Order details",
                                "schema": {"$ref": "#/definitions/Order"}
                            },
                            "404": {"description": "Order not found"}
                        }
                    },
                    "put": {
                        "summary": "Update order",
                        "parameters": [
                            {
                                "name": "orderId",
                                "in": "path",
                                "required": True,
                                "type": "string"
                            },
                            {
                                "name": "order",
                                "in": "body",
                                "required": True,
                                "schema": {"$ref": "#/definitions/UpdateOrder"}
                            }
                        ],
                        "responses": {
                            "200": {"description": "Order updated successfully"},
                            "404": {"description": "Order not found"}
                        }
                    },
                    "delete": {
                        "summary": "Delete order",
                        "parameters": [
                            {
                                "name": "orderId",
                                "in": "path",
                                "required": True,
                                "type": "string"
                            }
                        ],
                        "responses": {
                            "204": {"description": "Order deleted successfully"},
                            "404": {"description": "Order not found"}
                        }
                    }
                }
            },
            "definitions": {
                "Order": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "customerId": {"type": "string"},
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/OrderItem"}
                        },
                        "total": {"type": "number", "format": "float"},
                        "status": {"type": "string", "enum": ["pending", "processing", "completed", "cancelled"]},
                        "createdAt": {"type": "string", "format": "date-time"},
                        "updatedAt": {"type": "string", "format": "date-time"}
                    },
                    "required": ["id", "customerId", "items", "total", "status"]
                },
                "NewOrder": {
                    "type": "object",
                    "properties": {
                        "customerId": {"type": "string"},
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/OrderItem"}
                        }
                    },
                    "required": ["customerId", "items"]
                },
                "UpdateOrder": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["pending", "processing", "completed", "cancelled"]},
                        "items": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/OrderItem"}
                        }
                    }
                },
                "OrderItem": {
                    "type": "object",
                    "properties": {
                        "productId": {"type": "string"},
                        "quantity": {"type": "integer", "minimum": 1},
                        "price": {"type": "number", "format": "float"}
                    },
                    "required": ["productId", "quantity", "price"]
                }
            }
        }
        return swagger_spec

    def create_sample_openapi_yaml(self):
        """Create sample OpenAPI 3.0 YAML specification"""
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Customer Management API",
                "description": "Sample OpenAPI 3.0 specification for customer management",
                "version": "2.0.0"
            },
            "servers": [
                {"url": "https://api.customers.example.com/v2"}
            ],
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    },
                    "apiKey": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                },
                "schemas": {
                    "Customer": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "phone": {"type": "string"},
                            "address": {"$ref": "#/components/schemas/Address"}
                        },
                        "required": ["id", "name", "email"]
                    },
                    "Address": {
                        "type": "object",
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"},
                            "state": {"type": "string"},
                            "zipCode": {"type": "string"},
                            "country": {"type": "string"}
                        }
                    }
                }
            },
            "security": [
                {"bearerAuth": []},
                {"apiKey": []}
            ],
            "paths": {
                "/customers": {
                    "get": {
                        "summary": "List customers",
                        "responses": {
                            "200": {
                                "description": "List of customers",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Customer"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "Create customer",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Customer"}
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "Customer created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Customer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        return openapi_spec

    def test_swagger_json_upload(self):
        """Test uploading Swagger 2.0 JSON file"""
        print("\n🔍 Testing Swagger JSON Upload...")
        
        try:
            swagger_spec = self.create_sample_swagger_json()
            
            # Create temporary JSON file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(swagger_spec, f, indent=2)
                temp_file_path = f.name
            
            try:
                # Upload the file
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('boomi-orders-api.json', f, 'application/json')}
                    response = requests.post(f"{self.api_url}/upload-swagger", files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    spec_id = result.get('specId')
                    if spec_id:
                        self.uploaded_specs.append(spec_id)
                        self.log_test("Swagger JSON Upload", True, f"Spec ID: {spec_id}")
                        return True, spec_id
                    else:
                        self.log_test("Swagger JSON Upload", False, "No spec ID returned")
                        return False, None
                else:
                    error_msg = f"Status {response.status_code}: {response.text[:200]}"
                    self.log_test("Swagger JSON Upload", False, error_msg)
                    return False, None
                    
            finally:
                # Clean up temp file
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.log_test("Swagger JSON Upload", False, f"Exception: {str(e)}")
            return False, None

    def test_openapi_yaml_upload(self):
        """Test uploading OpenAPI 3.0 YAML file"""
        print("\n🔍 Testing OpenAPI YAML Upload...")
        
        try:
            openapi_spec = self.create_sample_openapi_yaml()
            
            # Create temporary YAML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(openapi_spec, f, default_flow_style=False)
                temp_file_path = f.name
            
            try:
                # Upload the file
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('customer-api.yaml', f, 'application/x-yaml')}
                    response = requests.post(f"{self.api_url}/upload-swagger", files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    spec_id = result.get('specId')
                    if spec_id:
                        self.uploaded_specs.append(spec_id)
                        self.log_test("OpenAPI YAML Upload", True, f"Spec ID: {spec_id}")
                        return True, spec_id
                    else:
                        self.log_test("OpenAPI YAML Upload", False, "No spec ID returned")
                        return False, None
                else:
                    error_msg = f"Status {response.status_code}: {response.text[:200]}"
                    self.log_test("OpenAPI YAML Upload", False, error_msg)
                    return False, None
                    
            finally:
                # Clean up temp file
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.log_test("OpenAPI YAML Upload", False, f"Exception: {str(e)}")
            return False, None

    def test_swagger_conversion(self, spec_id):
        """Test converting Swagger to Apigee X format"""
        print(f"\n🔄 Testing Swagger Conversion for spec {spec_id}...")
        
        try:
            response = requests.post(f"{self.api_url}/convert-swagger/{spec_id}", timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                converted_spec = result.get('convertedSpec')
                
                if converted_spec:
                    # Validate conversion results
                    validation_results = self.validate_converted_spec(converted_spec)
                    if validation_results['valid']:
                        self.log_test("Swagger Conversion", True, f"Converted to OpenAPI 3.0 with {len(validation_results['features'])} Apigee X features")
                        return True, converted_spec
                    else:
                        self.log_test("Swagger Conversion", False, f"Invalid conversion: {validation_results['errors']}")
                        return False, None
                else:
                    self.log_test("Swagger Conversion", False, "No converted spec returned")
                    return False, None
            else:
                error_msg = f"Status {response.status_code}: {response.text[:200]}"
                self.log_test("Swagger Conversion", False, error_msg)
                return False, None
                
        except Exception as e:
            self.log_test("Swagger Conversion", False, f"Exception: {str(e)}")
            return False, None

    def validate_converted_spec(self, converted_spec):
        """Validate the converted OpenAPI specification"""
        validation_result = {
            'valid': True,
            'errors': [],
            'features': []
        }
        
        # Check if it's OpenAPI 3.0+
        if not converted_spec.get('openapi', '').startswith('3.'):
            validation_result['errors'].append("Not converted to OpenAPI 3.0+")
            validation_result['valid'] = False
        else:
            validation_result['features'].append("OpenAPI 3.0+ format")
        
        # Check for security schemes
        components = converted_spec.get('components', {})
        security_schemes = components.get('securitySchemes', {})
        if security_schemes:
            validation_result['features'].append(f"Security schemes: {list(security_schemes.keys())}")
        
        # Check for Apigee X extensions
        if 'x-google-management' in converted_spec:
            validation_result['features'].append("Apigee X management extensions")
        
        # Check for paths
        paths = converted_spec.get('paths', {})
        if paths:
            validation_result['features'].append(f"API paths: {len(paths)} endpoints")
        
        return validation_result

    def test_file_size_validation(self):
        """Test file size validation (should reject files > 10MB)"""
        print("\n📏 Testing File Size Validation...")
        
        try:
            # Create a large JSON file (simulate > 10MB)
            large_spec = self.create_sample_swagger_json()
            # Add large description to make it bigger
            large_spec['info']['description'] = 'A' * (11 * 1024 * 1024)  # 11MB of 'A's
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(large_spec, f)
                temp_file_path = f.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('large-file.json', f, 'application/json')}
                    response = requests.post(f"{self.api_url}/upload-swagger", files=files, timeout=30)
                
                if response.status_code == 413:  # File too large
                    self.log_test("File Size Validation", True, "Correctly rejected large file")
                    return True
                else:
                    self.log_test("File Size Validation", False, f"Did not reject large file (status: {response.status_code})")
                    return False
                    
            finally:
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.log_test("File Size Validation", False, f"Exception: {str(e)}")
            return False

    def test_invalid_file_format(self):
        """Test uploading invalid file format"""
        print("\n❌ Testing Invalid File Format...")
        
        try:
            # Create a text file (not JSON/YAML)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("This is not a valid API specification")
                temp_file_path = f.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    files = {'file': ('invalid.txt', f, 'text/plain')}
                    response = requests.post(f"{self.api_url}/upload-swagger", files=files, timeout=30)
                
                if response.status_code == 400:  # Bad request
                    self.log_test("Invalid File Format", True, "Correctly rejected invalid format")
                    return True
                else:
                    self.log_test("Invalid File Format", False, f"Did not reject invalid format (status: {response.status_code})")
                    return False
                    
            finally:
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.log_test("Invalid File Format", False, f"Exception: {str(e)}")
            return False

    def test_complete_workflow(self):
        """Test complete end-to-end workflow"""
        print("\n🔄 Testing Complete Workflow...")
        
        workflow_success = True
        
        # Step 1: Upload Swagger JSON
        success, spec_id = self.test_swagger_json_upload()
        if not success:
            workflow_success = False
        
        # Step 2: Convert to Apigee X
        if success and spec_id:
            success, converted_spec = self.test_swagger_conversion(spec_id)
            if not success:
                workflow_success = False
        
        # Step 3: Upload OpenAPI YAML (separate flow)
        yaml_success, yaml_spec_id = self.test_openapi_yaml_upload()
        if not yaml_success:
            workflow_success = False
        
        # Step 4: Convert YAML spec
        if yaml_success and yaml_spec_id:
            yaml_conversion_success, _ = self.test_swagger_conversion(yaml_spec_id)
            if not yaml_conversion_success:
                workflow_success = False
        
        self.log_test("Complete Workflow", workflow_success, "End-to-end API documentation migration")
        return workflow_success

    def run_all_tests(self):
        """Run all API documentation tests"""
        print("🚀 Starting API Documentation & Testing - Automated Tests")
        print("=" * 70)
        
        start_time = time.time()
        
        # Test individual components
        print("\n📋 INDIVIDUAL COMPONENT TESTS")
        print("-" * 40)
        
        self.test_swagger_json_upload()
        self.test_openapi_yaml_upload()
        
        # Test conversion for uploaded specs
        if self.uploaded_specs:
            for spec_id in self.uploaded_specs:
                self.test_swagger_conversion(spec_id)
        
        # Test validation
        self.test_file_size_validation()
        self.test_invalid_file_format()
        
        # Test complete workflow
        print("\n📋 END-TO-END WORKFLOW TEST")
        print("-" * 40)
        self.test_complete_workflow()
        
        # Generate summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  Some tests failed. Please check the details above.")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    # Use configuration system (supports command line args and environment variables)
    tester = ApiDocumentationTester()
    print(f"🌐 Testing against: {tester.base_url}")
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)