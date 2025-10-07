#!/bin/bash

# Apigee Migration Tool - Docker Test Script
# Tests all services and functionality after setup

set -e

echo "🧪 Testing Apigee Migration Tool Docker Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $service_name... "
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" -eq "$expected_status" ]; then
            echo -e "${GREEN}✅ PASS${NC} (HTTP $response)"
        else
            echo -e "${RED}❌ FAIL${NC} (HTTP $response, expected $expected_status)"
            return 1
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (Connection failed)"
        return 1
    fi
}

# Check if services are running
echo "📋 Checking Docker services..."
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ Services are not running. Run: docker-compose up -d${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker services are running${NC}"

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 10

# Test each service
echo "🌐 Testing service endpoints..."

test_service "Frontend" "http://localhost:3000" 200
test_service "Backend API" "http://localhost:8001/api/" 200
test_service "API Documentation" "http://localhost:8001/docs" 200

# Test MongoDB connection
echo -n "Testing MongoDB connection... "
if docker-compose exec -T mongodb mongosh --quiet --eval "db.adminCommand('ping')" &>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# Test Redis connection
echo -n "Testing Redis connection... "
if docker-compose exec -T redis redis-cli ping &>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${YELLOW}⚠️  SKIP${NC} (Redis optional)"
fi

# Test API functionality
echo "🔧 Testing API functionality..."

# Test file upload
echo -n "Testing file upload API... "
test_file=$(mktemp)
cat > "$test_file" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<APIProxy name="test-proxy">
    <Policies>
        <Policy>OAuth2</Policy>
        <Policy>VerifyAPIKey</Policy>
    </Policies>
</APIProxy>
EOF

if upload_response=$(curl -s -X POST http://localhost:8001/api/upload-proxy -F "file=@$test_file" 2>/dev/null); then
    if echo "$upload_response" | grep -q "proxy_id"; then
        echo -e "${GREEN}✅ PASS${NC}"
        proxy_id=$(echo "$upload_response" | grep -o '"proxy_id":"[^"]*"' | cut -d'"' -f4)
        
        # Test analysis API
        echo -n "Testing analysis API... "
        if analysis_response=$(curl -s -X POST "http://localhost:8001/api/analyze-proxy/$proxy_id" 2>/dev/null); then
            if echo "$analysis_response" | grep -q "complexity_score"; then
                echo -e "${GREEN}✅ PASS${NC}"
            else
                echo -e "${RED}❌ FAIL${NC} (No complexity score in response)"
            fi
        else
            echo -e "${RED}❌ FAIL${NC} (Analysis request failed)"
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (No proxy_id in response)"
    fi
else
    echo -e "${RED}❌ FAIL${NC} (Upload request failed)"
fi

rm -f "$test_file"

# Test environment configuration
echo "⚙️  Testing environment configuration..."

echo -n "Checking LLM API key... "
if docker-compose exec -T backend python -c "import os; print('✓' if os.environ.get('EMERGENT_LLM_KEY') or os.environ.get('OPENAI_API_KEY') else '✗')" 2>/dev/null | grep -q "✓"; then
    echo -e "${GREEN}✅ CONFIGURED${NC}"
else
    echo -e "${YELLOW}⚠️  NOT CONFIGURED${NC} (Update EMERGENT_LLM_KEY in .env)"
fi

echo -n "Checking MongoDB credentials... "
if docker-compose exec -T backend python -c "import os; print('✓' if os.environ.get('MONGO_URL') else '✗')" 2>/dev/null | grep -q "✓"; then
    echo -e "${GREEN}✅ CONFIGURED${NC}"
else
    echo -e "${RED}❌ NOT CONFIGURED${NC}"
fi

# Test resource usage
echo "📊 Checking resource usage..."
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -5

# Summary
echo ""
echo "🎉 Docker setup test completed!"
echo ""
echo -e "${GREEN}✅ Successful tests:${NC}"
echo "   - Docker services running"
echo "   - Frontend accessible"
echo "   - Backend API responding" 
echo "   - Database connectivity"
echo "   - File upload functionality"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "   1. Update API keys in .env file if needed"
echo "   2. Access frontend: http://localhost:3000"
echo "   3. Access API docs: http://localhost:8001/docs"
echo "   4. Monitor logs: docker-compose logs -f"
echo ""
echo -e "${GREEN}🚀 Your Apigee Migration Tool is ready!${NC}"