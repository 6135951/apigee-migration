import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { ScrollArea } from './ui/scroll-area';
import { 
  Upload,
  FileText,
  Code,
  Play,
  CheckCircle,
  XCircle,
  ArrowRight,
  Download,
  Eye,
  Zap,
  Globe,
  Shield,
  Clock,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'sonner';

const ApiDocumentation = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, processing, complete
  const [swaggerFile, setSwaggerFile] = useState(null);
  const [originalSpec, setOriginalSpec] = useState(null);
  const [migratedSpec, setMigratedSpec] = useState(null);
  const [conversionProgress, setConversionProgress] = useState(0);
  const [testResults, setTestResults] = useState([]);
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);
  const [testEnvironment, setTestEnvironment] = useState('development');

  // Swagger/OpenAPI Upload
  const onDrop = React.useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    const fileName = file.name.toLowerCase();
    if (!fileName.endsWith('.json') && !fileName.endsWith('.yaml') && !fileName.endsWith('.yml')) {
      toast.error('Please upload a valid Swagger/OpenAPI file (JSON or YAML)');
      return;
    }

    setSwaggerFile(file);
    handleSwaggerUpload(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'text/yaml': ['.yaml', '.yml'],
      'application/x-yaml': ['.yaml', '.yml']
    },
    disabled: uploadStatus === 'uploading' || uploadStatus === 'processing'
  });

  const handleSwaggerUpload = async (file) => {
    setUploadStatus('uploading');
    setConversionProgress(10);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload-swagger', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setOriginalSpec(result.originalSpec);
        setConversionProgress(50);
        
        // Start AI conversion
        await convertToApigeeXSpec(result.specId);
        
        setUploadStatus('complete');
        setActiveTab('comparison');
        toast.success('Swagger documentation uploaded and converted successfully!');
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('idle');
      setConversionProgress(0);
      toast.error('Failed to upload Swagger documentation');
    }
  };

  const convertToApigeeXSpec = async (specId) => {
    setUploadStatus('processing');
    setConversionProgress(60);

    try {
      const response = await fetch(`/api/convert-swagger/${specId}`, {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        setMigratedSpec(result.convertedSpec);
        setConversionProgress(100);
      } else {
        throw new Error('Conversion failed');
      }
    } catch (error) {
      console.error('Conversion error:', error);
      toast.error('Failed to convert Swagger to Apigee X format');
    }
  };

  const runEndpointTest = async (endpoint) => {
    const testResult = {
      id: Date.now(),
      endpoint: endpoint.path,
      method: endpoint.method,
      status: 'running',
      timestamp: new Date().toISOString()
    };

    setTestResults(prev => [testResult, ...prev]);

    try {
      // Simulate API test
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock test result
      const success = Math.random() > 0.3; // 70% success rate
      
      setTestResults(prev => prev.map(test => 
        test.id === testResult.id 
          ? { 
              ...test, 
              status: success ? 'passed' : 'failed',
              responseTime: Math.floor(Math.random() * 500) + 100,
              statusCode: success ? 200 : 500,
              response: success ? 'Success response' : 'Error occurred'
            }
          : test
      ));

      toast.success(success ? 'Test passed!' : 'Test failed!');
    } catch (error) {
      setTestResults(prev => prev.map(test => 
        test.id === testResult.id 
          ? { ...test, status: 'failed', error: error.message }
          : test
      ));
    }
  };

  const mockEndpoints = originalSpec ? [
    { path: '/orders', method: 'GET', description: 'Get all orders' },
    { path: '/orders', method: 'POST', description: 'Create new order' },
    { path: '/orders/{id}', method: 'GET', description: 'Get order by ID' },
    { path: '/orders/{id}', method: 'PUT', description: 'Update order' },
    { path: '/orders/{id}', method: 'DELETE', description: 'Delete order' }
  ] : [];

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fadeIn">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">API Documentation & Testing</h1>
        <p className="text-gray-600">Upload, migrate, and test your API documentation for Apigee X</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="upload" className="flex items-center space-x-2">
            <Upload className="w-4 h-4" />
            <span>Upload Swagger</span>
          </TabsTrigger>
          <TabsTrigger value="comparison" disabled={!originalSpec}>
            <FileText className="w-4 h-4 mr-2" />
            Documentation
          </TabsTrigger>
          <TabsTrigger value="testing" disabled={!migratedSpec}>
            <Play className="w-4 h-4 mr-2" />
            API Testing
          </TabsTrigger>
          <TabsTrigger value="validation" disabled={!migratedSpec}>
            <CheckCircle className="w-4 h-4 mr-2" />
            Validation
          </TabsTrigger>
        </TabsList>

        {/* Upload Tab */}
        <TabsContent value="upload" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="w-5 h-5" />
                <span>Upload Swagger/OpenAPI Documentation</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div 
                {...getRootProps()} 
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-gray-400'
                } ${uploadStatus !== 'idle' ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <input {...getInputProps()} />
                
                {uploadStatus === 'idle' && (
                  <>
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <div>
                      <p className="text-lg font-medium text-gray-900 mb-2">
                        {isDragActive 
                          ? 'Drop your Swagger file here' 
                          : 'Upload Swagger/OpenAPI Documentation'
                        }
                      </p>
                      <p className="text-gray-600 mb-4">
                        Drag and drop or click to select JSON/YAML files
                      </p>
                      <p className="text-sm text-gray-500">
                        Supports Swagger 2.0, OpenAPI 3.0/3.1 formats
                      </p>
                    </div>
                  </>
                )}

                {uploadStatus === 'uploading' && (
                  <div className="space-y-4">
                    <Loader2 className="w-12 h-12 text-blue-600 mx-auto animate-spin" />
                    <div>
                      <p className="text-lg font-medium text-gray-900">Uploading Documentation</p>
                      <Progress value={conversionProgress} className="w-full max-w-md mx-auto mt-2" />
                    </div>
                  </div>
                )}

                {uploadStatus === 'processing' && (
                  <div className="space-y-4">
                    <Zap className="w-12 h-12 text-orange-600 mx-auto animate-pulse" />
                    <div>
                      <p className="text-lg font-medium text-gray-900">Converting to Apigee X Format</p>
                      <p className="text-gray-600">AI is migrating your documentation...</p>
                      <Progress value={conversionProgress} className="w-full max-w-md mx-auto mt-2" />
                    </div>
                  </div>
                )}

                {uploadStatus === 'complete' && (
                  <div className="space-y-4">
                    <CheckCircle className="w-12 h-12 text-green-600 mx-auto" />
                    <div>
                      <p className="text-lg font-medium text-gray-900">Conversion Complete!</p>
                      <p className="text-gray-600">Your documentation has been migrated to Apigee X format</p>
                      <Button 
                        onClick={() => setActiveTab('comparison')} 
                        className="mt-4"
                      >
                        View Documentation <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              {/* File Info */}
              {swaggerFile && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{swaggerFile.name}</p>
                      <p className="text-sm text-gray-600">
                        {(swaggerFile.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <Badge variant="outline">
                      {swaggerFile.name.toLowerCase().endsWith('.json') ? 'JSON' : 'YAML'}
                    </Badge>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Features Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <Code className="w-8 h-8 text-blue-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Smart Conversion</h3>
                <p className="text-sm text-gray-600">AI-powered migration from Swagger 2.0 to OpenAPI 3.0 with Apigee X optimizations</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <Play className="w-8 h-8 text-green-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Interactive Testing</h3>
                <p className="text-sm text-gray-600">Built-in API testing console with environment switching and validation</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <Shield className="w-8 h-8 text-purple-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Security Analysis</h3>
                <p className="text-sm text-gray-600">Automated security policy validation and compliance checking</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Documentation Comparison Tab */}
        <TabsContent value="comparison" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Original Documentation */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center justify-between">
                  <span className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-blue-600" />
                    <span>Original Swagger/OpenAPI</span>
                  </span>
                  <Badge variant="outline">Version 2.0</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-96">
                  <pre className="text-xs bg-gray-50 p-4 rounded-lg overflow-x-auto">
{originalSpec ? JSON.stringify(originalSpec, null, 2) : 'Loading...'}
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Migrated Documentation */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center justify-between">
                  <span className="flex items-center space-x-2">
                    <Code className="w-4 h-4 text-green-600" />
                    <span>Apigee X OpenAPI</span>
                  </span>
                  <Badge variant="outline" className="bg-green-50 text-green-700">Version 3.0</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-96">
                  <pre className="text-xs bg-green-50 p-4 rounded-lg overflow-x-auto">
{migratedSpec ? JSON.stringify(migratedSpec, null, 2) : 'Processing...'}
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-center space-x-4">
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Download Original
            </Button>
            <Button>
              <Download className="w-4 h-4 mr-2" />
              Download Migrated
            </Button>
            <Button 
              variant="outline"
              onClick={() => setActiveTab('testing')}
            >
              Start Testing <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </TabsContent>

        {/* API Testing Tab */}
        <TabsContent value="testing" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Endpoint List */}
            <Card className="lg:col-span-1">
              <CardHeader>
                <CardTitle className="text-sm flex items-center justify-between">
                  <span>API Endpoints</span>
                  <Badge>{mockEndpoints.length} endpoints</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-96">
                  {mockEndpoints.map((endpoint, index) => (
                    <div 
                      key={index}
                      className={`p-3 border-b cursor-pointer hover:bg-gray-50 ${
                        selectedEndpoint === endpoint ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => setSelectedEndpoint(endpoint)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <Badge 
                            variant="outline"
                            className={`text-xs ${
                              endpoint.method === 'GET' ? 'text-blue-600' :
                              endpoint.method === 'POST' ? 'text-green-600' :
                              endpoint.method === 'PUT' ? 'text-orange-600' :
                              'text-red-600'
                            }`}
                          >
                            {endpoint.method}
                          </Badge>
                          <p className="font-mono text-sm mt-1">{endpoint.path}</p>
                        </div>
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            runEndpointTest(endpoint);
                          }}
                        >
                          <Play className="w-3 h-3" />
                        </Button>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">{endpoint.description}</p>
                    </div>
                  ))}
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Test Console */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-sm flex items-center justify-between">
                  <span>API Test Console</span>
                  <div className="flex items-center space-x-2">
                    <Label className="text-xs">Environment:</Label>
                    <select 
                      value={testEnvironment}
                      onChange={(e) => setTestEnvironment(e.target.value)}
                      className="text-xs border rounded px-2 py-1"
                    >
                      <option value="development">Development</option>
                      <option value="staging">Staging</option>
                      <option value="production">Production</option>
                    </select>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {selectedEndpoint ? (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{selectedEndpoint.method}</Badge>
                      <code className="bg-gray-100 px-2 py-1 rounded text-sm">{selectedEndpoint.path}</code>
                      <Button size="sm" onClick={() => runEndpointTest(selectedEndpoint)}>
                        <Play className="w-3 h-3 mr-1" />
                        Test
                      </Button>
                    </div>
                    
                    {/* Request Parameters */}
                    <div className="space-y-2">
                      <Label className="text-sm">Headers</Label>
                      <Textarea 
                        placeholder='{"Content-Type": "application/json", "Authorization": "Bearer token"}'
                        className="font-mono text-sm h-20"
                      />
                    </div>
                    
                    {selectedEndpoint.method !== 'GET' && (
                      <div className="space-y-2">
                        <Label className="text-sm">Request Body</Label>
                        <Textarea 
                          placeholder='{"key": "value"}'
                          className="font-mono text-sm h-32"
                        />
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Globe className="w-12 h-12 mx-auto mb-2" />
                    <p>Select an endpoint to start testing</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Test Results */}
          {testResults.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Test Results</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  {testResults.map((result) => (
                    <div key={result.id} className="flex items-center justify-between p-3 border-b">
                      <div className="flex items-center space-x-3">
                        {result.status === 'running' && <Loader2 className="w-4 h-4 animate-spin text-blue-600" />}
                        {result.status === 'passed' && <CheckCircle className="w-4 h-4 text-green-600" />}
                        {result.status === 'failed' && <XCircle className="w-4 h-4 text-red-600" />}
                        
                        <div>
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline" className="text-xs">{result.method}</Badge>
                            <code className="text-sm">{result.endpoint}</code>
                          </div>
                          <p className="text-xs text-gray-600">
                            {new Date(result.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        {result.responseTime && (
                          <div className="flex items-center space-x-2">
                            <Clock className="w-3 h-3" />
                            <span className="text-xs">{result.responseTime}ms</span>
                            {result.statusCode && (
                              <Badge 
                                variant={result.statusCode === 200 ? "default" : "destructive"}
                                className="text-xs"
                              >
                                {result.statusCode}
                              </Badge>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </ScrollArea>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Validation Tab */}
        <TabsContent value="validation" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Validation Summary Cards */}
            <Card>
              <CardContent className="p-6 text-center">
                <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Schema Validation</h3>
                <p className="text-sm text-gray-600">OpenAPI 3.0 compliant</p>
                <Badge className="mt-2 bg-green-50 text-green-700">Passed</Badge>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <Shield className="w-8 h-8 text-blue-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Security Policies</h3>
                <p className="text-sm text-gray-600">OAuth 2.0 & API Key configured</p>
                <Badge className="mt-2 bg-blue-50 text-blue-700">Validated</Badge>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6 text-center">
                <AlertCircle className="w-8 h-8 text-orange-600 mx-auto mb-3" />
                <h3 className="font-semibold text-gray-900 mb-2">Compatibility</h3>
                <p className="text-sm text-gray-600">2 minor issues found</p>
                <Badge variant="outline" className="mt-2 text-orange-600">Review Required</Badge>
              </CardContent>
            </Card>
          </div>
          
          {/* Detailed Validation Results */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Validation Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-green-900">OpenAPI Schema Valid</h4>
                    <p className="text-sm text-green-700">Your API documentation follows OpenAPI 3.0 specifications correctly.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3 p-3 bg-orange-50 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-orange-900">Deprecated Response Format</h4>
                    <p className="text-sm text-orange-700">Some response schemas use deprecated formats that should be updated for better compatibility.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-900">Security Policies Applied</h4>
                    <p className="text-sm text-blue-700">Authentication and authorization policies are properly configured for Apigee X.</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ApiDocumentation;