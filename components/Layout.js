import { useState, useEffect } from 'react';

export default function Layout({ user, activeTab, onTabChange, onLogout, stats, children }) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">
                <i className="fas fa-robot text-blue-600 mr-3"></i>
                {process.env.NEXT_PUBLIC_APP_NAME || 'Seekan-LG'}
              </h1>
              <nav className="flex space-x-4">
                {['dashboard', 'profiles', 'campaigns', 'drafts'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => onTabChange(tab)}
                    className={`px-3 py-2 rounded-md text-sm font-medium capitalize ${
                      activeTab === tab
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                <i className="fas fa-check-circle text-green-500 mr-1"></i>
                API Online
              </div>
              <div className="text-xs text-gray-400">
                {currentTime.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">
                {user.email}
              </div>
              <button
                onClick={onLogout}
                className="px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition duration-200 text-sm"
              >
                <i className="fas fa-sign-out-alt mr-1"></i>Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Overview */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { label: 'Active Campaigns', value: stats.activeCampaigns, icon: 'bullseye', color: 'blue' },
            { label: 'Running Jobs', value: stats.runningJobs, icon: 'tasks', color: 'green' },
            { label: 'Drafts Ready', value: stats.readyDrafts, icon: 'envelope', color: 'purple' },
            { label: 'Emails Sent', value: stats.emailsSent, icon: 'paper-plane', color: 'orange' }
          ].map((stat) => (
            <div key={stat.label} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className={`p-3 rounded-full bg-${stat.color}-100 text-${stat.color}-600`}>
                  <i className={`fas fa-${stat.icon} text-xl`}></i>
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-500">{stat.label}</h3>
                  <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Main Content */}
        {children}
      </div>

      {/* Footer */}
      <footer className="mt-12 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <h3 className="text-lg font-semibold text-gray-900">
                {process.env.NEXT_PUBLIC_APP_NAME || 'Seekan-LG'}
              </h3>
              <p className="text-sm text-gray-600">Autonomous Lead Generation Agent</p>
              <p className="text-xs text-gray-500 mt-1">Created by NOFA Business Consulting</p>
            </div>
            <div className="text-center md:text-right">
              <p className="text-sm text-gray-600">
                <i className="fas fa-map-marker-alt mr-1"></i>
                Gaithersburg, MD
              </p>
              <p className="text-xs text-gray-500 mt-1">
                &copy; 2025 NOFA Business Consulting. All rights reserved.
              </p>
            </div>
          </div>
        </div>
      </footer>

      <style jsx>{`
        .loading {
          display: inline-block;
          width: 20px;
          height: 20px;
          border: 3px solid #f3f3f3;
          border-top: 3px solid #3498db;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
