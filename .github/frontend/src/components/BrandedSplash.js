import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';

const BrandedSplash = ({ onComplete }) => {
  const [isVisible, setIsVisible] = useState(true);
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    // Auto-dismiss after 3 seconds
    const timer = setTimeout(() => {
      handleClose();
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  const handleClose = () => {
    setFadeOut(true);
    setTimeout(() => {
      setIsVisible(false);
      if (onComplete) onComplete();
    }, 500);
  };

  if (!isVisible) return null;

  return (
    <div className={`fixed inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 flex items-center justify-center z-50 transition-opacity duration-500 ${fadeOut ? 'opacity-0' : 'opacity-100'}`}>
      <div className="text-center space-y-12 px-8">
        {/* Main Logo - Removed per user request */}
        <div className="flex justify-center">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-400 to-indigo-600 rounded-xl flex items-center justify-center">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
        
        {/* Welcome Content */}
        <div className="space-y-6">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold text-white">Apigee Migration Tool</h1>
            <p className="text-xl text-blue-200">Edge to Apigee X Migration Assistant</p>
          </div>
          
          <div className="space-y-4 text-white/80">
            <p className="text-lg">Streamline your API migration journey</p>
            <div className="flex justify-center space-x-8 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>Automated Analysis</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span>AI-Powered Insights</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <span>Seamless Migration</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Action Button */}
        <div className="space-y-4">
          <Button 
            onClick={handleClose}
            className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-3 text-lg font-medium rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
          >
            Get Started
          </Button>
          <p className="text-xs text-blue-300/60">Click anywhere or wait to continue</p>
        </div>
      </div>
      
      {/* Click to dismiss overlay */}
      <div 
        className="absolute inset-0 cursor-pointer"
        onClick={handleClose}
      />
    </div>
  );
};

export default BrandedSplash;