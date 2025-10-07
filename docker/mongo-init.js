// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

print('Starting MongoDB initialization...');

// Switch to the application database
db = db.getSiblingDB('apigee_migration_db');

// Create application user with proper permissions
db.createUser({
  user: 'apigee_user',
  pwd: 'apigee_password_2024!',
  roles: [
    {
      role: 'readWrite',
      db: 'apigee_migration_db'
    }
  ]
});

// Create initial collections with proper indexing
print('Creating collections...');

// Proxy Files Collection
db.proxy_files.createIndex({ "id": 1 }, { unique: true });
db.proxy_files.createIndex({ "filename": 1 });
db.proxy_files.createIndex({ "uploaded_at": -1 });

// Proxy Analyses Collection
db.proxy_analyses.createIndex({ "id": 1 }, { unique: true });
db.proxy_analyses.createIndex({ "proxy_id": 1 });
db.proxy_analyses.createIndex({ "proxy_name": 1 });
db.proxy_analyses.createIndex({ "complexity_level": 1 });
db.proxy_analyses.createIndex({ "analyzed_at": -1 });

// Apigee Credentials Collection
db.apigee_credentials.createIndex({ "id": 1 }, { unique: true });
db.apigee_credentials.createIndex({ "name": 1 });
db.apigee_credentials.createIndex({ "edge_org": 1 });
db.apigee_credentials.createIndex({ "created_at": -1 });

// Migration Executions Collection
db.migration_executions.createIndex({ "id": 1 }, { unique: true });
db.migration_executions.createIndex({ "proxy_analysis_id": 1 });
db.migration_executions.createIndex({ "status": 1 });
db.migration_executions.createIndex({ "created_at": -1 });
db.migration_executions.createIndex({ "started_at": -1 });

// Create initial sample data for development
print('Creating sample data...');

// Insert sample proxy file
db.proxy_files.insertOne({
  id: "sample-proxy-001",
  filename: "oauth-sample-proxy.xml",
  content: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<APIProxy name="oauth-sample-proxy" revision="1">
    <DisplayName>OAuth Sample API</DisplayName>
    <Description>Sample Apigee proxy for migration testing</Description>
    <Policies>
        <Policy>OAuth2</Policy>
        <Policy>VerifyAPIKey</Policy>
        <Policy>SpikeArrest</Policy>
        <Policy>Quota</Policy>
        <Policy>JavaScript</Policy>
    </Policies>
</APIProxy>`,
  file_type: "xml",
  uploaded_at: new Date()
});

print('MongoDB initialization completed successfully!');
print('Database: apigee_migration_db');
print('Collections created: proxy_files, proxy_analyses, apigee_credentials, migration_executions');
print('Indexes created for optimal performance');
print('Sample data inserted for development');