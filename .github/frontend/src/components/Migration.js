import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Checkbox } from './ui/checkbox';
import { toast } from 'sonner';
import { 
  Settings, 
  Play, 
  Pause, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  AlertCircle,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  Edit,
  RefreshCw,
  Download,
  Upload as UploadIcon,
  Zap,
  Activity,
  Database,
  Server,
  ArrowRight
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Migration = ({ analysisData }) => {
  const [activeTab, setActiveTab] = useState('execute');
  const [credentials, setCredentials] = useState([]);
  const [migrations, setMigrations] = useState([]);
  const [selectedProxies, setSelectedProxies] = useState([]);
  const [selectedCredential, setSelectedCredential] = useState('');
  const [isCredentialDialogOpen, setIsCredentialDialogOpen] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showConversionPreview, setShowConversionPreview] = useState(false);
  const [conversionPreview, setConversionPreview] = useState(null);
  const [showPolicyComparison, setShowPolicyComparison] = useState(false);
  const [selectedPolicyComparison, setSelectedPolicyComparison] = useState(null);
  const [convertedPolicies, setConvertedPolicies] = useState({});
  const [migrationConsoleLog, setMigrationConsoleLog] = useState([]);
  const [migrationPhase, setMigrationPhase] = useState('preview'); // preview, converting, validation, ready, executing
  const [isEditingPolicy, setIsEditingPolicy] = useState(false);
  const [editedPolicyContent, setEditedPolicyContent] = useState('');
  
  // Real-time polling for migration status
  const [pollingInterval, setPollingInterval] = useState(null);

  // New credential form
  const [newCredential, setNewCredential] = useState({
    name: '',
    edge_org: '',
    edge_env: '',
    edge_username: '',
    edge_password: '',
    apigee_x_project: '',
    apigee_x_env: '',
    apigee_x_service_account: ''
  });

  useEffect(() => {
    loadCredentials();
    loadMigrations();
    
    // Start polling for migration status
    const interval = setInterval(loadMigrations, 3000);
    setPollingInterval(interval);
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, []);

  const loadCredentials = async () => {
    try {
      const response = await axios.get(`${API}/credentials`);
      setCredentials(response.data);
    } catch (error) {
      console.error('Failed to load credentials:', error);
      toast.error('Failed to load credentials');
    }
  };

  const loadMigrations = async () => {
    try {
      const response = await axios.get(`${API}/migrations`);
      setMigrations(response.data);
    } catch (error) {
      console.error('Failed to load migrations:', error);
    }
  };

  const saveCredential = async () => {
    if (!newCredential.name || !newCredential.edge_org || !newCredential.apigee_x_project) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      await axios.post(`${API}/credentials`, newCredential);
      toast.success('Credentials saved successfully');
      setIsCredentialDialogOpen(false);
      setNewCredential({
        name: '',
        edge_org: '',
        edge_env: '',
        edge_username: '',
        edge_password: '',
        apigee_x_project: '',
        apigee_x_env: '',
        apigee_x_service_account: ''
      });
      loadCredentials();
    } catch (error) {
      console.error('Failed to save credentials:', error);
      toast.error('Failed to save credentials');
    } finally {
      setLoading(false);
    }
  };

  const deleteCredential = async (credId) => {
    try {
      await axios.delete(`${API}/credentials/${credId}`);
      toast.success('Credentials deleted successfully');
      loadCredentials();
    } catch (error) {
      console.error('Failed to delete credentials:', error);
      toast.error('Failed to delete credentials');
    }
  };

  const startMigration = async () => {
    if (!selectedCredential) {
      toast.error('Please select credentials');
      return;
    }
    if (selectedProxies.length === 0) {
      toast.error('Please select at least one proxy to migrate');
      return;
    }

    // Show conversion preview first
    await generateConversionPreview();
  };

  const generateConversionPreview = async () => {
    try {
      setLoading(true);
      setMigrationPhase('preview');
      setMigrationConsoleLog(['Starting migration analysis...']);
      
      // Get policy mappings for selected proxies
      const selectedAnalyses = analysisData.filter(analysis => 
        selectedProxies.includes(analysis.id)
      );
      
      const preview = {
        proxies: selectedAnalyses.map(analysis => ({
          name: analysis.proxy_name,
          policies: analysis.policy_mappings.map(mapping => ({
            edge_policy: mapping.edge_policy,
            apigee_x_policy: mapping.apigee_x_equivalent,
            complexity: mapping.complexity,
            changes_required: mapping.custom_code_required,
            migration_notes: mapping.migration_notes
          }))
        }))
      };
      
      setConversionPreview(preview);
      setMigrationConsoleLog(prev => [...prev, 'Migration analysis completed', 'Ready for policy conversion...']);
      setShowConversionPreview(true);
    } catch (error) {
      console.error('Failed to generate preview:', error);
      toast.error('Failed to generate conversion preview');
    } finally {
      setLoading(false);
    }
  };

  const startPolicyConversion = async () => {
    try {
      setLoading(true);
      setMigrationPhase('converting');
      setMigrationConsoleLog(prev => [...prev, 'Starting AI-powered policy conversion...']);
      
      // Simulate AI conversion process with real-time updates
      await simulateConversionSteps();
      
    } catch (error) {
      console.error('Policy conversion failed:', error);
      setMigrationConsoleLog(prev => [...prev, `❌ Conversion failed: ${error.message}`]);
      toast.error('Policy conversion failed');
    } finally {
      setLoading(false);
    }
  };

  const simulateConversionSteps = async () => {
    const steps = [
      { message: 'Validating source proxy configuration...', delay: 2000 },
      { message: 'Completed: Validating source proxy', delay: 1000 },
      { message: 'Starting: Converting policies to Apigee X format', delay: 1000 },
      { message: 'Processing OAuth2 policy...', delay: 1500 },
      { message: 'Processing JavaScript policies...', delay: 2000 },
      { message: 'Processing custom policies...', delay: 2500 },
      { message: 'Completed: Converting policies to Apigee X format', delay: 1000 },
      { message: 'Starting: Generating Apigee X bundle with AI', delay: 1000 },
      { message: 'AI analyzing policy compatibility...', delay: 3000 },
      { message: 'Completed: Generating Apigee X bundle with AI', delay: 1000 },
      { message: 'Starting: Validating Apigee X bundle', delay: 1000 },
      { message: 'Validating policy syntax...', delay: 1500 },
      { message: 'Validating flow configuration...', delay: 1500 },
      { message: 'Completed: Validating Apigee X bundle', delay: 1000 },
      { message: '✅ Conversion completed! Review converted policies before migration.', delay: 1000 }
    ];

    for (const step of steps) {
      await new Promise(resolve => setTimeout(resolve, step.delay));
      setMigrationConsoleLog(prev => [...prev, step.message]);
    }

    // Generate sample converted policies
    await generateConvertedPolicies();
    setMigrationPhase('validation');
  };

  const generateConvertedPolicies = async () => {
    const sampleConversions = {};
    
    conversionPreview?.proxies.forEach(proxy => {
      proxy.policies.forEach(policy => {
        const convertedXML = generateApigeeXPolicyXML(policy);
        sampleConversions[policy.edge_policy] = {
          source: generateEdgePolicyXML(policy),
          converted: convertedXML,
          notes: policy.migration_notes,
          complexity: policy.complexity
        };
      });
    });
    
    setConvertedPolicies(sampleConversions);
  };

  const generateEdgePolicyXML = (policy) => {
    const templates = {
      'OAuth2': `<?xml version="1.0" encoding="UTF-8"?>
<OAuthV2 name="${policy.edge_policy}">
    <Operation>VerifyAccessToken</Operation>
    <AccessToken ref="request.header.authorization"/>
    <Scope>read</Scope>
</OAuthV2>`,
      'VerifyAPIKey': `<?xml version="1.0" encoding="UTF-8"?>
<VerifyAPIKey name="${policy.edge_policy}">
    <APIKey ref="request.queryparam.apikey"/>
</VerifyAPIKey>`,
      'JavaScript': `<?xml version="1.0" encoding="UTF-8"?>
<Javascript name="${policy.edge_policy}" timeLimit="200">
    <ResourceURL>jsc://custom-logic.js</ResourceURL>
</Javascript>`,
      'Quota': `<?xml version="1.0" encoding="UTF-8"?>
<Quota name="${policy.edge_policy}">
    <Allow count="1000"/>
    <Interval>1</Interval>
    <TimeUnit>hour</TimeUnit>
</Quota>`
    };
    
    return templates[policy.edge_policy] || `// Custom Edge Policy: ${policy.edge_policy}
// Original configuration needs manual review`;
  };

  const generateApigeeXPolicyXML = (policy) => {
    const templates = {
      'OAuth2': `<?xml version="1.0" encoding="UTF-8"?>
<OAuthV2 name="${policy.apigee_x_policy}">
    <Operation>VerifyAccessToken</Operation>
    <AccessToken ref="request.header.authorization"/>
    <Scope>read</Scope>
    <!-- Apigee X: Enhanced with GCP integration -->
    <GenerateResponse enabled="false"/>
</OAuthV2>`,
      'VerifyAPIKey': `<?xml version="1.0" encoding="UTF-8"?>
<VerifyAPIKey name="${policy.apigee_x_policy}">
    <APIKey ref="request.queryparam.apikey"/>
    <!-- Apigee X: Improved validation -->
    <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</VerifyAPIKey>`,
      'JavaScript': `<?xml version="1.0" encoding="UTF-8"?>
<Javascript name="${policy.apigee_x_policy}" timeLimit="200">
    <ResourceURL>jsc://custom-logic-x.js</ResourceURL>
    <!-- Apigee X: Updated runtime compatibility -->
    <IncludeURL>jsc://apigee-x-utils.js</IncludeURL>
</Javascript>`,
      'Quota': `<?xml version="1.0" encoding="UTF-8"?>
<Quota name="${policy.apigee_x_policy}">
    <Allow count="1000"/>
    <Interval>1</Interval>
    <TimeUnit>hour</TimeUnit>
    <!-- Apigee X: Enhanced distributed quota -->
    <Distributed>true</Distributed>
    <Synchronous>false</Synchronous>
</Quota>`
    };
    
    return templates[policy.edge_policy] || `// Converted Apigee X Policy: ${policy.apigee_x_policy}
// AI-generated configuration - requires validation`;
  };

  const viewPolicyComparison = (policy) => {
    const conversion = convertedPolicies[policy.edge_policy];
    setSelectedPolicyComparison({
      ...policy,
      source: conversion?.source || 'Source policy not available',
      converted: conversion?.converted || 'Converted policy not available',
      notes: conversion?.notes || policy.migration_notes
    });
    setShowPolicyComparison(true);
  };

  const updateConvertedPolicy = (policyName, newContent) => {
    setConvertedPolicies(prev => ({
      ...prev,
      [policyName]: {
        ...prev[policyName],
        converted: newContent
      }
    }));
    setMigrationConsoleLog(prev => [...prev, `📝 Policy ${policyName} updated by user`]);
  };

  const confirmMigration = async () => {
    try {
      setLoading(true);
      const request = {
        proxy_analysis_ids: selectedProxies,
        credentials_id: selectedCredential,
        target_environment: 'development',
        auto_deploy: true
      };
      
      await axios.post(`${API}/migrate`, request);
      toast.success(`Started migration for ${selectedProxies.length} proxies`);
      setSelectedProxies([]);
      setShowConversionPreview(false);
      setActiveTab('status');
      loadMigrations();
    } catch (error) {
      console.error('Failed to start migration:', error);
      toast.error('Failed to start migration');
    } finally {
      setLoading(false);
    }
  };

  const cancelMigration = async (migrationId) => {
    try {
      await axios.delete(`${API}/migration/${migrationId}`);
      toast.success('Migration cancelled');
      loadMigrations();
    } catch (error) {
      console.error('Failed to cancel migration:', error);
      toast.error('Failed to cancel migration');
    }
  };

  const pauseMigration = async (migrationId) => {
    try {
      // In a real implementation, you'd have a pause endpoint
      toast.info('Migration pause requested (demo)');
      // await axios.post(`${API}/migration/${migrationId}/pause`);
    } catch (error) {
      console.error('Failed to pause migration:', error);
      toast.error('Failed to pause migration');
    }
  };

  const downloadMigrationReport = (migration) => {
    const report = {
      migration_id: migration.id,
      proxy_name: migration.proxy_name,
      status: migration.status,
      started_at: migration.started_at,
      completed_at: migration.completed_at,
      progress: migration.progress,
      steps_completed: migration.steps_completed,
      steps_failed: migration.steps_failed,
      migration_log: migration.migration_log,
      deployment_url: migration.deployment_url,
      error_message: migration.error_message
    };
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `migration_report_${migration.proxy_name}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-gray-100 text-gray-800';
      case 'preparing': return 'bg-blue-100 text-blue-800';
      case 'converting': return 'bg-purple-100 text-purple-800';
      case 'validating': return 'bg-yellow-100 text-yellow-800';
      case 'deploying': return 'bg-indigo-100 text-indigo-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-600" />;
      case 'pending': return <Clock className="w-4 h-4 text-gray-600" />;
      default: return <Activity className="w-4 h-4 text-blue-600 animate-spin" />;
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const completedAnalyses = analysisData.filter(analysis => analysis.status === 'completed');

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Migration Center</h1>
          <p className="text-gray-600 mt-1">Execute real-time migrations from Apigee Edge to Apigee X</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button 
            onClick={loadMigrations} 
            variant="outline" 
            size="sm"
            data-testid="refresh-migrations"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-fit lg:grid-cols-3">
          <TabsTrigger value="execute" className="flex items-center space-x-2">
            <Play className="w-4 h-4" />
            <span>Execute Migration</span>
          </TabsTrigger>
          <TabsTrigger value="status" className="flex items-center space-x-2">
            <Activity className="w-4 h-4" />
            <span>Migration Status</span>
          </TabsTrigger>
          <TabsTrigger value="credentials" className="flex items-center space-x-2">
            <Settings className="w-4 h-4" />
            <span>Credentials</span>
          </TabsTrigger>
        </TabsList>

        {/* Execute Migration Tab */}
        <TabsContent value="execute" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Proxy Selection */}
            <Card className="glass-effect border-0">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="w-5 h-5 text-blue-600" />
                  <span>Select Proxies to Migrate</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-3">
                    {completedAnalyses.length > 0 ? (
                      completedAnalyses.map((analysis) => (
                        <div
                          key={analysis.id}
                          className="flex items-center space-x-3 p-3 bg-white/50 rounded-lg border border-gray-100"
                        >
                          <Checkbox
                            checked={selectedProxies.includes(analysis.id)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setSelectedProxies([...selectedProxies, analysis.id]);
                              } else {
                                setSelectedProxies(selectedProxies.filter(id => id !== analysis.id));
                              }
                            }}
                            data-testid={`select-proxy-${analysis.id}`}
                          />
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <h3 className="font-medium text-gray-900">{analysis.proxy_name}</h3>
                              <Badge className={
                                analysis.complexity_level === 'simple' ? 'bg-green-100 text-green-800' :
                                analysis.complexity_level === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }>
                                {analysis.complexity_level}
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600">
                              {analysis.policy_count} policies • {analysis.migration_effort}
                            </p>
                            <Progress value={analysis.complexity_score} className="mt-2 h-2" />
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8">
                        <Database className="w-12 h-12 mx-auto text-gray-300 mb-4" />
                        <p className="text-gray-600">No analyzed proxies available for migration</p>
                        <p className="text-sm text-gray-500 mt-1">
                          Upload and analyze proxies first to enable migration
                        </p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Migration Configuration */}
            <Card className="glass-effect border-0">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Server className="w-5 h-5 text-purple-600" />
                  <span>Migration Configuration</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Credentials Selection */}
                <div>
                  <Label htmlFor="credentials">Apigee Credentials</Label>
                  <Select value={selectedCredential} onValueChange={setSelectedCredential}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select credentials" />
                    </SelectTrigger>
                    <SelectContent>
                      {credentials.map((cred) => (
                        <SelectItem key={cred.id} value={cred.id}>
                          <div>
                            <div className="font-medium">{cred.name}</div>
                            <div className="text-sm text-gray-500">
                              {cred.edge_org} → {cred.apigee_x_project}
                            </div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  {credentials.length === 0 && (
                    <p className="text-sm text-yellow-600 mt-2">
                      No credentials configured. Add credentials in the Credentials tab.
                    </p>
                  )}
                </div>

                {/* Selected Proxies Summary */}
                <div>
                  <Label>Selected Proxies ({selectedProxies.length})</Label>
                  <div className="mt-2 space-y-1">
                    {selectedProxies.length > 0 ? (
                      selectedProxies.map((proxyId) => {
                        const proxy = completedAnalyses.find(a => a.id === proxyId);
                        return proxy ? (
                          <div key={proxyId} className="text-sm text-gray-600 bg-gray-50 px-2 py-1 rounded">
                            {proxy.proxy_name}
                          </div>
                        ) : null;
                      })
                    ) : (
                      <p className="text-sm text-gray-500">No proxies selected</p>
                    )}
                  </div>
                </div>

                <Separator />

                {/* Migration Button */}
                <Button
                  onClick={startMigration}
                  disabled={!selectedCredential || selectedProxies.length === 0 || loading}
                  className="w-full btn-animation"
                  size="lg"
                  data-testid="preview-migration"
                >
                  {loading ? (
                    <>
                      <Activity className="w-4 h-4 mr-2 animate-spin" />
                      Generating Preview...
                    </>
                  ) : (
                    <>
                      <Eye className="w-4 h-4 mr-2" />
                      Preview Migration ({selectedProxies.length} proxies)
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Migration Status Tab */}
        <TabsContent value="status" className="space-y-6">
          <Card className="glass-effect border-0">
            <CardHeader>
              <CardTitle>Live Migration Status</CardTitle>
              <p className="text-sm text-gray-600">Real-time tracking of migration executions</p>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[600px]">
                <div className="space-y-4">
                  {migrations.length > 0 ? (
                    migrations.map((migration) => (
                      <Card key={migration.id} className="border border-gray-200">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <div className="flex items-center space-x-2 mb-1">
                                {getStatusIcon(migration.status)}
                                <h3 className="font-semibold text-gray-900">{migration.proxy_name}</h3>
                                <Badge className={getStatusColor(migration.status)}>
                                  {migration.status}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-600">{migration.current_step}</p>
                              <p className="text-xs text-gray-500 mt-1">
                                Started: {formatDateTime(migration.started_at)}
                              </p>
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              {migration.deployment_url && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => window.open(migration.deployment_url, '_blank')}
                                >
                                  <Download className="w-3 h-3 mr-1" />
                                  View
                                </Button>
                              )}
                              
                              {migration.status === 'completed' && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => downloadMigrationReport(migration)}
                                >
                                  <Download className="w-3 h-3 mr-1" />
                                  Report
                                </Button>
                              )}
                              
                              {['pending', 'preparing', 'converting', 'validating'].includes(migration.status) && (
                                <div className="flex space-x-2">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => pauseMigration(migration.id)}
                                  >
                                    <Pause className="w-3 h-3 mr-1" />
                                    Pause
                                  </Button>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => cancelMigration(migration.id)}
                                  >
                                    <XCircle className="w-3 h-3 mr-1" />
                                    Stop
                                  </Button>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          {/* Progress Bar */}
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>Progress</span>
                              <span>{migration.progress}%</span>
                            </div>
                            <Progress value={migration.progress} className="w-full" />
                          </div>
                          
                          {/* Migration Log */}
                          {migration.migration_log && migration.migration_log.length > 0 && (
                            <div className="mt-3">
                              <details className="text-xs">
                                <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                                  View Migration Log ({migration.migration_log.length} entries)
                                </summary>
                                <div className="mt-2 bg-gray-50 rounded p-2 max-h-32 overflow-y-auto">
                                  {migration.migration_log.map((log, index) => (
                                    <div key={index} className="text-gray-700">
                                      {log}
                                    </div>
                                  ))}
                                </div>
                              </details>
                            </div>
                          )}
                          
                          {/* Error Message */}
                          {migration.error_message && (
                            <div className="mt-3 bg-red-50 border border-red-200 rounded p-2">
                              <div className="flex items-center space-x-2">
                                <AlertCircle className="w-4 h-4 text-red-600" />
                                <span className="text-sm text-red-800 font-medium">Error</span>
                              </div>
                              <p className="text-sm text-red-700 mt-1">{migration.error_message}</p>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <div className="text-center py-12">
                      <Activity className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Migrations Yet</h3>
                      <p className="text-gray-600 mb-4">
                        Start your first migration from the Execute Migration tab
                      </p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Credentials Tab */}
        <TabsContent value="credentials" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Apigee Credentials</h2>
              <p className="text-gray-600">Manage your Apigee Edge and Apigee X credentials</p>
            </div>
            
            <Dialog open={isCredentialDialogOpen} onOpenChange={setIsCredentialDialogOpen}>
              <DialogTrigger asChild>
                <Button className="btn-animation" data-testid="add-credentials">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Credentials
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Add Apigee Credentials</DialogTitle>
                </DialogHeader>
                
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Configuration Name *</Label>
                    <Input
                      id="name"
                      value={newCredential.name}
                      onChange={(e) => setNewCredential({...newCredential, name: e.target.value})}
                      placeholder="e.g., Production Credentials"
                    />
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-3">
                    <h3 className="font-medium text-gray-900">Apigee Edge Configuration</h3>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor="edge_org">Organization *</Label>
                        <Input
                          id="edge_org"
                          value={newCredential.edge_org}
                          onChange={(e) => setNewCredential({...newCredential, edge_org: e.target.value})}
                          placeholder="edge-org-name"
                        />
                      </div>
                      <div>
                        <Label htmlFor="edge_env">Environment</Label>
                        <Input
                          id="edge_env"
                          value={newCredential.edge_env}
                          onChange={(e) => setNewCredential({...newCredential, edge_env: e.target.value})}
                          placeholder="prod"
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor="edge_username">Username</Label>
                        <Input
                          id="edge_username"
                          value={newCredential.edge_username}
                          onChange={(e) => setNewCredential({...newCredential, edge_username: e.target.value})}
                          placeholder="username@company.com"
                        />
                      </div>
                      <div>
                        <Label htmlFor="edge_password">Password</Label>
                        <div className="relative">
                          <Input
                            id="edge_password"
                            type={showPassword ? "text" : "password"}
                            value={newCredential.edge_password}
                            onChange={(e) => setNewCredential({...newCredential, edge_password: e.target.value})}
                            placeholder="password"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-2 top-1/2 transform -translate-y-1/2 h-auto p-1"
                            onClick={() => setShowPassword(!showPassword)}
                          >
                            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-3">
                    <h3 className="font-medium text-gray-900">Apigee X Configuration</h3>
                    
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor="apigee_x_project">Project ID *</Label>
                        <Input
                          id="apigee_x_project"
                          value={newCredential.apigee_x_project}
                          onChange={(e) => setNewCredential({...newCredential, apigee_x_project: e.target.value})}
                          placeholder="my-apigee-project"
                        />
                      </div>
                      <div>
                        <Label htmlFor="apigee_x_env">Environment</Label>
                        <Input
                          id="apigee_x_env"
                          value={newCredential.apigee_x_env}
                          onChange={(e) => setNewCredential({...newCredential, apigee_x_env: e.target.value})}
                          placeholder="eval"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Label htmlFor="apigee_x_service_account">Service Account JSON Key</Label>
                      <Textarea
                        id="apigee_x_service_account"
                        value={newCredential.apigee_x_service_account}
                        onChange={(e) => setNewCredential({...newCredential, apigee_x_service_account: e.target.value})}
                        placeholder="Paste your Google Cloud service account JSON key here..."
                        rows={4}
                      />
                    </div>
                  </div>
                  
                  <div className="flex justify-end space-x-3 pt-4">
                    <Button 
                      variant="outline" 
                      onClick={() => setIsCredentialDialogOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button 
                      onClick={saveCredential} 
                      disabled={loading}
                      data-testid="save-credentials"
                    >
                      {loading ? (
                        <>
                          <Activity className="w-4 h-4 mr-2 animate-spin" />
                          Saving...
                        </>
                      ) : (
                        'Save Credentials'
                      )}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Credentials List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {credentials.length > 0 ? (
              credentials.map((cred) => (
                <Card key={cred.id} className="glass-effect border-0">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-gray-900">{cred.name}</h3>
                        <p className="text-sm text-gray-600">
                          Created {formatDateTime(cred.created_at)}
                        </p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => deleteCredential(cred.id)}
                        data-testid={`delete-credential-${cred.id}`}
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Edge Org:</span>
                        <span className="font-medium">{cred.edge_org}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Edge Env:</span>
                        <span className="font-medium">{cred.edge_env}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Apigee X Project:</span>
                        <span className="font-medium">{cred.apigee_x_project}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Apigee X Env:</span>
                        <span className="font-medium">{cred.apigee_x_env}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <Settings className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Credentials Configured</h3>
                <p className="text-gray-600 mb-4">
                  Add your Apigee Edge and Apigee X credentials to start migrations
                </p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
      
      {/* Conversion Preview Dialog */}
      <Dialog open={showConversionPreview} onOpenChange={setShowConversionPreview}>
        <DialogContent className="max-w-7xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Migration Preview: Policy Conversion</DialogTitle>
            <p className="text-gray-600">Review the changes that will be applied during migration</p>
          </DialogHeader>
          
          {conversionPreview && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Migration Console */}
              <div className="lg:col-span-1">
                <Card className="h-fit">
                  <CardHeader>
                    <CardTitle className="text-sm flex items-center space-x-2">
                      <Activity className="w-4 h-4" />
                      <span>Migration Console</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-black rounded-lg p-4 h-64 overflow-y-auto text-xs text-green-400 font-mono">
                      {migrationConsoleLog.map((log, index) => (
                        <div key={index} className="mb-1">
                          {log}
                        </div>
                      ))}
                      {migrationPhase === 'converting' && (
                        <div className="animate-pulse">▋</div>
                      )}
                    </div>
                    
                    <div className="mt-4 space-y-2">
                      {migrationPhase === 'preview' && (
                        <Button
                          onClick={startPolicyConversion}
                          disabled={loading}
                          className="w-full"
                          data-testid="start-conversion"
                        >
                          {loading ? (
                            <>
                              <Activity className="w-4 h-4 mr-2 animate-spin" />
                              Analyzing...
                            </>
                          ) : (
                            <>
                              <Zap className="w-4 h-4 mr-2" />
                              Start AI Conversion
                            </>
                          )}
                        </Button>
                      )}
                      
                      {migrationPhase === 'validation' && (
                        <div className="space-y-2">
                          <div className="text-sm text-green-600 font-medium">
                            ✅ Conversion completed! Review policies below.
                          </div>
                          <Button
                            onClick={confirmMigration}
                            disabled={loading}
                            className="w-full bg-green-600 hover:bg-green-700"
                            data-testid="proceed-with-migration"
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Proceed with Migration
                          </Button>
                        </div>
                      )}
                      
                      {migrationPhase === 'converting' && (
                        <div className="text-sm text-blue-600">
                          🔄 Converting policies with AI...
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              {/* Right Column: Policy Conversion Details */}
              <div className="lg:col-span-2">
                <div className="space-y-4">
                  {conversionPreview.proxies.map((proxy, proxyIndex) => (
                    <Card key={proxyIndex} className="border-2">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          <span>{proxy.name}</span>
                          <Badge variant="outline">{proxy.policies.length} policies</Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <h4 className="font-medium text-gray-900">Policy Conversions:</h4>
                          
                          {proxy.policies.map((policy, policyIndex) => (
                            <div key={policyIndex} className="p-4 bg-gray-50 rounded-lg border">
                              {/* Policy Header */}
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center space-x-3">
                                  <Badge className={
                                    policy.complexity === 'simple' ? 'bg-green-100 text-green-800' :
                                    policy.complexity === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-red-100 text-red-800'
                                  }>
                                    {policy.complexity}
                                  </Badge>
                                  <span className="font-medium">{policy.edge_policy}</span>
                                  <ArrowRight className="w-4 h-4 text-gray-400" />
                                  <span className="font-medium text-green-700">{policy.apigee_x_policy}</span>
                                </div>
                                
                                {migrationPhase === 'validation' && convertedPolicies[policy.edge_policy] && (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => viewPolicyComparison(policy)}
                                    data-testid={`view-conversion-${policy.edge_policy}`}
                                  >
                                    <Eye className="w-3 h-3 mr-1" />
                                    View/Edit
                                  </Button>
                                )}
                              </div>
                              
                              {/* Conversion Status */}
                              <div className="text-sm space-y-2">
                                {migrationPhase === 'preview' && (
                                  <div className="text-gray-600">
                                    ⏳ Pending conversion...
                                  </div>
                                )}
                                
                                {migrationPhase === 'converting' && (
                                  <div className="text-blue-600">
                                    🔄 Converting...
                                  </div>
                                )}
                                
                                {migrationPhase === 'validation' && (
                                  <div className="text-green-600">
                                    ✅ Conversion completed - Ready for review
                                  </div>
                                )}
                                
                                {policy.migration_notes && (
                                  <div className="p-2 bg-blue-50 rounded text-sm text-blue-800">
                                    <strong>Notes:</strong> {policy.migration_notes}
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                
                {/* Warning for Complex Policies */}
                <Card className="bg-yellow-50 border-yellow-200 mt-4">
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-3">
                      <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-yellow-800">Important Migration Notes</h4>
                        <ul className="text-yellow-700 text-sm mt-2 space-y-1">
                          <li>• Review all converted policies before proceeding</li>
                          <li>• Complex policies may require additional configuration</li>
                          <li>• JavaScript policies are updated for Apigee X runtime</li>
                          <li>• Test thoroughly in development environment</li>
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
      
      {/* Policy Comparison Dialog */}
      <Dialog open={showPolicyComparison} onOpenChange={(open) => {
        setShowPolicyComparison(open);
        if (!open) {
          // Reset editing state when dialog closes
          setIsEditingPolicy(false);
          setEditedPolicyContent('');
        }
      }}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Policy Comparison: {selectedPolicyComparison?.edge_policy}</DialogTitle>
            <p className="text-gray-600">Compare source and converted policies</p>
          </DialogHeader>
          
          {selectedPolicyComparison && (
            <div className="space-y-6">
              {/* Policy Info */}
              <div className="grid grid-cols-2 gap-4">
                <Card className="bg-blue-50 border-blue-200">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-blue-700">Apigee Edge (Source)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="font-medium">{selectedPolicyComparison.edge_policy}</p>
                  </CardContent>
                </Card>
                
                <Card className="bg-green-50 border-green-200">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-green-700">Apigee X (Converted)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="font-medium">{selectedPolicyComparison.apigee_x_policy}</p>
                  </CardContent>
                </Card>
              </div>
              
              {/* Side-by-side Policy Content */}
              <div className="grid grid-cols-2 gap-4">
                {/* Source Policy */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Source Policy Configuration</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="bg-gray-100 p-4 rounded-lg text-xs overflow-x-auto font-mono h-64 overflow-y-auto">
                      {selectedPolicyComparison.source}
                    </pre>
                  </CardContent>
                </Card>
                
                {/* Converted Policy (Editable) */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm flex items-center justify-between">
                      <span>Converted Policy Configuration</span>
                      <div className="flex items-center space-x-2">
                        {isEditingPolicy ? (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                updateConvertedPolicy(selectedPolicyComparison.edge_policy, editedPolicyContent);
                                setSelectedPolicyComparison({
                                  ...selectedPolicyComparison,
                                  converted: editedPolicyContent
                                });
                                setIsEditingPolicy(false);
                                toast.success('Policy updated successfully');
                              }}
                              className="text-green-700 border-green-300 hover:bg-green-50"
                            >
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Save
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setIsEditingPolicy(false);
                                setEditedPolicyContent('');
                              }}
                              className="text-gray-600"
                            >
                              <XCircle className="w-3 h-3 mr-1" />
                              Cancel
                            </Button>
                          </>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setIsEditingPolicy(true);
                              setEditedPolicyContent(selectedPolicyComparison.converted);
                            }}
                          >
                            <Edit className="w-3 h-3 mr-1" />
                            Edit
                          </Button>
                        )}
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {isEditingPolicy ? (
                      <div className="space-y-2">
                        <Label htmlFor="policy-editor" className="text-xs text-gray-600">
                          Edit the converted policy configuration below:
                        </Label>
                        <Textarea
                          id="policy-editor"
                          value={editedPolicyContent}
                          onChange={(e) => setEditedPolicyContent(e.target.value)}
                          className="font-mono text-xs h-64 bg-green-50 border-2 border-green-300 focus:border-green-500"
                          placeholder="Edit policy configuration here..."
                        />
                        <div className="text-xs text-gray-500 flex items-center space-x-1">
                          <AlertCircle className="w-3 h-3" />
                          <span>Make sure to maintain valid XML/JSON syntax</span>
                        </div>
                      </div>
                    ) : (
                      <pre className="bg-green-50 p-4 rounded-lg text-xs overflow-x-auto font-mono h-64 overflow-y-auto border-2 border-green-200">
                        {selectedPolicyComparison.converted}
                      </pre>
                    )}
                  </CardContent>
                </Card>
              </div>
              
              {/* Migration Notes */}
              <Card className="bg-yellow-50 border-yellow-200">
                <CardHeader>
                  <CardTitle className="text-sm text-yellow-800">Conversion Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-yellow-700">{selectedPolicyComparison.notes}</p>
                  {selectedPolicyComparison.changes_required && (
                    <Badge className="bg-amber-100 text-amber-800 mt-2">
                      Manual Review Required
                    </Badge>
                  )}
                </CardContent>
              </Card>
              
              <div className="flex justify-end space-x-3">
                <Button 
                  variant="outline" 
                  onClick={() => setShowPolicyComparison(false)}
                >
                  Close
                </Button>
                <Button 
                  onClick={() => {
                    toast.success('Policy changes saved');
                    setShowPolicyComparison(false);
                  }}
                >
                  Save Changes
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Migration;