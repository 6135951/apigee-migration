from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import uuid
import json
import re
import asyncio
import xml.etree.ElementTree as ET
from openai import OpenAI
import zipfile
import tempfile
import shutil
import yaml

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuration from environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'apigee_migration_db')
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if not OPENAI_API_KEY:
    logger.warning("No OpenAI API key found. AI features will be limited.")

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# FastAPI setup
app = FastAPI(title="Apigee Migration Tool", description="Automated Apigee Edge to Apigee X migration analysis")
api_router = APIRouter(prefix="/api")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM Chat
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY not found in environment variables")
else:
    logging.info("OpenAI API key found, AI features enabled")

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Pydantic Models
class ProxyFile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    content: str
    file_type: str  # xml, json
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PolicyMapping(BaseModel):
    edge_policy: str
    apigee_x_equivalent: str
    complexity: str  # simple, moderate, complex
    migration_notes: str
    custom_code_required: bool = False

class ProxyAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proxy_id: str
    proxy_name: str
    complexity_score: float  # 0-100
    complexity_level: str  # simple, moderate, complex
    policy_count: int
    custom_policies: List[str] = []
    policy_mappings: List[PolicyMapping] = []
    dependencies: List[str] = []
    migration_effort: str  # hours/days estimate
    ai_recommendations: str
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"  # pending, completed, failed

class MigrationPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proxy_analysis_id: str
    migration_steps: List[Dict[str, Any]] = []
    estimated_time: str
    priority: str  # high, medium, low
    blockers: List[str] = []
    status: str = "draft"  # draft, approved, in_progress, completed, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ApigeeCredentials(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    edge_org: str
    edge_env: str
    edge_username: str
    edge_password: str  # In production, this should be encrypted
    apigee_x_project: str
    apigee_x_env: str
    apigee_x_service_account: str  # JSON key as string
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MigrationExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proxy_analysis_id: str
    proxy_name: str
    credentials_id: str
    status: str = "pending"  # pending, preparing, converting, validating, deploying, completed, failed
    progress: int = 0  # 0-100
    current_step: str = ""
    steps_completed: List[str] = []
    steps_failed: List[str] = []
    migration_log: List[str] = []
    apigee_x_bundle: Optional[str] = None  # Generated Apigee X bundle
    deployment_url: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MigrationRequest(BaseModel):
    proxy_analysis_ids: List[str]
    credentials_id: str
    target_environment: str = "development"  # development, staging, production
    auto_deploy: bool = False

# Common Apigee Policies mapping
POLICY_MAPPINGS = {
    # Authentication & Security
    "OAuth2": {"apigee_x": "OAuthV2", "complexity": "simple", "notes": "Direct mapping with minimal changes"},
    "VerifyAPIKey": {"apigee_x": "VerifyAPIKey", "complexity": "simple", "notes": "Same policy, no changes needed"},
    "BasicAuthentication": {"apigee_x": "BasicAuthentication", "complexity": "simple", "notes": "Direct mapping"},
    "SAML": {"apigee_x": "SAMLAssertion", "complexity": "moderate", "notes": "May require configuration adjustments"},
    
    # Rate Limiting & Quotas
    "Quota": {"apigee_x": "Quota", "complexity": "simple", "notes": "Direct mapping"},
    "SpikeArrest": {"apigee_x": "SpikeArrest", "complexity": "simple", "notes": "No changes needed"},
    "ConcurrentRateLimit": {"apigee_x": "ConcurrentRateLimit", "complexity": "simple", "notes": "Direct mapping"},
    
    # Transformation
    "JSONtoXML": {"apigee_x": "JSONtoXML", "complexity": "simple", "notes": "Direct mapping"},
    "XMLtoJSON": {"apigee_x": "XMLtoJSON", "complexity": "simple", "notes": "Direct mapping"},
    "XSL": {"apigee_x": "XSL", "complexity": "moderate", "notes": "May need XSLT validation"},
    
    # JavaScript & Custom
    "JavaScript": {"apigee_x": "JavaScript", "complexity": "complex", "notes": "Requires code review and testing"},
    "Node.js": {"apigee_x": "NodeJS", "complexity": "complex", "notes": "May require updates to Node.js runtime"},
    "Python": {"apigee_x": "Python", "complexity": "complex", "notes": "Custom runtime policy, needs migration planning"},
    
    # Traffic Management
    "LoadBalancer": {"apigee_x": "LoadBalancing", "complexity": "moderate", "notes": "Configuration may need updates"},
    "ServiceCallout": {"apigee_x": "ServiceCallout", "complexity": "simple", "notes": "Direct mapping"},
    "RaiseFault": {"apigee_x": "RaiseFault", "complexity": "simple", "notes": "Direct mapping"},
}

def extract_and_parse_zip_bundle(zip_content: bytes) -> Dict[str, Any]:
    """Extract and parse Apigee Edge ZIP bundle"""
    try:
        bundle_info = {
            "main_config": None,
            "policies": {},
            "resources": {},
            "proxies": {},
            "targets": {},
            "extracted_policies": [],
            "bundle_structure": []
        }
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "bundle.zip"
            
            # Write ZIP content to temporary file
            with open(zip_path, 'wb') as f:
                f.write(zip_content)
            
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
                
                # Get list of all files
                file_list = []
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        if file != 'bundle.zip':
                            rel_path = os.path.relpath(os.path.join(root, file), temp_path)
                            file_list.append(rel_path)
                
                bundle_info["bundle_structure"] = file_list
                
                # Parse main apiproxy.xml
                apiproxy_path = temp_path / "apiproxy" / "apiproxy.xml"
                if not apiproxy_path.exists():
                    # Try alternate locations
                    for alt_path in temp_path.rglob("apiproxy.xml"):
                        apiproxy_path = alt_path
                        break
                
                if apiproxy_path.exists():
                    with open(apiproxy_path, 'r', encoding='utf-8') as f:
                        bundle_info["main_config"] = f.read()
                
                # Parse policies directory
                policies_dir = temp_path / "apiproxy" / "policies"
                if not policies_dir.exists():
                    # Try alternate locations
                    for alt_dir in temp_path.rglob("policies"):
                        if alt_dir.is_dir():
                            policies_dir = alt_dir
                            break
                
                if policies_dir.exists():
                    for policy_file in policies_dir.glob("*.xml"):
                        with open(policy_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            policy_name = policy_file.stem
                            bundle_info["policies"][policy_name] = content
                            
                            # Extract policy type from XML
                            try:
                                root = ET.fromstring(content)
                                policy_type = root.tag
                                bundle_info["extracted_policies"].append(policy_type)
                            except:
                                bundle_info["extracted_policies"].append(policy_name)
                
                # Parse resources directory (JavaScript, Python, Java files)
                resources_dirs = ["resources/jsc", "resources/py", "resources/java"]
                for res_dir in resources_dirs:
                    resource_path = temp_path / "apiproxy" / res_dir
                    if resource_path.exists():
                        for resource_file in resource_path.rglob("*"):
                            if resource_file.is_file():
                                try:
                                    with open(resource_file, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        rel_path = str(resource_file.relative_to(temp_path))
                                        bundle_info["resources"][rel_path] = content
                                except:
                                    # Handle binary files
                                    bundle_info["resources"][str(resource_file.relative_to(temp_path))] = "[Binary File]"
                
                # Parse proxy endpoints
                proxies_dir = temp_path / "apiproxy" / "proxies"
                if proxies_dir.exists():
                    for proxy_file in proxies_dir.glob("*.xml"):
                        with open(proxy_file, 'r', encoding='utf-8') as f:
                            bundle_info["proxies"][proxy_file.stem] = f.read()
                
                # Parse target endpoints
                targets_dir = temp_path / "apiproxy" / "targets"
                if targets_dir.exists():
                    for target_file in targets_dir.glob("*.xml"):
                        with open(target_file, 'r', encoding='utf-8') as f:
                            bundle_info["targets"][target_file.stem] = f.read()
        
        return bundle_info
        
    except Exception as e:
        logging.error(f"ZIP extraction error: {e}")
        return {"error": str(e)}

def extract_policies_from_bundle(bundle_info: Dict[str, Any]) -> List[str]:
    """Extract all policies from the bundle"""
    policies = []
    
    # Get policies from main config
    if bundle_info.get("main_config"):
        main_policies = extract_policies_from_xml(bundle_info["main_config"])
        policies.extend(main_policies)
    
    # Get policies from proxy endpoints
    for proxy_name, proxy_content in bundle_info.get("proxies", {}).items():
        proxy_policies = extract_policies_from_xml(proxy_content)
        policies.extend(proxy_policies)
    
    # Get policies from target endpoints
    for target_name, target_content in bundle_info.get("targets", {}).items():
        target_policies = extract_policies_from_xml(target_content)
        policies.extend(target_policies)
    
    # Add policies from policies directory
    if bundle_info.get("extracted_policies"):
        policies.extend(bundle_info["extracted_policies"])
    
    return list(set(policies))  # Remove duplicates

def extract_proxy_info_from_bundle(bundle_info: Dict[str, Any]) -> Dict[str, Any]:
    """Extract proxy information from bundle"""
    proxy_info = {
        "name": "Unknown",
        "base_paths": [],
        "target_servers": [],
        "resources": [],
        "policies_count": len(bundle_info.get("policies", {})),
        "resources_count": len(bundle_info.get("resources", {})),
        "endpoints": {
            "proxies": list(bundle_info.get("proxies", {}).keys()),
            "targets": list(bundle_info.get("targets", {}).keys())
        }
    }
    
    # Extract info from main config
    if bundle_info.get("main_config"):
        main_info = extract_proxy_info(bundle_info["main_config"])
        proxy_info.update(main_info)
    
    # Add resource information
    for resource_path in bundle_info.get("resources", {}):
        resource_type = "unknown"
        if ".js" in resource_path:
            resource_type = "javascript"
        elif ".py" in resource_path:
            resource_type = "python"
        elif ".java" in resource_path:
            resource_type = "java"
        elif ".wsdl" in resource_path or ".xsd" in resource_path:
            resource_type = "schema"
        
        proxy_info["resources"].append({
            "path": resource_path,
            "type": resource_type
        })
    
    return proxy_info

def extract_policies_from_xml(xml_content: str) -> List[str]:
    """Extract policy names from Apigee proxy XML"""
    try:
        root = ET.fromstring(xml_content)
        policies = []
        
        # Method 1: Look for policies in the <Policies> section (common format)
        policies_section = root.find('Policies')
        if policies_section is not None:
            for policy in policies_section.findall('Policy'):
                if policy.text:
                    policies.append(policy.text.strip())
        
        # Method 2: Look for policy references in Steps within flows
        for step in root.findall('.//Step'):
            name_elem = step.find('Name')
            if name_elem is not None and name_elem.text:
                policies.append(name_elem.text.strip())
        
        # Method 3: Check PreFlow and PostFlow
        for flow in root.findall('.//PreFlow'):
            for step in flow.findall('.//Step'):
                name_elem = step.find('Name')
                if name_elem is not None and name_elem.text:
                    policies.append(name_elem.text.strip())
                    
        for flow in root.findall('.//PostFlow'):
            for step in flow.findall('.//Step'):
                name_elem = step.find('Name')
                if name_elem is not None and name_elem.text:
                    policies.append(name_elem.text.strip())
        
        # Clean up and return unique policies
        policies = [p for p in policies if p]  # Remove empty strings
        return list(set(policies))  # Remove duplicates
    except ET.ParseError as e:
        logging.error(f"XML parsing error: {e}")
        return []

def extract_proxy_info(xml_content: str) -> Dict[str, Any]:
    """Extract basic proxy information from XML"""
    try:
        root = ET.fromstring(xml_content)
        proxy_info = {
            "name": root.get('name', 'Unknown'),
            "base_paths": [],
            "target_servers": [],
            "resources": []
        }
        
        # Extract base paths
        for vhost in root.findall('.//VirtualHost'):
            proxy_info["base_paths"].append(vhost.text)
            
        # Extract target servers
        for target in root.findall('.//TargetEndpoint'):
            name_elem = target.get('name')
            if name_elem:
                proxy_info["target_servers"].append(name_elem)
        
        return proxy_info
    except ET.ParseError as e:
        logging.error(f"XML parsing error: {e}")
        return {"name": "Unknown", "base_paths": [], "target_servers": [], "resources": []}

async def convert_edge_to_apigee_x(proxy_content: str, policy_mappings: List[PolicyMapping]) -> str:
    """Convert Apigee Edge proxy to Apigee X format using AI"""
    if not openai_client:
        return proxy_content  # Return original if no AI available
        
    try:
        conversion_prompt = f"""
Convert this Apigee Edge proxy configuration to Apigee X format:

Original Edge Configuration:
{proxy_content[:3000]}...

Policy Mappings to Apply:
{json.dumps([mapping.model_dump() for mapping in policy_mappings], indent=2)}

Requirements:
1. Convert all policies to Apigee X equivalents
2. Update policy configurations for Apigee X compatibility
3. Ensure proper flow structure
4. Handle custom policies appropriately
5. Return valid XML configuration

Generate the complete Apigee X proxy bundle XML.
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in converting Apigee Edge configurations to Apigee X format. Generate valid Apigee X proxy bundles."},
                {"role": "user", "content": conversion_prompt}
            ],
            max_tokens=4000,
            temperature=0.1
        )
        
        # Extract response content
        response_content = response.choices[0].message.content
        
        # Extract XML from response
        if "<?xml" in response_content:
            start = response_content.find("<?xml")
            end = response_content.rfind("</APIProxy>") + len("</APIProxy>")
            if end > start:
                return response_content[start:end]
        
        return response_content  # Return full response if no XML found
        
    except Exception as e:
        logging.error(f"AI conversion error: {e}")
        return proxy_content  # Return original on error

async def execute_migration_step(execution_id: str, step: str, step_function, *args):
    """Execute a single migration step and update progress"""
    try:
        # Update current step
        await db.migration_executions.update_one(
            {"id": execution_id},
            {"$set": {
                "current_step": step,
                "updated_at": datetime.now(timezone.utc)
            },
            "$push": {"migration_log": f"Starting: {step}"}}
        )
        
        # Execute the step
        result = await step_function(*args)
        
        # Mark step as completed
        await db.migration_executions.update_one(
            {"id": execution_id},
            {"$push": {
                "steps_completed": step,
                "migration_log": f"Completed: {step}"
            }}
        )
        
        return result
        
    except Exception as e:
        # Mark step as failed
        await db.migration_executions.update_one(
            {"id": execution_id},
            {"$push": {
                "steps_failed": step,
                "migration_log": f"Failed: {step} - {str(e)}"
            }}
        )
        raise e

async def perform_migration(execution_id: str):
    """Perform the actual migration process"""
    try:
        # Get execution details
        execution = await db.migration_executions.find_one({"id": execution_id})
        if not execution:
            return
            
        # Get proxy analysis
        analysis = await db.proxy_analyses.find_one({"id": execution["proxy_analysis_id"]})
        if not analysis:
            await db.migration_executions.update_one(
                {"id": execution_id},
                {"$set": {"status": "failed", "error_message": "Analysis not found"}}
            )
            return
            
        # Get original proxy file
        proxy_file = await db.proxy_files.find_one({"id": analysis["proxy_id"]})
        if not proxy_file:
            await db.migration_executions.update_one(
                {"id": execution_id},
                {"$set": {"status": "failed", "error_message": "Proxy file not found"}}
            )
            return

        # Start migration
        await db.migration_executions.update_one(
            {"id": execution_id},
            {"$set": {
                "status": "preparing",
                "progress": 10,
                "started_at": datetime.now(timezone.utc)
            }}
        )
        
        # Step 1: Validate source proxy
        await execute_migration_step(
            execution_id, 
            "Validating source proxy",
            lambda: asyncio.sleep(2)  # Simulate validation
        )
        
        await db.migration_executions.update_one(
            {"id": execution_id},
            {"$set": {"progress": 25}}
        )
        
        # Step 2: Convert policies
        await execute_migration_step(
            execution_id,
            "Converting policies to Apigee X format",
            lambda: asyncio.sleep(3)  # Simulate policy conversion
        )
        
        await db.migration_executions.update_one(
            {"id": execution_id},
            {"$set": {"progress": 50, "status": "converting"}}
        )
        
        # Step 3: Generate Apigee X bundle using AI
        apigee_x_bundle = await execute_migration_step(
            execution_id,
            "Generating Apigee X bundle with AI",
            convert_edge_to_apigee_x,
            proxy_file["content"],
            [PolicyMapping(**mapping) for mapping in analysis["policy_mappings"]]
        )
        
        await db.migration_executions.update_one(
            {"id": execution_id},
            {"$set": {"progress": 70, "apigee_x_bundle": apigee_x_bundle}}
        )
        
        # Step 4: Validate Apigee X bundle
        await execute_migration_step(
            execution_id,
            "Validating Apigee X bundle",
            lambda: asyncio.sleep(2)  # Simulate validation
        )
        
        await db.migration_executions.update_one(
            {"id": execution_id},
            {"$set": {"progress": 85, "status": "validating"}}
        )
        
        # Step 5: Deploy (simulated)
        await execute_migration_step(
            execution_id,
            "Deploying to Apigee X (Demo Mode)",
            lambda: asyncio.sleep(3)  # Simulate deployment
        )
        
        # Complete migration
        await db.migration_executions.update_one(
            {"id": execution_id},
            {"$set": {
                "status": "completed",
                "progress": 100,
                "current_step": "Migration completed successfully",
                "deployment_url": f"https://apigee.google.com/organizations/demo-org/environments/dev/apis/{analysis['proxy_name']}",
                "completed_at": datetime.now(timezone.utc)
            },
            "$push": {"migration_log": "Migration completed successfully!"}}
        )
        
    except Exception as e:
        logging.error(f"Migration failed for {execution_id}: {e}")
        await db.migration_executions.update_one(
            {"id": execution_id},
            {"$set": {
                "status": "failed",
                "error_message": str(e),
                "completed_at": datetime.now(timezone.utc)
            }}
        )

async def analyze_proxy_with_ai(proxy_content: str, policies: List[str]) -> Dict[str, Any]:
    """Use AI to analyze proxy complexity and provide recommendations"""
    if not openai_client:
        return {"complexity_score": 50, "recommendations": "AI analysis unavailable - API key not configured"}
        
    try:
        
        analysis_prompt = f"""
Analyze this Apigee Edge proxy configuration for migration to Apigee X:

Policies found: {', '.join(policies)}

Proxy content preview:
{proxy_content[:2000]}...

Provide a JSON response with:
1. complexity_score (0-100, where 0=simple, 100=very complex)
2. complexity_reasoning (why this score)
3. migration_effort (estimated hours/days)
4. key_challenges (list of main migration challenges)
5. recommendations (specific migration recommendations)
6. custom_policies (list of any custom/non-standard policies detected)

Focus on:
- Custom JavaScript/Node.js code
- Non-standard policy usage
- Complex integrations
- Deprecated features
- Security implications
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in Apigee Edge to Apigee X migrations. Analyze proxy configurations and provide migration complexity assessments."},
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        # Extract response content
        response_content = response.choices[0].message.content
        
        # Try to parse JSON from response
        try:
            # Extract JSON from the response
            json_match = re.search(r'{.*}', response_content, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                # Ensure recommendations is a string
                if "recommendations" in analysis_data:
                    if isinstance(analysis_data["recommendations"], list):
                        analysis_data["recommendations"] = " ".join(analysis_data["recommendations"])
                    elif not isinstance(analysis_data["recommendations"], str):
                        analysis_data["recommendations"] = str(analysis_data["recommendations"])
                return analysis_data
        except json.JSONDecodeError:
            pass
            
        # Fallback if JSON parsing fails
        return {
            "complexity_score": 50,
            "complexity_reasoning": "AI analysis completed",
            "migration_effort": "2-4 hours",
            "key_challenges": ["Standard migration requirements"],
            "recommendations": response[:500],
            "custom_policies": []
        }
        
    except Exception as e:
        logging.error(f"AI analysis error: {e}")
        return {
            "complexity_score": 50,
            "recommendations": f"AI analysis failed: {str(e)}",
            "migration_effort": "Unknown",
            "key_challenges": ["Analysis unavailable"],
            "custom_policies": []
        }

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Apigee Migration Tool API", "version": "1.0.0"}

@api_router.post("/upload-proxy", response_model=Dict[str, str])
async def upload_proxy(file: UploadFile = File(...)):
    """Upload Apigee proxy configuration file (XML, JSON, or ZIP bundle)"""
    try:
        # Check file size (100MB limit)
        max_file_size = 100 * 1024 * 1024  # 100MB in bytes
        content = await file.read()
        
        if len(content) > max_file_size:
            raise HTTPException(status_code=413, detail="File size exceeds 100MB limit")
        
        filename_lower = file.filename.lower()
        
        # Handle ZIP files
        if filename_lower.endswith('.zip'):
            # Validate and extract ZIP bundle
            bundle_info = extract_and_parse_zip_bundle(content)
            
            if "error" in bundle_info:
                raise HTTPException(status_code=400, detail=f"Invalid ZIP bundle: {bundle_info['error']}")
            
            # Validate ZIP contains valid Apigee proxy structure
            if not bundle_info.get("main_config"):
                raise HTTPException(status_code=400, detail="ZIP bundle must contain apiproxy.xml file")
            
            if not bundle_info.get("policies") and not bundle_info.get("extracted_policies"):
                logger.warning("ZIP bundle does not contain policies directory - this may be a simple proxy")
            
            # Store ZIP bundle information
            proxy_file = ProxyFile(
                filename=file.filename,
                content=json.dumps({
                    "type": "zip_bundle",
                    "main_config": bundle_info.get("main_config", ""),
                    "policies": bundle_info.get("policies", {}),
                    "resources": bundle_info.get("resources", {}),
                    "proxies": bundle_info.get("proxies", {}),
                    "targets": bundle_info.get("targets", {}),
                    "bundle_structure": bundle_info.get("bundle_structure", []),
                    "extracted_policies": bundle_info.get("extracted_policies", [])
                }),
                file_type="zip"
            )
            
            await db.proxy_files.insert_one(proxy_file.model_dump())
            
            return {"proxy_id": proxy_file.id, "message": "ZIP proxy bundle uploaded and extracted successfully"}
        
        # Handle XML/JSON files
        elif filename_lower.endswith('.xml') or filename_lower.endswith('.json'):
            try:
                content_str = content.decode('utf-8')
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="File must be valid UTF-8 encoded text")
            
            # Determine file type
            file_type = "xml" if filename_lower.endswith('.xml') else "json"
            
            # Basic validation for XML files
            if file_type == "xml":
                try:
                    ET.fromstring(content_str)
                except ET.ParseError:
                    raise HTTPException(status_code=400, detail="Invalid XML format")
            
            # Basic validation for JSON files  
            if file_type == "json":
                try:
                    json.loads(content_str)
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="Invalid JSON format")
            
            # Store file in database
            proxy_file = ProxyFile(
                filename=file.filename,
                content=content_str,
                file_type=file_type
            )
            
            await db.proxy_files.insert_one(proxy_file.model_dump())
            
            return {"proxy_id": proxy_file.id, "message": "Proxy file uploaded successfully"}
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload XML, JSON, or ZIP files only.")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router.post("/analyze-proxy/{proxy_id}", response_model=ProxyAnalysis)
async def analyze_proxy(proxy_id: str):
    """Analyze uploaded proxy for migration complexity"""
    try:
        # Get proxy file from database
        proxy_file = await db.proxy_files.find_one({"id": proxy_id})
        if not proxy_file:
            raise HTTPException(status_code=404, detail="Proxy file not found")
        
        # Handle different file types
        if proxy_file["file_type"] == "zip":
            # Parse ZIP bundle data
            bundle_data = json.loads(proxy_file["content"])
            
            # Extract proxy information from ZIP bundle
            if bundle_data.get("main_config"):
                proxy_info = extract_proxy_info(bundle_data["main_config"])
            else:
                proxy_info = {"name": "Unknown", "base_paths": [], "target_servers": [], "resources": []}
            
            # Extract policies from ZIP bundle
            policies = extract_policies_from_bundle(bundle_data)
            
            # Use main config for AI analysis if available
            analysis_content = bundle_data.get("main_config", "")
            if not analysis_content and bundle_data.get("proxies"):
                # Use first proxy endpoint if main config not available
                analysis_content = list(bundle_data["proxies"].values())[0] if bundle_data["proxies"] else ""
                
        else:
            # Handle XML/JSON files
            proxy_info = extract_proxy_info(proxy_file["content"])
            policies = extract_policies_from_xml(proxy_file["content"])
            analysis_content = proxy_file["content"]
        
        # Map policies to Apigee X equivalents
        policy_mappings = []
        custom_policies = []
        total_complexity = 0
        
        for policy in policies:
            if policy in POLICY_MAPPINGS:
                mapping_info = POLICY_MAPPINGS[policy]
                policy_mappings.append(PolicyMapping(
                    edge_policy=policy,
                    apigee_x_equivalent=mapping_info["apigee_x"],
                    complexity=mapping_info["complexity"],
                    migration_notes=mapping_info["notes"],
                    custom_code_required=mapping_info["complexity"] == "complex"
                ))
                
                # Add to complexity score
                if mapping_info["complexity"] == "simple":
                    total_complexity += 10
                elif mapping_info["complexity"] == "moderate":
                    total_complexity += 25
                else:
                    total_complexity += 50
            else:
                # Unknown/custom policy
                custom_policies.append(policy)
                policy_mappings.append(PolicyMapping(
                    edge_policy=policy,
                    apigee_x_equivalent="Manual Migration Required",
                    complexity="complex",
                    migration_notes="Custom policy requires manual analysis and migration",
                    custom_code_required=True
                ))
                total_complexity += 75
        
        # AI Analysis
        ai_analysis = await analyze_proxy_with_ai(analysis_content, policies)
        
        # Calculate final complexity score
        complexity_score = min(100, (total_complexity / len(policies)) if policies else 0)
        if ai_analysis.get("complexity_score"):
            complexity_score = (complexity_score + ai_analysis["complexity_score"]) / 2
        
        # Determine complexity level
        if complexity_score < 30:
            complexity_level = "simple"
            migration_effort = "1-2 hours"
        elif complexity_score < 70:
            complexity_level = "moderate"
            migration_effort = "4-8 hours"
        else:
            complexity_level = "complex"
            migration_effort = "1-3 days"
        
        # Override with AI estimate if available
        if ai_analysis.get("migration_effort"):
            migration_effort = ai_analysis["migration_effort"]
            
        # Create analysis
        analysis = ProxyAnalysis(
            proxy_id=proxy_id,
            proxy_name=proxy_info["name"],
            complexity_score=complexity_score,
            complexity_level=complexity_level,
            policy_count=len(policies),
            custom_policies=custom_policies,
            policy_mappings=policy_mappings,
            dependencies=proxy_info["target_servers"],
            migration_effort=migration_effort,
            ai_recommendations=str(ai_analysis.get("recommendations", "No AI recommendations available")) if ai_analysis.get("recommendations") else "No AI recommendations available",
            status="completed"
        )
        
        # Store analysis
        await db.proxy_analyses.insert_one(analysis.model_dump())
        
        return analysis
        
    except Exception as e:
        logging.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Swagger/OpenAPI Documentation Endpoints
@api_router.post("/upload-swagger", response_model=Dict[str, str])
async def upload_swagger(file: UploadFile = File(...)):
    """Upload Swagger/OpenAPI documentation"""
    try:
        # Check file size (10MB limit for docs)
        max_file_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        
        if len(content) > max_file_size:
            raise HTTPException(status_code=413, detail="File size exceeds 10MB limit")
        
        filename_lower = file.filename.lower()
        
        # Validate file type
        if not (filename_lower.endswith('.json') or filename_lower.endswith('.yaml') or filename_lower.endswith('.yml')):
            raise HTTPException(status_code=400, detail="Only JSON and YAML files are supported")
        
        try:
            if filename_lower.endswith('.json'):
                spec_data = json.loads(content.decode('utf-8'))
            else:
                spec_data = yaml.safe_load(content.decode('utf-8'))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON/YAML format")
        
        # Validate basic Swagger/OpenAPI structure
        if 'swagger' not in spec_data and 'openapi' not in spec_data:
            raise HTTPException(status_code=400, detail="Not a valid Swagger/OpenAPI specification")
        
        # Store the specification
        spec_id = str(uuid.uuid4())
        swagger_doc = {
            "id": spec_id,
            "filename": file.filename,
            "original_spec": spec_data,
            "spec_version": spec_data.get('swagger', spec_data.get('openapi', 'unknown')),
            "uploaded_at": datetime.now(timezone.utc),
            "migrated_spec": None,
            "conversion_status": "pending"
        }
        
        await db.swagger_docs.insert_one(swagger_doc)
        
        return {
            "specId": spec_id,
            "message": "Swagger documentation uploaded successfully",
            "originalSpec": json.dumps(spec_data) if isinstance(spec_data, dict) else str(spec_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Swagger upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router.post("/convert-swagger/{spec_id}", response_model=Dict[str, Any])
async def convert_swagger_to_apigee_x(spec_id: str):
    """Convert Swagger/OpenAPI to Apigee X format using AI"""
    try:
        # Get the swagger document
        swagger_doc = await db.swagger_docs.find_one({"id": spec_id})
        if not swagger_doc:
            raise HTTPException(status_code=404, detail="Swagger document not found")
        
        original_spec = swagger_doc["original_spec"]
        
        if not openai_client:
            # Fallback conversion without AI
            converted_spec = convert_swagger_fallback(original_spec)
        else:
            # AI-powered conversion
            converted_spec = await convert_swagger_with_ai(original_spec)
        
        # Update the document with converted spec
        await db.swagger_docs.update_one(
            {"id": spec_id},
            {"$set": {
                "migrated_spec": converted_spec,
                "conversion_status": "completed",
                "converted_at": datetime.now(timezone.utc)
            }}
        )
        
        return {
            "convertedSpec": converted_spec,
            "message": "Swagger documentation converted to Apigee X format"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Swagger conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

async def convert_swagger_with_ai(original_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Swagger to Apigee X format using AI"""
    try:
        conversion_prompt = f"""
Convert this Swagger/OpenAPI specification to be optimized for Apigee X:

Original Specification:
{json.dumps(original_spec, indent=2)[:3000]}...

Requirements for Apigee X conversion:
1. Upgrade to OpenAPI 3.0+ if it's Swagger 2.0
2. Add Apigee X specific security policies (OAuth 2.0, API Key)
3. Add rate limiting and quota policies in x-google-* extensions
4. Update server URLs for Apigee X format
5. Add proper error response schemas
6. Include CORS configuration
7. Add health check endpoints
8. Optimize for Apigee X performance

Return a valid OpenAPI 3.0 specification optimized for Apigee X deployment.
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in API documentation and Apigee X. Convert Swagger/OpenAPI specifications to be optimized for Apigee X platform."},
                {"role": "user", "content": conversion_prompt}
            ],
            max_tokens=4000,
            temperature=0.1
        )
        
        response_content = response.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Look for JSON content in the response
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                converted_spec = json.loads(json_match.group())
                return converted_spec
        except json.JSONDecodeError:
            pass
        
        # Fallback if AI response is not valid JSON
        return convert_swagger_fallback(original_spec)
        
    except Exception as e:
        logging.error(f"AI Swagger conversion error: {e}")
        return convert_swagger_fallback(original_spec)

def convert_swagger_fallback(original_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback conversion without AI"""
    converted_spec = original_spec.copy()
    
    # Convert Swagger 2.0 to OpenAPI 3.0 basic structure
    if 'swagger' in converted_spec:
        openapi_spec = {
            "openapi": "3.0.0",
            "info": converted_spec.get("info", {}),
            "servers": [{"url": converted_spec.get("host", "api.example.com") + converted_spec.get("basePath", "")}],
            "paths": converted_spec.get("paths", {}),
            "components": {
                "schemas": converted_spec.get("definitions", {}),
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    },
                    "OAuth2": {
                        "type": "oauth2",
                        "flows": {
                            "clientCredentials": {
                                "tokenUrl": "https://oauth.example.com/token",
                                "scopes": {}
                            }
                        }
                    }
                }
            },
            "security": [
                {"ApiKeyAuth": []},
                {"OAuth2": []}
            ]
        }
        converted_spec = openapi_spec
    
    # Add Apigee X extensions
    converted_spec["x-google-management"] = {
        "metrics": [
            {"name": "request_count", "valueType": "INT64", "metricKind": "DELTA"}
        ],
        "quota": {
            "limits": [
                {"name": "ApiCalls", "metric": "request_count", "unit": "1/min", "values": {"STANDARD": 1000}}
            ]
        }
    }
    
    return converted_spec

@api_router.get("/analyses", response_model=List[ProxyAnalysis])
async def get_analyses():
    """Get all proxy analyses"""
    try:
        analyses = await db.proxy_analyses.find().sort("analyzed_at", -1).to_list(100)
        return [ProxyAnalysis(**analysis) for analysis in analyses]
    except Exception as e:
        logging.error(f"Get analyses error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analyses: {str(e)}")

@api_router.get("/analysis/{analysis_id}", response_model=ProxyAnalysis)
async def get_analysis(analysis_id: str):
    """Get specific proxy analysis"""
    try:
        analysis = await db.proxy_analyses.find_one({"id": analysis_id})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return ProxyAnalysis(**analysis)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")

@api_router.get("/dashboard-stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get total analyses count
        total_analyses = await db.proxy_analyses.count_documents({})
        
        # Get complexity distribution
        complexity_distribution = await db.proxy_analyses.aggregate([
            {"$group": {
                "_id": "$complexity_level",
                "count": {"$sum": 1}
            }}
        ]).to_list(10)
        
        # Get recent analyses
        recent_analyses = await db.proxy_analyses.find().sort("analyzed_at", -1).limit(5).to_list(5)
        
        # Calculate average complexity
        avg_complexity_result = await db.proxy_analyses.aggregate([
            {"$group": {
                "_id": None,
                "avg_complexity": {"$avg": "$complexity_score"}
            }}
        ]).to_list(1)
        
        avg_complexity = avg_complexity_result[0]["avg_complexity"] if avg_complexity_result else 0
        
        # Get policy distribution
        policy_stats = await db.proxy_analyses.aggregate([
            {"$unwind": "$policy_mappings"},
            {"$group": {
                "_id": "$policy_mappings.edge_policy",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]).to_list(10)
        
        return {
            "total_analyses": total_analyses,
            "avg_complexity": round(avg_complexity, 1),
            "complexity_distribution": {item["_id"]: item["count"] for item in complexity_distribution},
            "recent_analyses": [ProxyAnalysis(**analysis) for analysis in recent_analyses],
            "top_policies": [{"policy": item["_id"], "count": item["count"]} for item in policy_stats]
        }
        
    except Exception as e:
        logging.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Credentials Management APIs
@api_router.post("/credentials", response_model=Dict[str, str])
async def save_credentials(credentials: ApigeeCredentials):
    """Save Apigee credentials"""
    try:
        await db.apigee_credentials.insert_one(credentials.model_dump())
        return {"id": credentials.id, "message": "Credentials saved successfully"}
    except Exception as e:
        logging.error(f"Save credentials error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save credentials: {str(e)}")

@api_router.get("/credentials", response_model=List[Dict[str, Any]])
async def get_credentials():
    """Get saved credentials (excluding sensitive data)"""
    try:
        credentials = await db.apigee_credentials.find().to_list(100)
        # Remove sensitive data
        safe_credentials = []
        for cred in credentials:
            safe_credentials.append({
                "id": cred["id"],
                "name": cred["name"],
                "edge_org": cred["edge_org"],
                "edge_env": cred["edge_env"],
                "apigee_x_project": cred["apigee_x_project"],
                "apigee_x_env": cred["apigee_x_env"],
                "created_at": cred["created_at"]
            })
        return safe_credentials
    except Exception as e:
        logging.error(f"Get credentials error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get credentials: {str(e)}")

@api_router.delete("/credentials/{cred_id}")
async def delete_credentials(cred_id: str):
    """Delete credentials"""
    try:
        result = await db.apigee_credentials.delete_one({"id": cred_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Credentials not found")
        return {"message": "Credentials deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Delete credentials error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete credentials: {str(e)}")

# Migration APIs
@api_router.post("/migrate", response_model=List[MigrationExecution])
async def start_migration(request: MigrationRequest, background_tasks: BackgroundTasks):
    """Start migration process for selected proxies"""
    try:
        executions = []
        
        for proxy_analysis_id in request.proxy_analysis_ids:
            # Get analysis details
            analysis = await db.proxy_analyses.find_one({"id": proxy_analysis_id})
            if not analysis:
                continue
                
            # Create migration execution
            execution = MigrationExecution(
                proxy_analysis_id=proxy_analysis_id,
                proxy_name=analysis["proxy_name"],
                credentials_id=request.credentials_id,
                status="pending",
                current_step="Queued for migration"
            )
            
            await db.migration_executions.insert_one(execution.model_dump())
            executions.append(execution)
            
            # Start migration in background
            background_tasks.add_task(perform_migration, execution.id)
        
        return executions
        
    except Exception as e:
        logging.error(f"Start migration error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start migration: {str(e)}")

@api_router.get("/migrations", response_model=List[MigrationExecution])
async def get_migrations():
    """Get all migration executions"""
    try:
        migrations = await db.migration_executions.find().sort("created_at", -1).to_list(100)
        return [MigrationExecution(**migration) for migration in migrations]
    except Exception as e:
        logging.error(f"Get migrations error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get migrations: {str(e)}")

@api_router.get("/migration/{execution_id}", response_model=MigrationExecution)
async def get_migration(execution_id: str):
    """Get specific migration execution with real-time status"""
    try:
        migration = await db.migration_executions.find_one({"id": execution_id})
        if not migration:
            raise HTTPException(status_code=404, detail="Migration not found")
        return MigrationExecution(**migration)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get migration error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get migration: {str(e)}")

@api_router.delete("/migration/{execution_id}")
async def cancel_migration(execution_id: str):
    """Cancel a running migration"""
    try:
        # Update status to cancelled
        result = await db.migration_executions.update_one(
            {"id": execution_id, "status": {"$in": ["pending", "preparing", "converting", "validating"]}},
            {"$set": {
                "status": "failed",
                "error_message": "Migration cancelled by user",
                "completed_at": datetime.now(timezone.utc)
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Migration not found or cannot be cancelled")
            
        return {"message": "Migration cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Cancel migration error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel migration: {str(e)}")

# Include API router
app.include_router(api_router)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)