import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { RefreshCw, TrendingUp, Clock, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ analysisData, loading, onRefresh }) => {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [migrationStats, setMigrationStats] = useState(null);

  useEffect(() => {
    loadDashboardStats();
    loadMigrationStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setStatsLoading(true);
      const response = await axios.get(`${API}/dashboard-stats`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    } finally {
      setStatsLoading(false);
    }
  };

  const loadMigrationStats = async () => {
    try {
      const response = await axios.get(`${API}/migrations`);
      const migrations = response.data;
      
      const stats = {
        total: migrations.length,
        completed: migrations.filter(m => m.status === 'completed').length,
        in_progress: migrations.filter(m => ['pending', 'preparing', 'converting', 'validating', 'deploying'].includes(m.status)).length,
        failed: migrations.filter(m => m.status === 'failed').length,
        recent: migrations.slice(0, 3)
      };
      
      setMigrationStats(stats);
    } catch (error) {
      console.error('Failed to load migration stats:', error);
    }
  };

  const handleRefresh = () => {
    onRefresh();
    loadDashboardStats();
    loadMigrationStats();
  };

  const getComplexityColor = (level) => {
    switch (level) {
      case 'simple': return 'bg-green-100 text-green-800';
      case 'moderate': return 'bg-yellow-100 text-yellow-800';
      case 'complex': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
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

  // Prepare chart data
  const complexityData = dashboardStats?.complexity_distribution ? 
    Object.entries(dashboardStats.complexity_distribution).map(([key, value]) => ({
      name: key.charAt(0).toUpperCase() + key.slice(1),
      count: value
    })) : [];

  const COLORS = {
    'Simple': '#10B981',
    'Moderate': '#F59E0B',
    'Complex': '#EF4444'
  };

  if (loading || statsLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div className="space-y-2">
            <div className="h-8 bg-gray-200 rounded-lg w-64 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-96 animate-pulse"></div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader className="pb-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-full"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Migration Dashboard</h1>
          <p className="text-gray-600 mt-1">Overview of your Apigee Edge to Apigee X migration progress</p>
        </div>
        <Button 
          onClick={handleRefresh} 
          className="flex items-center space-x-2 btn-animation"
          data-testid="refresh-dashboard"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <Card className="card-hover glass-effect border-0">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Total Analyses</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {dashboardStats?.total_analyses || 0}
            </div>
            <Progress value={100} className="mt-2" />
          </CardContent>
        </Card>

        <Card className="card-hover glass-effect border-0">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Avg. Complexity</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {dashboardStats?.avg_complexity || 0}%
            </div>
            <Progress value={dashboardStats?.avg_complexity || 0} className="mt-2" />
          </CardContent>
        </Card>

        <Card className="card-hover glass-effect border-0">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Total Migrations</CardTitle>
            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {migrationStats?.total || 0}
            </div>
            <Progress value={75} className="mt-2 [&>div]:bg-purple-500" />
          </CardContent>
        </Card>

        <Card className="card-hover glass-effect border-0">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">Completed</CardTitle>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {migrationStats?.completed || 0}
            </div>
            <Progress value={75} className="mt-2 [&>div]:bg-green-500" />
          </CardContent>
        </Card>

        <Card className="card-hover glass-effect border-0">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-700">In Progress</CardTitle>
            <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse"></div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {migrationStats?.in_progress || 0}
            </div>
            <Progress value={50} className="mt-2 [&>div]:bg-blue-500" />
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Complexity Distribution Chart */}
        <Card className="glass-effect border-0">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-gray-900">Migration Complexity Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={complexityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {complexityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Migration Status Chart */}
        <Card className="glass-effect border-0">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-gray-900">Migration Status</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Completed', count: migrationStats?.completed || 0 },
                    { name: 'In Progress', count: migrationStats?.in_progress || 0 },
                    { name: 'Failed', count: migrationStats?.failed || 0 }
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => percent > 0 ? `${name} ${(percent * 100).toFixed(0)}%` : ''}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  <Cell fill="#10B981" />
                  <Cell fill="#3B82F6" />
                  <Cell fill="#EF4444" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top Policies Chart */}
        <Card className="glass-effect border-0">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-gray-900">Most Common Policies</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dashboardStats?.top_policies?.slice(0, 6) || []}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="policy" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Analyses */}
      <Card className="glass-effect border-0">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">Recent Analyses</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {dashboardStats?.recent_analyses?.length > 0 ? (
              dashboardStats.recent_analyses.map((analysis, index) => (
                <div
                  key={analysis.id}
                  className="flex items-center justify-between p-4 bg-white/50 rounded-xl border border-gray-100 hover:shadow-md transition-all duration-200"
                  data-testid={`recent-analysis-${index}`}
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">
                      {analysis.proxy_name?.charAt(0) || 'P'}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{analysis.proxy_name}</h3>
                      <p className="text-sm text-gray-600">
                        {analysis.policy_count} policies • {analysis.migration_effort}
                      </p>
                      <p className="text-xs text-gray-500 flex items-center mt-1">
                        <Clock className="w-3 h-3 mr-1" />
                        {formatDateTime(analysis.analyzed_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900">
                        {Math.round(analysis.complexity_score)}%
                      </div>
                      <Progress value={analysis.complexity_score} className="w-20 mt-1" />
                    </div>
                    <div className="space-y-1">
                      <Badge className={getComplexityColor(analysis.complexity_level)}>
                        {analysis.complexity_level}
                      </Badge>
                      <Badge className={getStatusColor(analysis.status)}>
                        {analysis.status}
                      </Badge>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                  <TrendingUp className="w-12 h-12 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No analyses yet</h3>
                <p className="text-gray-600 mb-6">Upload your first Apigee proxy to get started with migration analysis.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;