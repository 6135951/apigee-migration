import requests
import zipfile
import os
import random
from io import BytesIO

def create_large_uncompressible_file(size_mb):
    """Create a ZIP file with random data that won't compress much"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_STORED) as zip_file:  # No compression
        # Add main apiproxy.xml
        apiproxy_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy revision="1" name="test-large-proxy">
    <ConfigurationVersion majorVersion="4" minorVersion="0"/>
    <CreatedAt>1234567890000</CreatedAt>
    <CreatedBy>test@example.com</CreatedBy>
    <Description>Test large proxy bundle</Description>
    <DisplayName>Test Large Proxy</DisplayName>
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
        
        # Create random binary data that won't compress
        chunk_size = 1024 * 1024  # 1MB chunks
        for i in range(size_mb):
            # Generate random bytes
            random_data = bytes([random.randint(0, 255) for _ in range(chunk_size)])
            zip_file.writestr(f'random_data_{i}.bin', random_data)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def test_large_file():
    """Test with a file that's actually over 100MB"""
    print("Creating 101MB file with random data (no compression)...")
    
    # Configure base URL
    base_url = "http://localhost:3000"
    
    zip_content = create_large_uncompressible_file(101)
    actual_size_mb = len(zip_content) / (1024 * 1024)
    print(f"Actual file size: {actual_size_mb:.2f}MB")
    
    if actual_size_mb < 100:
        print("❌ File is still too small after adding random data")
        return False
    
    files = {'file': ('test-large.zip', zip_content, 'application/zip')}
    
    try:
        print("Uploading large file...")
        response = requests.post(
            f"{base_url}/api/upload-proxy", 
            files=files, 
            timeout=120
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 413:
            print("✅ PASSED - File size limit working correctly")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text[:200]}")
            return True
        else:
            print(f"❌ FAILED - Expected 413, got {response.status_code}")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED - Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_large_file()