// components/ProfileManager.js
'use client';
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function ProfileManager({ currentAnalysis, currentLeadData, analysisType }) {
  const [profiles, setProfiles] = useState([]);
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [profileName, setProfileName] = useState('');
  const [tags, setTags] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const { currentUser } = useAuth();

  // Load profiles from localStorage instead of Firestore
  useEffect(() => {
    const savedProfiles = localStorage.getItem('avicenna_profiles');
    if (savedProfiles) {
      setProfiles(JSON.parse(savedProfiles));
    }
  }, []);

  const handleSaveProfile = async () => {
    if (!profileName.trim()) {
      setMessage('Please enter a profile name');
      return;
    }

    if (!currentAnalysis || !currentLeadData) {
      setMessage('No analysis data to save');
      return;
    }

    setLoading(true);
    
    try {
      const newProfile = {
        id: `profile_${Date.now()}`,
        name: profileName,
        leadData: currentLeadData,
        analysis: currentAnalysis,
        analysisType: analysisType,
        tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        createdAt: new Date().toISOString()
      };

      const updatedProfiles = [newProfile, ...profiles];
      setProfiles(updatedProfiles);
      localStorage.setItem('avicenna_profiles', JSON.stringify(updatedProfiles));

      setMessage('Profile saved successfully!');
      setProfileName('');
      setTags('');
      setShowSaveForm(false);
    } catch (error) {
      setMessage('Error saving profile: ' + error.message);
    }
    
    setLoading(false);
  };

  const handleDeleteProfile = async (profileId) => {
    if (!confirm('Are you sure you want to delete this profile?')) return;

    const updatedProfiles = profiles.filter(p => p.id !== profileId);
    setProfiles(updatedProfiles);
    localStorage.setItem('avicenna_profiles', JSON.stringify(updatedProfiles));
    setMessage('Profile deleted successfully!');
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 mt-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold text-gray-800">Saved Patient Profiles</h2>
        <button
          onClick={() => setShowSaveForm(!showSaveForm)}
          className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition duration-200"
        >
          {showSaveForm ? 'Cancel' : 'Save Current Analysis'}
        </button>
      </div>

      {message && (
        <div className={`p-3 rounded-lg mb-4 ${
          message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
        }`}>
          {message}
        </div>
      )}

      {showSaveForm && (
        <div className="bg-blue-50 rounded-lg p-4 mb-6 border border-blue-200">
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
            <span className="text-blue-600 mr-2">💾</span>
            Save Patient Profile
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Profile Name *
              </label>
              <input
                type="text"
                value={profileName}
                onChange={(e) => setProfileName(e.target.value)}
                placeholder="e.g., Chronic Pain Patient - High Priority"
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Medical Tags
              </label>
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="e.g., chronic-pain, regenerative-candidate, high-urgency"
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={handleSaveProfile}
              disabled={loading || !profileName.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-2 px-4 rounded-lg"
            >
              {loading ? 'Saving...' : 'Save Patient Profile'}
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Loading profiles...</p>
        </div>
      ) : profiles.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No saved profiles yet. Analyze a patient lead and save it to get started!
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {profiles.map(profile => (
            <div key={profile.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-gray-800 truncate">{profile.name}</h3>
                <button
                  onClick={() => handleDeleteProfile(profile.id)}
                  className="text-red-500 hover:text-red-700 text-sm"
                >
                  Delete
                </button>
              </div>
              
              <p className="text-sm text-gray-600 mb-2 line-clamp-3">
                {profile.analysis.substring(0, 100)}...
              </p>
              
              <div className="flex flex-wrap gap-1 mb-2">
                {profile.tags?.map((tag, index) => (
                  <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                    {tag}
                  </span>
                ))}
              </div>
              
              <div className="flex justify-between items-center text-xs text-gray-500">
                <span>{profile.analysisType}</span>
                <span>{formatDate(profile.createdAt)}</span>
              </div>
              
              <button
                onClick={() => {
                  alert(`Viewing profile: ${profile.name}\n\nAnalysis: ${profile.analysis}`);
                }}
                className="w-full mt-3 bg-gray-100 hover:bg-gray-200 text-gray-800 text-sm font-medium py-2 rounded-lg transition duration-200"
              >
                View Details
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
