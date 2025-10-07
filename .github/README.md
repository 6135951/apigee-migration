# 🚀 Apigee Migration Tool

**Automated Apigee Edge to Apigee X Migration with AI-Powered Analysis**

A comprehensive full-stack application that automates the migration process from Apigee Edge to Apigee X using advanced AI analysis, real-time policy conversion, and interactive migration management.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-green.svg)
![React](https://img.shields.io/badge/frontend-React-blue.svg)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-green.svg)
![MongoDB](https://img.shields.io/badge/database-MongoDB-green.svg)

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [💻 Local Development](#-local-development)
- [🐳 Docker Deployment](#-docker-deployment)
- [🗄️ Database Configuration](#️-database-configuration)
- [🔐 Security & API Keys](#-security--api-keys)
- [📊 Application Features](#-application-features)
- [🛠️ API Documentation](#️-api-documentation)
- [🧪 Testing](#-testing)
- [📝 Development Guide](#-development-guide)
- [🚨 Troubleshooting](#-troubleshooting)

## 🎯 Overview

The **Apigee Migration Tool** is an enterprise-grade application designed to automate and simplify the migration process from Apigee Edge to Apigee X. It leverages artificial intelligence to analyze proxy configurations, assess migration complexity, and provide intelligent recommendations for seamless transitions.

### 🎪 Live Demo

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Interactive API**: http://localhost:8001/redoc

### 🎬 Key Use Cases

1. **Automated Proxy Assessment**: Upload Apigee Edge proxies and get instant AI-powered complexity analysis
2. **Policy Mapping & Conversion**: Intelligent mapping of Edge policies to Apigee X equivalents
3. **Real-time Migration**: Execute migrations with live progress tracking and console logging
4. **Interactive Policy Review**: View and edit converted policies before migration
5. **Migration Management**: Track, pause, resume, and manage multiple migrations
6. **Enterprise Analytics**: Comprehensive dashboards with migration insights

## ✨ Key Features

### 🤖 AI-Powered Analysis
- **ChatGPT 4.1 Integration** for intelligent proxy analysis
- **Complexity Scoring** (0-100) with detailed breakdowns
- **Custom Policy Detection** with migration recommendations
- **Risk Assessment** for complex migrations

### 🔄 Real-time Migration
- **Live Console Logging** with terminal-style output
- **Step-by-step Validation** with user approval workflow
- **Policy Conversion Preview** before execution
- **Background Processing** with progress tracking

### 🖥️ Interactive UI/UX
- **Modern Glass-morphism Design** with responsive layout
- **Policy Comparison Viewer** (Edge vs Apigee X side-by-side)
- **Edit Capabilities** for converted policies
- **Comprehensive Dashboards** with analytics and charts

### 🔐 Enterprise Security
- **Multiple Authentication Methods** (JWT, OAuth2)
- **Secure Credential Management** for Apigee environments
- **Environment Variable Security** with multiple secret sources
- **Audit Logging** for all migration activities

### 📊 Advanced Analytics
- **Migration Success Rates** and performance metrics
- **Policy Usage Statistics** across all analyzed proxies
- **Complexity Distribution** charts and visualizations
- **Export Capabilities** for reports and analytics

## 🏗️ Architecture

### 🎨 System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React SPA<br/>Port: 3000] --> B[Nginx<br/>Static Files]
    end
    
    subgraph "Backend Layer"
        C[FastAPI Server<br/>Port: 8001] --> D[LLM Integration<br/>ChatGPT 4.1]
        C --> E[Policy Engine<br/>Edge → X Mapping]
        C --> F[Migration Engine<br/>Real-time Processing]
    end
    
    subgraph "Data Layer"
        G[MongoDB<br/>Port: 27017] --> H[Proxy Configurations]
        G --> I[Analysis Results]
        G --> J[Migration History]
        K[Redis Cache<br/>Port: 6379] --> L[Session Storage]
        K --> M[Migration State]
    end
    
    subgraph "External Integrations"
        N[Apigee Edge APIs] --> C
        O[Apigee X APIs] --> C
        P[LLM Services] --> D
    end
    
    A --> C
    C --> G
    C --> K
    
    classDef frontend fill:#e1f5fe
    classDef backend fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef external fill:#fce4ec
    
    class A,B frontend
    class C,D,E,F backend
    class G,H,I,J,K,L,M data
    class N,O,P external
```

### 🔧 Technology Stack

#### Frontend
- **React 19.0** - Modern UI framework with hooks
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/UI** - High-quality component library
- **Recharts** - Interactive charts and visualizations
- **Axios** - HTTP client for API communication
- **React Router** - Client-side routing

#### Backend
- **FastAPI** - High-performance async Python framework
- **Pydantic** - Data validation and serialization
- **Motor** - Async MongoDB driver
- **OpenAI Python SDK** - Direct OpenAI API integration for AI analysis
- **Python-Jose** - JWT token handling
- **Uvicorn** - ASGI server

#### Database
- **MongoDB 7.0** - Document database for flexible data storage
- **Redis 7.2** - In-memory cache for session management
- **Motor** - Async MongoDB operations

#### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy and static file serving
- **GitHub Actions** - CI/CD pipeline

### 📁 Project Structure

```
apigee-migration-tool/
├── 📁 frontend/                    # React application
│   ├── 📁 public/                  # Static assets
│   ├── 📁 src/                     # Source code
│   │   ├── 📁 components/          # React components
│   │   │   ├── 📁 ui/             # Shadcn UI components
│   │   │   ├── Dashboard.js        # Main dashboard
│   │   │   ├── Migration.js        # Migration center
│   │   │   ├── ProxyAnalysis.js    # Analysis results
│   │   │   └── ProxyUpload.js      # File upload interface
│   │   ├── App.js                  # Main application component
│   │   ├── App.css                 # Global styles
│   │   └── index.js               # Application entry point
│   ├── package.json               # Dependencies
│   └── tailwind.config.js         # Tailwind configuration
├── 📁 backend/                     # FastAPI server
│   ├── server.py                  # Main server application
│   ├── requirements.txt           # Python dependencies
│   └── .env                      # Environment variables
├── 📁 docker/                     # Docker configurations
│   ├── nginx.conf                 # Nginx configuration
│   ├── nginx-proxy.conf          # Production proxy
│   └── mongo-init.js             # MongoDB initialization
├── 📁 scripts/                    # Automation scripts
│   ├── setup-aws-secrets.sh      # AWS integration
│   ├── azure-keyvault.py         # Azure integration
│   └── setup-vault.sh            # Vault integration
├── 📁 k8s/                        # Kubernetes deployment
│   └── deployment.yml            # K8s manifests
├── 📁 .github/                    # GitHub Actions
│   └── workflows/deploy.yml      # CI/CD pipeline
├── docker-compose.yml            # Main orchestration
├── docker-compose.dev.yml        # Development override
├── Dockerfile.backend            # Backend container
├── Dockerfile.frontend           # Frontend container
├── .env                          # Environment variables
├── setup.sh                     # Quick setup script
└── README.md                     # This file
```

## 🚀 Quick Start

### ⚡ One-Command Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd apigee-migration-tool

# Quick setup (includes Docker build and start)
# Note: .env file is included in repository for local development
chmod +x setup.sh
./setup.sh
```

**📝 Note**: The `.env` file is **included in the repository** with pre-configured values for local development, including:
- ✅ **OPENAI_API_KEY** - Configured for AI analysis features
- ✅ **MongoDB credentials** - Ready for local development
- ✅ **Port configurations** - Optimized for local setup
- ✅ **CORS settings** - Configured for localhost development

For production deployments, copy `.env.example` and update with your production values.

### 🌐 Access Points

After setup completes:

- **🖥️ Frontend Application**: http://localhost:3000
- **🔌 Backend API**: http://localhost:8001
- **📚 API Documentation**: http://localhost:8001/docs
- **🗄️ MongoDB**: localhost:27017
- **🧠 Redis Cache**: localhost:6379

### ✅ Verify Installation

```bash
# Test all services
./test-docker.sh

# Check individual services
curl http://localhost:8001/api/          # Backend API
curl http://localhost:3000               # Frontend
docker-compose ps                        # Service status
```

## 💻 Local Development

### 🛠️ Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Node.js** 18+ and **Yarn** (for frontend development)
- **Python** 3.11+ (for backend development)
- **4GB RAM** minimum, **8GB recommended**
- **10GB disk space**

### 🔧 Development Setup

#### Option 1: Full Docker Development (Recommended)
```bash
# Start all services with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f backend frontend
```

#### Option 2: Hybrid Development (Frontend local, Backend Docker)
```bash
# Start backend and database only
docker-compose up -d backend mongodb redis

# Install frontend dependencies locally
cd frontend
yarn install

# Start frontend with hot reload
yarn start
```

#### Option 3: Full Local Development
```bash
# Start databases only
docker-compose up -d mongodb redis

# Backend setup
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Frontend setup (new terminal)
cd frontend
yarn install
yarn start
```

### 🔄 Development Workflow

1. **Make Changes**: Edit files in `frontend/src/` or `backend/`
2. **Hot Reload**: Changes automatically reload in development mode
3. **Test Changes**: Use `./test-docker.sh` or manual testing
4. **Commit**: Use conventional commits for better tracking

### 🧪 Running Tests

```bash
# Run all tests
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build

# Backend tests only
cd backend
pytest tests/

# Frontend tests only
cd frontend
yarn test

# Integration tests
./test-docker.sh
```

## 🐳 Docker Deployment

### 🏠 Local Docker Deployment

```bash
# Production-like local deployment
docker-compose --profile production up -d

# With custom environment
cp .env.example .env.production
docker-compose --env-file .env.production up -d
```

### ☁️ Cloud Deployment

#### AWS Deployment
```bash
# Using AWS Secrets Manager
export AWS_SECRET_NAME="apigee-migration-tool/production"
./scripts/setup-aws-secrets.sh
```

#### Azure Deployment
```bash
# Using Azure Key Vault
export AZURE_VAULT_URL="https://your-vault.vault.azure.net/"
python3 scripts/azure-keyvault.py
docker-compose up -d
```

#### Kubernetes Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/deployment.yml

# Check deployment status
kubectl get pods -n apigee-migration
kubectl logs -f deployment/apigee-backend -n apigee-migration
```

### 📊 Monitoring & Scaling

```bash
# Monitor resource usage
docker stats

# Scale services
docker-compose up -d --scale backend=3

# View service health
curl http://localhost:8001/api/health
```

## 🗄️ Database Configuration

### 🍃 MongoDB Setup

The application uses **MongoDB 7.0** as the primary database for storing:

- **Proxy Configurations** - Uploaded Apigee Edge XML/JSON files
- **Analysis Results** - AI-powered complexity assessments
- **Migration History** - Execution logs and status tracking
- **User Credentials** - Encrypted Apigee environment credentials

#### 🔗 Connection Details

```env
# Default MongoDB Configuration (from .env file)
MONGO_ROOT_USERNAME=apigee_admin
MONGO_ROOT_PASSWORD=SecureMongo2024!@#
MONGO_DATABASE=apigee_migration_db
MONGO_PORT=27017

# Connection String (automatically constructed)
mongodb://apigee_admin:SecureMongo2024!@#@mongodb:27017/apigee_migration_db?authSource=admin
```

#### 📊 Database Schema

```javascript
// Proxy Files Collection
{
  "_id": ObjectId,
  "id": "unique-uuid",
  "filename": "oauth-proxy.xml",
  "content": "<xml>proxy configuration</xml>",
  "file_type": "xml|json",
  "uploaded_at": ISODate
}

// Proxy Analyses Collection
{
  "_id": ObjectId,
  "id": "unique-uuid",
  "proxy_id": "reference-to-proxy-file",
  "proxy_name": "oauth-sample-proxy",
  "complexity_score": 65.5,
  "complexity_level": "moderate|simple|complex",
  "policy_count": 12,
  "custom_policies": ["CustomAuth", "CustomLogging"],
  "policy_mappings": [
    {
      "edge_policy": "OAuth2",
      "apigee_x_equivalent": "OAuthV2",
      "complexity": "simple",
      "migration_notes": "Direct mapping available"
    }
  ],
  "ai_recommendations": "Generated by ChatGPT 4.1",
  "analyzed_at": ISODate,
  "status": "completed"
}

// Migration Executions Collection
{
  "_id": ObjectId,
  "id": "unique-uuid",
  "proxy_analysis_id": "reference-to-analysis",
  "proxy_name": "oauth-sample-proxy",
  "credentials_id": "reference-to-credentials",
  "status": "pending|preparing|converting|completed|failed",
  "progress": 85,
  "current_step": "Validating Apigee X bundle",
  "steps_completed": ["validation", "conversion"],
  "migration_log": ["Step 1 completed", "Step 2 in progress"],
  "apigee_x_bundle": "converted XML content",
  "started_at": ISODate,
  "completed_at": ISODate
}

// Credentials Collection (Encrypted)
{
  "_id": ObjectId,
  "id": "unique-uuid",
  "name": "Production Environment",
  "edge_org": "my-edge-org",
  "edge_env": "prod",
  "apigee_x_project": "my-apigee-x-project",
  "created_at": ISODate
  // Sensitive fields encrypted
}
```

#### 🔧 Database Administration

```bash
# Connect to MongoDB container
docker-compose exec mongodb mongosh -u apigee_admin -p

# View databases
show dbs

# Use application database
use apigee_migration_db

# View collections
show collections

# Query proxy analyses
db.proxy_analyses.find({}).limit(5).pretty()

# Check migration status
db.migration_executions.find({"status": "in_progress"})

# Create indexes (already automated)
db.proxy_analyses.createIndex({"proxy_name": 1})
db.migration_executions.createIndex({"status": 1})
```

#### 💾 Backup & Recovery

```bash
# Backup database
docker-compose exec mongodb mongodump --out /tmp/backup --authenticationDatabase admin

# Restore database
docker-compose exec mongodb mongorestore /tmp/backup --authenticationDatabase admin

# Export specific collection
docker-compose exec mongodb mongoexport --db apigee_migration_db --collection proxy_analyses --out analyses.json
```

### 🧠 Redis Configuration

Redis is used for:

- **Session Management** - User sessions and temporary data
- **Migration State** - Real-time migration progress tracking
- **API Rate Limiting** - Request throttling and quota management
- **Caching** - Frequently accessed analysis results

```env
# Redis Configuration (from .env file)
REDIS_PASSWORD=SecureRedis2024!@#
REDIS_PORT=6379
```

## 🔐 Security & API Keys

### 🗝️ Required API Keys

The application requires AI/LLM API keys for intelligent proxy analysis:

#### OpenAI API Configuration (Current Setup)
```env
# OpenAI API Key for AI analysis and migration features
OPENAI_API_KEY=sk-your-openai-api-key-here  # ✅ Update with your key
```

**To get your OpenAI API key:**
1. Go to https://platform.openai.com/account/api-keys
2. Click "Create new secret key" 
3. Copy the key and replace the placeholder above

#### Alternative: Individual Provider Keys (Optional)
```env
# If you prefer to use other providers directly
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Anthropic API Key (for Claude models)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Google API Key (for Gemini models)
GOOGLE_API_KEY=your-google-api-key-here
```

### 🔒 Security Features

- **Environment Variable Encryption** - All sensitive data stored securely
- **JWT Authentication** - Secure API access tokens
- **CORS Protection** - Configurable cross-origin resource sharing
- **Input Validation** - Comprehensive request validation
- **Audit Logging** - All actions logged for compliance
- **Rate Limiting** - Protection against abuse

### 📋 Environment Configuration

The `.env` file contains all necessary configuration:

```env
# Application Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Service Ports
FRONTEND_PORT=3000
BACKEND_PORT=8001
MONGO_PORT=27017
REDIS_PORT=6379

# Security Keys
OPENAI_API_KEY=sk-your-openai-api-key-here  # Update with your OpenAI key
JWT_SECRET=your-super-secure-jwt-secret-key-minimum-32-characters
ENCRYPTION_KEY=your-32-character-encryption-key-12

# Database Credentials
MONGO_ROOT_USERNAME=apigee_admin
MONGO_ROOT_PASSWORD=SecureMongo2024!@#
MONGO_DATABASE=apigee_migration_db

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:80
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 📊 Application Features

### 🏠 Dashboard
- **Migration Statistics** - Total analyses, complexity distribution
- **Real-time Metrics** - Active migrations, success rates
- **Interactive Charts** - Policy usage, complexity trends
- **Recent Activity** - Latest analyses and migrations

### 📤 Proxy Upload
- **Drag & Drop Interface** - Easy file upload
- **Format Support** - XML and JSON proxy configurations
- **Validation** - Automatic file format verification
- **Progress Tracking** - Upload status with progress bars

### 🔍 Analysis Engine
- **AI-Powered Assessment** - ChatGPT 4.1 complexity analysis
- **Policy Detection** - Automatic policy identification and mapping
- **Risk Assessment** - Migration complexity scoring (0-100)
- **Recommendations** - Intelligent migration guidance

### ⚙️ Migration Center
- **Real-time Execution** - Live migration progress tracking
- **Policy Preview** - Side-by-side Edge vs Apigee X comparison
- **Interactive Validation** - Edit policies before migration
- **Status Management** - Pause, resume, cancel migrations

### 🔐 Credential Management
- **Secure Storage** - Encrypted credential management
- **Multi-Environment** - Support for multiple Apigee environments
- **Validation** - Connection testing and verification

## 🛠️ API Documentation

### 📚 Interactive Documentation

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### 🔗 Core Endpoints

#### Proxy Management
```bash
# Upload proxy configuration
POST /api/upload-proxy
Content-Type: multipart/form-data

# Analyze uploaded proxy
POST /api/analyze-proxy/{proxy_id}

# Get all analyses
GET /api/analyses

# Get specific analysis
GET /api/analysis/{analysis_id}
```

#### Migration Management
```bash
# Start migration
POST /api/migrate
{
  "proxy_analysis_ids": ["uuid1", "uuid2"],
  "credentials_id": "cred-uuid",
  "auto_deploy": true
}

# Get migration status
GET /api/migration/{execution_id}

# Get all migrations
GET /api/migrations

# Cancel migration
DELETE /api/migration/{execution_id}
```

#### Credential Management
```bash
# Save credentials
POST /api/credentials
{
  "name": "Production",
  "edge_org": "my-org",
  "apigee_x_project": "my-project"
}

# Get credentials (safe)
GET /api/credentials

# Delete credentials
DELETE /api/credentials/{cred_id}
```

#### Analytics & Stats
```bash
# Dashboard statistics
GET /api/dashboard-stats

# Health check
GET /api/

# Service health
GET /api/health
```

## 🧪 Testing

### 🔬 Test Suite

```bash
# Run all tests
./test-docker.sh

# Backend unit tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
yarn test --coverage

# Integration tests
pytest tests/integration/ -v
```

### 🧪 Manual Testing

```bash
# Test file upload
curl -X POST http://localhost:8001/api/upload-proxy \
  -F "file=@sample-proxy.xml"

# Test analysis
curl -X POST http://localhost:8001/api/analyze-proxy/proxy-id

# Test dashboard stats
curl http://localhost:8001/api/dashboard-stats
```

## 📝 Development Guide

### 🔄 Making Changes

#### Frontend Development
```bash
# Start development server
cd frontend
yarn start

# Add new component
# 1. Create component in src/components/
# 2. Export from appropriate index
# 3. Import and use in parent components
# 4. Update tests
```

#### Backend Development
```bash
# Start development server
cd backend
uvicorn server:app --reload

# Add new endpoint
# 1. Define Pydantic models
# 2. Create route handler
# 3. Add to router
# 4. Update documentation
# 5. Add tests
```

## 🚨 Troubleshooting

### 🔍 Common Issues

#### Services Won't Start
```bash
# Check port conflicts
lsof -i :3000 :8001 :27017

# Check Docker status
docker-compose ps
docker-compose logs

# Restart services
docker-compose restart
```

#### Database Connection Issues
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Verify credentials from .env
echo $MONGO_ROOT_PASSWORD

# Test connection
docker-compose exec mongodb mongosh -u apigee_admin -p
```

#### API Key Issues
```bash
# Verify LLM key from .env
echo $OPENAI_API_KEY

# Check backend logs
docker-compose logs backend | grep -i "key\|auth\|error"
```

### 📞 Getting Help

1. **Check Logs**: `docker-compose logs [service-name]`
2. **Run Tests**: `./test-docker.sh`
3. **Verify Config**: Check `.env` file values
4. **Reset Environment**: `docker-compose down -v && ./setup.sh`
5. **Check Documentation**: Review API docs at `/docs`

---

**🎉 Happy Migrating! Transform your Apigee Edge APIs to Apigee X with confidence and intelligence.**
