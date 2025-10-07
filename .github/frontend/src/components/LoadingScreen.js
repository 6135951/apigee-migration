import React from 'react';

const LoadingScreen = ({ message = "Loading Apigee Migration Tool..." }) => {
  return (
    <div className="fixed inset-0 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center z-50">
      <div className="text-center space-y-8">
        {/* Logo with subtle animation */}
        <div className="flex justify-center">
          <div className="relative">
            <img 
              src="/images/thomson-reuters-logo.png" 
              alt="Thomson Reuters" 
              className="h-16 w-auto opacity-90 animate-pulse"
            />
            {/* Subtle glow effect */}
            <div className="absolute inset-0 bg-orange-200/20 rounded-full blur-xl animate-pulse"></div>
          </div>
        </div>
        
        {/* Loading message */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-gray-900">Apigee Migration Tool</h2>
          <p className="text-gray-600 text-lg">{message}</p>
          
          {/* Loading dots animation */}
          <div className="flex justify-center space-x-2">
            <div className="w-3 h-3 bg-orange-500 rounded-full animate-bounce"></div>
            <div className="w-3 h-3 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-3 h-3 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
        </div>
        
        {/* Optional progress indicator */}
        <div className="w-64 bg-gray-200 rounded-full h-2 mx-auto">
          <div className="bg-gradient-to-r from-orange-400 to-orange-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;