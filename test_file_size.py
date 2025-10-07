import requests
import zipfile
from io import BytesIO

def create_test_file(size_mb):
    """Create a test ZIP file of specified size"""
    zip_buffer = BytesIO()
    
    # Create content to fill the file
    content_1mb = "A" * (1024 * 1024)  # 1MB of 'A' characters
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add main apiproxy.xml
        apiproxy_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy revision="1" name="test-size-proxy">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <CreatedAt>1234567890000</CreatedAt>
    <CreatedBy>test@example.com</CreatedBy>
    <Description>Test size proxy bundle</Description>
    <DisplayName>Test Size Proxy</DisplayName>
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
        
        # Add large files to reach desired size
        for i in range(size_mb):
            zip_file.writestr(f'large_file_{i}.txt', content_1mb)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def test_file_size(size_mb, expected_status):
    """Test file upload with specific size"""
    print(f"Testing {size_mb}MB file (expecting status {expected_status})...")
    
    zip_content = create_test_file(size_mb)
    actual_size_mb = len(zip_content) / (1024 * 1024)
    print(f"Actual file size: {actual_size_mb:.2f}MB")
    
    files = {'file': (f'test-{size_mb}mb.zip', zip_content, 'application/zip')}
    
    try:
        response = requests.post(
            "https://proxy-zip-support.preview.emergentagent.com/api/upload-proxy", 
            files=files, 
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == expected_status:
            print("✅ PASSED")
            return True
        else:
            print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED - Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing file size validation...")
    
    # Test with 50MB file (should pass)
    test_file_size(50, 200)
    
    print("\n" + "="*50 + "\n")
    
    # Test with 101MB file (should fail)
    test_file_size(101, 413)