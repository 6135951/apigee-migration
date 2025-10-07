import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import { Upload, FileText, CheckCircle, XCircle, Loader, AlertCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProxyUpload = ({ onProxyUploaded }) => {
  const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, analyzing, completed, error
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentProxyId, setCurrentProxyId] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    const fileName = file.name.toLowerCase();
    if (!fileName.endsWith('.xml') && !fileName.endsWith('.json') && !fileName.endsWith('.zip')) {
      toast.error('Please upload a valid XML, JSON, or ZIP proxy configuration file');
      return;
    }

    // Validate file size (100MB limit)
    const maxFileSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxFileSize) {
      toast.error('File size must be less than 100MB');
      return;
    }

    try {
      setUploadStatus('uploading');
      setUploadProgress(25);
      setError(null);
      
      // Upload file
      const formData = new FormData();
      formData.append('file', file);
      
      const uploadResponse = await axios.post(`${API}/upload-proxy`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const proxyId = uploadResponse.data.proxy_id;
      setCurrentProxyId(proxyId);
      setUploadProgress(50);
      
      // Start analysis
      setUploadStatus('analyzing');
      setUploadProgress(75);
      
      const analysisResponse = await axios.post(`${API}/analyze-proxy/${proxyId}`);
      setAnalysisResult(analysisResponse.data);
      setUploadProgress(100);
      setUploadStatus('completed');
      
      toast.success(`Analysis completed for ${analysisResponse.data.proxy_name}`);
      
      if (onProxyUploaded) {
        onProxyUploaded(analysisResponse.data);
      }
      
    } catch (error) {
      console.error('Upload/analysis error:', error);
      setUploadStatus('error');
      setError(error.response?.data?.detail || 'Upload or analysis failed');
      toast.error('Failed to upload or analyze proxy');
    }
  }, [onProxyUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/xml': ['.xml'],
      'application/json': ['.json'],
      'application/zip': ['.zip']
    },
    multiple: false,
    disabled: uploadStatus === 'uploading' || uploadStatus === 'analyzing'
  });

  const resetUpload = () => {
    setUploadStatus('idle');
    setUploadProgress(0);
    setCurrentProxyId(null);
    setAnalysisResult(null);
    setError(null);
  };

  const getComplexityColor = (level) => {
    switch (level) {
      case 'simple': return 'bg-green-100 text-green-800';
      case 'moderate': return 'bg-yellow-100 text-yellow-800';
      case 'complex': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case 'uploading': return <Loader className="w-5 h-5 animate-spin text-blue-600" />;
      case 'analyzing': return <Loader className="w-5 h-5 animate-spin text-purple-600" />;
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-600" />;
      default: return <Upload className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = () => {
    switch (uploadStatus) {
      case 'uploading': return 'Uploading proxy...';
      case 'analyzing': return 'Analyzing with AI...';
      case 'completed': return 'Analysis completed!';
      case 'error': return 'Upload failed';
      default: return 'Ready to upload';
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fadeIn">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Apigee Proxy</h1>
        <p className="text-gray-600">Upload your Apigee Edge proxy configuration (XML, JSON, or complete ZIP bundle) for automated migration analysis</p>
      </div>

      {/* Upload Area */}
      <Card className="glass-effect border-0">
        <CardContent className="p-8">
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300
              ${isDragActive 
                ? 'border-blue-500 bg-blue-50 transform scale-105' 
                : uploadStatus === 'idle'
                  ? 'border-gray-300 hover:border-blue-400 hover:bg-blue-50/50'
                  : 'border-gray-300 bg-gray-50 cursor-not-allowed'
              }
            `}
            data-testid="proxy-upload-dropzone"
          >
            <input {...getInputProps()} data-testid="proxy-upload-input" />
            
            <div className="space-y-4">
              <div className="flex justify-center">
                {getStatusIcon()}
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {isDragActive ? 'Drop the file here' : 'Drop your proxy file here'}
                </h3>
                <p className="text-gray-600 mt-1">
                  {uploadStatus === 'idle' 
                    ? 'or click to select file (XML, JSON, or ZIP formats supported)'
                    : getStatusText()
                  }
                </p>
              </div>
              
              {uploadStatus !== 'idle' && (
                <div className="space-y-2">
                  <Progress value={uploadProgress} className="w-full max-w-md mx-auto" />
                  <p className="text-sm text-gray-500">{uploadProgress}% complete</p>
                </div>
              )}
              
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-md mx-auto">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    <span className="text-red-800 text-sm font-medium">Error</span>
                  </div>
                  <p className="text-red-700 text-sm mt-1">{error}</p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Result */}
      {analysisResult && (
        <Card className="glass-effect border-0">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-gray-900">Analysis Results</CardTitle>
              <Button onClick={resetUpload} variant="outline" size="sm" data-testid="reset-upload">
                Upload Another
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white/50 rounded-lg p-4 text-center">
                <FileText className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                <div className="text-2xl font-bold text-gray-900">{analysisResult.proxy_name}</div>
                <div className="text-sm text-gray-600">Proxy Name</div>
              </div>
              
              <div className="bg-white/50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-gray-900">{analysisResult.policy_count}</div>
                <div className="text-sm text-gray-600">Total Policies</div>
              </div>
              
              <div className="bg-white/50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-gray-900">{Math.round(analysisResult.complexity_score)}%</div>
                <div className="text-sm text-gray-600">Complexity Score</div>
                <Badge className={`mt-2 ${getComplexityColor(analysisResult.complexity_level)}`}>
                  {analysisResult.complexity_level}
                </Badge>
              </div>
            </div>
            
            {/* Migration Effort */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">Estimated Migration Effort</h4>
              <p className="text-lg text-blue-800 font-medium">{analysisResult.migration_effort}</p>
            </div>
            
            {/* Custom Policies */}
            {analysisResult.custom_policies && analysisResult.custom_policies.length > 0 && (
              <div className="bg-yellow-50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-2 text-yellow-600" />
                  Custom Policies Detected
                </h4>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.custom_policies.map((policy, index) => (
                    <Badge key={index} className="bg-yellow-200 text-yellow-800">
                      {policy}
                    </Badge>
                  ))}
                </div>
                <p className="text-sm text-yellow-700 mt-2">
                  These policies require manual analysis and migration planning.
                </p>
              </div>
            )}
            
            {/* AI Recommendations */}
            <div className="bg-purple-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-2">AI Recommendations</h4>
              <p className="text-gray-700 text-sm leading-relaxed">{analysisResult.ai_recommendations}</p>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Help Section */}
      <Card className="glass-effect border-0">
        <CardContent className="p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Supported File Types</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-3 p-3 bg-white/50 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
              <div>
                <div className="font-medium text-gray-900">XML Proxy Bundle</div>
                <div className="text-sm text-gray-600">Apigee Edge proxy configuration files</div>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-white/50 rounded-lg">
              <FileText className="w-6 h-6 text-green-600" />
              <div>
                <div className="font-medium text-gray-900">JSON Configuration</div>
                <div className="text-sm text-gray-600">JSON-formatted proxy definitions</div>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-white/50 rounded-lg">
              <FileText className="w-6 h-6 text-purple-600" />
              <div>
                <div className="font-medium text-gray-900">ZIP Proxy Bundle</div>
                <div className="text-sm text-gray-600">Complete Apigee Edge proxy bundles (up to 100MB)</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProxyUpload;