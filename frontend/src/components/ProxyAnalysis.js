import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Textarea } from './ui/textarea';
import { 
  Search, 
  Filter, 
  FileText, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  ArrowRight,
  ExternalLink,
  Code,
  Settings,
  Shield,
  Download,
  Eye,
  Edit,
  Save,
  X
} from 'lucide-react';

const ProxyAnalysis = ({ analysisData }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [complexityFilter, setComplexityFilter] = useState('all');
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [showPolicyDialog, setShowPolicyDialog] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState(null);
  const [editingPolicy, setEditingPolicy] = useState(false);
  const [policyContent, setPolicyContent] = useState('');

  const filteredData = analysisData.filter(analysis => {
    const matchesSearch = analysis.proxy_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesComplexity = complexityFilter === 'all' || analysis.complexity_level === complexityFilter;
    return matchesSearch && matchesComplexity;
  });

  const getComplexityColor = (level) => {
    switch (level) {
      case 'simple': return 'bg-green-100 text-green-800 border-green-200';
      case 'moderate': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'complex': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const downloadReport = (analysis, type = 'full') => {
    let reportData;
    const filename = `${analysis.proxy_name}_${type}_report_${new Date().toISOString().split('T')[0]}.json`;
    
    switch (type) {
      case 'policies':
        reportData = {
          proxy_name: analysis.proxy_name,
          analysis_date: analysis.analyzed_at,
          policy_mappings: analysis.policy_mappings,
          custom_policies: analysis.custom_policies,
          policy_count: analysis.policy_count
        };
        break;
      case 'complexity':
        reportData = {
          proxy_name: analysis.proxy_name,
          complexity_score: analysis.complexity_score,
          complexity_level: analysis.complexity_level,
          migration_effort: analysis.migration_effort,
          ai_recommendations: analysis.ai_recommendations,
          analysis_date: analysis.analyzed_at
        };
        break;
      default:
        reportData = analysis;
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadAllReports = () => {
    const summaryReport = {
      generated_at: new Date().toISOString(),
      total_analyses: analysisData.length,
      complexity_distribution: analysisData.reduce((acc, analysis) => {
        acc[analysis.complexity_level] = (acc[analysis.complexity_level] || 0) + 1;
        return acc;
      }, {}),
      average_complexity: analysisData.reduce((sum, a) => sum + a.complexity_score, 0) / analysisData.length,
      analyses: analysisData.map(analysis => ({
        proxy_name: analysis.proxy_name,
        complexity_level: analysis.complexity_level,
        complexity_score: analysis.complexity_score,
        policy_count: analysis.policy_count,
        custom_policies_count: analysis.custom_policies.length,
        migration_effort: analysis.migration_effort,
        analyzed_at: analysis.analyzed_at
      }))
    };
    
    const blob = new Blob([JSON.stringify(summaryReport, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `apigee_migration_summary_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const viewPolicy = (policy) => {
    setSelectedPolicy(policy);
    // Generate sample policy content based on type
    const sampleContent = generateSamplePolicyContent(policy);
    setPolicyContent(sampleContent);
    setShowPolicyDialog(true);
    setEditingPolicy(false);
  };

  const generateSamplePolicyContent = (policy) => {
    const policyTemplates = {
      'OAuth2': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<OAuthV2 async="false" continueOnError="false" enabled="true" name="${policy.edge_policy}">
    <Operation>VerifyAccessToken</Operation>
    <AccessToken ref="request.header.authorization"/>
    <Scope>READ</Scope>
</OAuthV2>`,
      'VerifyAPIKey': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<VerifyAPIKey async="false" continueOnError="false" enabled="true" name="${policy.edge_policy}">
    <APIKey ref="request.queryparam.apikey"/>
</VerifyAPIKey>`,
      'SpikeArrest': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<SpikeArrest async="false" continueOnError="false" enabled="true" name="${policy.edge_policy}">
    <Rate>100pm</Rate>
</SpikeArrest>`,
      'Quota': `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Quota async="false" continueOnError="false" enabled="true" name="${policy.edge_policy}">
    <Allow count="1000"/>
    <Interval>1</Interval>
    <TimeUnit>hour</TimeUnit>
</Quota>`,
      'JavaScript': `// JavaScript policy: ${policy.edge_policy}
var request = context.getVariable("request");
var response = context.getVariable("response");

// Custom business logic
function processRequest() {
    // Implementation depends on specific requirements
    context.setVariable("custom.processed", true);
}`
    };
    
    return policyTemplates[policy.edge_policy] || `// Custom Policy: ${policy.edge_policy}
// This is a custom policy that requires manual migration
// Original configuration needs to be reviewed and adapted for Apigee X`;
  };

  const savePolicyContent = async () => {
    try {
      // Update the selected policy's content locally
      if (selectedPolicy) {
        // Create updated policy object
        const updatedPolicy = {
          ...selectedPolicy,
          apigee_x_equivalent: policyContent,
          migration_notes: `${selectedPolicy.migration_notes}\n[Edited by user on ${new Date().toLocaleString()}]`
        };
        
        // Update in the local data
        const updatedAnalysisData = analysisData.map(analysis => {
          if (analysis.policy_mappings) {
            const updatedMappings = analysis.policy_mappings.map(mapping => 
              mapping.edge_policy === selectedPolicy.edge_policy 
                ? updatedPolicy 
                : mapping
            );
            return { ...analysis, policy_mappings: updatedMappings };
          }
          return analysis;
        });
        
        // Update the selected policy state
        setSelectedPolicy(updatedPolicy);
        
        // Here you could also save to backend if needed
        // await fetch(`/api/update-policy/${analysis.id}`, {
        //   method: 'PUT',
        //   body: JSON.stringify(updatedPolicy)
        // });
        
        console.log('Policy content saved successfully:', policyContent);
        setEditingPolicy(false);
        
        // Show success message (you could add toast notification here)
        alert('Policy configuration saved successfully!');
      }
    } catch (error) {
      console.error('Error saving policy content:', error);
      alert('Failed to save policy configuration. Please try again.');
    }
  };

  const PolicyMappingCard = ({ mapping }) => (
    <Card className="mb-3">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Code className="w-4 h-4 text-blue-600" />
            <Button 
              variant="link" 
              className="p-0 h-auto font-medium text-gray-900 hover:text-blue-600"
              onClick={() => viewPolicy(mapping)}
              data-testid={`view-policy-${mapping.edge_policy}`}
            >
              {mapping.edge_policy}
            </Button>
          </div>
          <ArrowRight className="w-4 h-4 text-gray-400" />
          <div className="flex items-center space-x-2">
            <Settings className="w-4 h-4 text-green-600" />
            <span className="font-medium text-gray-900">{mapping.apigee_x_equivalent}</span>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <Badge className={getComplexityColor(mapping.complexity)}>
            {mapping.complexity}
          </Badge>
          {mapping.custom_code_required && (
            <Badge className="bg-purple-100 text-purple-800">
              Custom Code Required
            </Badge>
          )}
        </div>
        {mapping.migration_notes && (
          <p className="text-sm text-gray-600 mt-2">{mapping.migration_notes}</p>
        )}
      </CardContent>
    </Card>
  );

  if (analysisData.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-24 h-24 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
          <FileText className="w-12 h-12 text-gray-400" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">No Analyses Yet</h2>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          Upload your first Apigee proxy to see detailed migration analysis results here.
        </p>
        <Button className="btn-animation" data-testid="go-to-upload">
          Upload First Proxy
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <p className="text-gray-600 mt-1">Detailed migration analysis for your Apigee proxies</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button 
            onClick={downloadAllReports}
            variant="outline" 
            className="btn-animation"
            data-testid="download-all-reports"
          >
            <Download className="w-4 h-4 mr-2" />
            Download Summary
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="glass-effect border-0">
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search proxies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  data-testid="analysis-search"
                />
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={complexityFilter}
                onChange={(e) => setComplexityFilter(e.target.value)}
                className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                data-testid="complexity-filter"
              >
                <option value="all">All Complexity</option>
                <option value="simple">Simple</option>
                <option value="moderate">Moderate</option>
                <option value="complex">Complex</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Analysis List */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Proxy Analyses ({filteredData.length})
          </h2>
          <ScrollArea className="h-[600px]">
            <div className="space-y-3">
              {filteredData.map((analysis, index) => (
                <Card
                  key={analysis.id}
                  className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                    selectedAnalysis?.id === analysis.id 
                      ? 'ring-2 ring-blue-500 shadow-lg' 
                      : 'hover:shadow-md'
                  }`}
                  onClick={() => setSelectedAnalysis(analysis)}
                  data-testid={`analysis-card-${index}`}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-gray-900 mb-1">{analysis.proxy_name}</h3>
                        <p className="text-sm text-gray-600 flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {formatDateTime(analysis.analyzed_at)}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-gray-900">
                          {Math.round(analysis.complexity_score)}%
                        </div>
                        <Badge className={getComplexityColor(analysis.complexity_level)}>
                          {analysis.complexity_level}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Progress value={analysis.complexity_score} className="w-full" />
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>{analysis.policy_count} policies</span>
                        <span>{analysis.migration_effort}</span>
                      </div>
                      
                      {analysis.custom_policies.length > 0 && (
                        <div className="flex items-center space-x-1">
                          <AlertTriangle className="w-3 h-3 text-yellow-600" />
                          <span className="text-xs text-yellow-700">
                            {analysis.custom_policies.length} custom policies
                          </span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </div>

        {/* Analysis Details */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Analysis Details
          </h2>
          
          {selectedAnalysis ? (
            <Card className="glass-effect border-0">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{selectedAnalysis.proxy_name}</CardTitle>
                  <Badge className={getStatusColor(selectedAnalysis.status)}>
                    {selectedAnalysis.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="overview" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="policies">Policies</TabsTrigger>
                    <TabsTrigger value="recommendations">AI Insights</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="overview" className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-white/50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-gray-900">
                          {Math.round(selectedAnalysis.complexity_score)}%
                        </div>
                        <div className="text-sm text-gray-600">Complexity Score</div>
                      </div>
                      <div className="bg-white/50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-gray-900">
                          {selectedAnalysis.policy_count}
                        </div>
                        <div className="text-sm text-gray-600">Total Policies</div>
                      </div>
                    </div>
                    
                    <Separator />
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Migration Effort</h4>
                      <p className="text-lg text-blue-800 font-medium bg-blue-50 rounded-lg p-3">
                        {selectedAnalysis.migration_effort}
                      </p>
                    </div>
                    
                    <div className="flex justify-between">
                      <Button 
                        onClick={() => downloadReport(selectedAnalysis, 'complexity')}
                        variant="outline" 
                        size="sm"
                      >
                        <Download className="w-3 h-3 mr-1" />
                        Complexity Report
                      </Button>
                      <Button 
                        onClick={() => downloadReport(selectedAnalysis, 'policies')}
                        variant="outline" 
                        size="sm"
                      >
                        <Download className="w-3 h-3 mr-1" />
                        Policy Report
                      </Button>
                    </div>
                    
                    {selectedAnalysis.custom_policies.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                          <AlertTriangle className="w-4 h-4 mr-2 text-yellow-600" />
                          Custom Policies
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {selectedAnalysis.custom_policies.map((policy, idx) => (
                            <Badge key={idx} className="bg-yellow-200 text-yellow-800">
                              {policy}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </TabsContent>
                  
                  <TabsContent value="policies" className="space-y-3">
                    <ScrollArea className="h-[400px]">
                      {selectedAnalysis.policy_mappings.map((mapping, idx) => (
                        <PolicyMappingCard key={idx} mapping={mapping} />
                      ))}
                    </ScrollArea>
                  </TabsContent>
                  
                  <TabsContent value="recommendations">
                    <div className="bg-purple-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                        <Shield className="w-4 h-4 mr-2 text-purple-600" />
                        AI-Generated Insights
                      </h4>
                      <p className="text-gray-700 text-sm leading-relaxed">
                        {selectedAnalysis.ai_recommendations}
                      </p>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          ) : (
            <Card className="glass-effect border-0">
              <CardContent className="p-8 text-center">
                <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Select an Analysis</h3>
                <p className="text-gray-600">
                  Click on any proxy analysis from the list to view detailed migration information.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
      
      {/* Policy Viewer Dialog */}
      <Dialog open={showPolicyDialog} onOpenChange={setShowPolicyDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between">
              <span>Policy Details: {selectedPolicy?.edge_policy}</span>
              <div className="flex items-center space-x-2">
                <Badge className={getComplexityColor(selectedPolicy?.complexity)}>
                  {selectedPolicy?.complexity}
                </Badge>
                {!editingPolicy ? (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => setEditingPolicy(true)}
                  >
                    <Edit className="w-3 h-3 mr-1" />
                    Edit
                  </Button>
                ) : (
                  <div className="flex space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={savePolicyContent}
                    >
                      <Save className="w-3 h-3 mr-1" />
                      Save
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={() => setEditingPolicy(false)}
                    >
                      <X className="w-3 h-3" />
                    </Button>
                  </div>
                )}
              </div>
            </DialogTitle>
          </DialogHeader>
          
          {selectedPolicy && (
            <div className="space-y-4">
              {/* Policy Mapping Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-blue-700">Apigee Edge Policy</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="font-medium">{selectedPolicy.edge_policy}</p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-green-700">Apigee X Equivalent</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="font-medium">{selectedPolicy.apigee_x_equivalent}</p>
                  </CardContent>
                </Card>
              </div>
              
              {/* Migration Notes */}
              <Card className="bg-yellow-50 border-yellow-200">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm text-yellow-800">Migration Notes</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-yellow-700">{selectedPolicy.migration_notes}</p>
                  {selectedPolicy.custom_code_required && (
                    <Badge className="bg-purple-100 text-purple-800 mt-2">
                      Requires Custom Code Review
                    </Badge>
                  )}
                </CardContent>
              </Card>
              
              {/* Policy Configuration */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Policy Configuration</CardTitle>
                </CardHeader>
                <CardContent>
                  {editingPolicy ? (
                    <Textarea
                      value={policyContent}
                      onChange={(e) => setPolicyContent(e.target.value)}
                      className="font-mono text-sm min-h-[300px]"
                      placeholder="Policy configuration..."
                    />
                  ) : (
                    <pre className="bg-gray-100 p-4 rounded-lg text-sm overflow-x-auto font-mono whitespace-pre-wrap">
                      {policyContent}
                    </pre>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProxyAnalysis;