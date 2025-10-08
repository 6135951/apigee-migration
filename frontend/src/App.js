import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Import components
import Dashboard from './components/Dashboard';
import ProxyUpload from './components/ProxyUpload';
import ProxyAnalysis from './components/ProxyAnalysis';
import Migration from './components/Migration';
import ApiDocumentation from './components/ApiDocumentation';
import NavigationMenu from './components/NavigationMenu';
import BrandedSplash from './components/BrandedSplash';
import LoadingScreen from './components/LoadingScreen';
import { Toaster } from './components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [analysisData, setAnalysisData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showSplash, setShowSplash] = useState(false); // Disabled splash screen
  const [appLoading, setAppLoading] = useState(false); // Disabled loading screen

  // Load dashboard data
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/analyses`);
      setAnalysisData(response.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleProxyUploaded = (newAnalysis) => {
    setAnalysisData(prev => [newAnalysis, ...prev]);
    setCurrentPage('dashboard');
  };

  // Splash and loading screens disabled per user request

  return (
    <div className="App">
      <BrowserRouter>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex flex-col">
          {/* Header */}
          <header className="bg-white/90 backdrop-blur-md shadow-lg border-b border-white/20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-4">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-3">
                    <img 
                      src="/images/thomson-reuters-logo.png" 
                      alt="Thomson Reuters" 
                      className="h-8 w-auto cursor-pointer hover:opacity-80 transition-opacity"
                      onClick={() => setCurrentPage('dashboard')}
                      title="Go to Dashboard"
                    />
                  </div>
                  <div className="border-l border-gray-300 pl-3 ml-3">
                    <h1 className="text-2xl font-bold text-gray-900">Apigee Migration Tool</h1>
                    <p className="text-sm text-gray-600">Edge to Apigee X Migration Assistant</p>
                  </div>
                </div>
                
                <NavigationMenu currentPage={currentPage} setCurrentPage={setCurrentPage} />
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
            <Routes>
              <Route path="/" element={
                currentPage === 'dashboard' ? 
                  <Dashboard 
                    analysisData={analysisData}
                    loading={loading}
                    onRefresh={loadDashboardData}
                  /> :
                currentPage === 'upload' ?
                  <ProxyUpload onProxyUploaded={handleProxyUploaded} /> :
                currentPage === 'analysis' ?
                  <ProxyAnalysis analysisData={analysisData} /> :
                currentPage === 'migration' ?
                  <Migration analysisData={analysisData} /> :
                currentPage === 'documentation' ?
                  <ApiDocumentation /> :
                  <Navigate to="/" replace />
              } />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="bg-white/70 backdrop-blur-sm border-t border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <div className="flex justify-between items-center">
                <div className="flex items-center space-x-4">
                  <img 
                    src="/images/thomson-reuters-logo.png" 
                    alt="Thomson Reuters" 
                    className="h-6 w-auto opacity-60"
                  />
                  <div className="text-sm text-gray-600">
                    <p>© 2024 Thomson Reuters. All rights reserved.</p>
                  </div>
                </div>
                <div className="flex items-center space-x-6 text-sm text-gray-600">
                  <span>Apigee Migration Tool v1.0</span>
                  <span>•</span>
                  <span>Edge to Apigee X</span>
                </div>
              </div>
            </div>
          </footer>
        </div>
        
        <Toaster position="top-right" richColors />
      </BrowserRouter>
    </div>
  );
}

export default App;