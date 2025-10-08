import React from 'react';
import { Button } from './ui/button';

const NavigationMenu = ({ currentPage, setCurrentPage }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z' },
    { id: 'upload', label: 'Upload Proxy', icon: 'M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m-9 4v10a2 2 0 002 2h8a2 2 0 002-2V8m-9 0h10m-9 0l-2-2m11 2l2-2' },
    { id: 'analysis', label: 'Analysis Results', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
    { id: 'migration', label: 'Migration', icon: 'M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z' },
    { id: 'documentation', label: 'API Docs & Testing', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' }
  ];

  return (
    <nav className="flex space-x-1 bg-gray-100 p-1 rounded-xl">
      {menuItems.map((item) => (
        <Button
          key={item.id}
          variant={currentPage === item.id ? "default" : "ghost"}
          onClick={() => setCurrentPage(item.id)}
          className={`
            flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200
            ${currentPage === item.id 
              ? 'bg-white shadow-md text-blue-700 font-medium' 
              : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
            }
          `}
          data-testid={`nav-${item.id}`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
          </svg>
          <span className="text-sm font-medium">{item.label}</span>
        </Button>
      ))}
    </nav>
  );
};

export default NavigationMenu;