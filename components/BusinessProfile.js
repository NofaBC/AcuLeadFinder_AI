import { useState, useEffect } from 'react';
import { db } from '@/lib/firebase';
import { collection, addDoc, query, where, onSnapshot, deleteDoc, doc, getDocs } from 'firebase/firestore';

export default function BusinessProfile({ user }) {
  const [profiles, setProfiles] = useState([]);
  const [showWizard, setShowWizard] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    companyName: '',
    industry: '',
    services: [''],
    targetCustomers: '',
    geography: '',
    valueProposition: '',
    offers: ''
  });

  // Load profiles with better error handling
  useEffect(() => {
    if (!user) {
      setProfiles([]);
      return;
    }

    console.log('Loading profiles for user:', user.uid);
    
    const loadProfiles = async () => {
      try {
        setError('');
        const q = query(
          collection(db, 'businessProfiles'),
          where('userId', '==', user.uid)
        );

        // Test with getDocs first (one-time read)
        const querySnapshot = await getDocs(q);
        const profilesData = querySnapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
        
        console.log('Profiles loaded:', profilesData);
        setProfiles(profilesData);

        // Then set up real-time listener
        const unsubscribe = onSnapshot(
          q,
          (snapshot) => {
            const updatedProfiles = snapshot.docs.map(doc => ({
              id: doc.id,
              ...doc.data()
            }));
            console.log('Real-time update:', updatedProfiles);
            setProfiles(updatedProfiles);
          },
          (error) => {
            console.error('Firestore listener error:', error);
            setError('Failed to load profiles: ' + error.message);
          }
        );

        return unsubscribe;
      } catch (error) {
        console.error('Error loading profiles:', error);
        setError('Error loading profiles: ' + error.message);
      }
    };

    loadProfiles();
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const addService = () => {
    setFormData(prev => ({
      ...prev,
      services: [...prev.services, '']
    }));
  };

  const updateService = (index, value) => {
    setFormData(prev => ({
      ...prev,
      services: prev.services.map((service, i) => i === index ? value : service)
    }));
  };

  const removeService = (index) => {
    if (formData.services.length > 1) {
      setFormData(prev => ({
        ...prev,
        services: prev.services.filter((_, i) => i !== index)
      }));
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    if (!user) {
      setError('No user logged in');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      console.log('Saving profile for user:', user.uid);
      
      const profileData = {
        ...formData,
        userId: user.uid,
        createdAt: new Date(),
        services: formData.services.filter(service => service.trim() !== ''),
        offers: formData.offers.split(',').map(offer => offer.trim()).filter(offer => offer)
      };

      console.log('Profile data to save:', profileData);

      const docRef = await addDoc(collection(db, 'businessProfiles'), profileData);
      console.log('Profile saved with ID:', docRef.id);

      // Reset form and close wizard
      setFormData({
        companyName: '',
        industry: '',
        services: [''],
        targetCustomers: '',
        geography: '',
        valueProposition: '',
        offers: ''
      });
      setShowWizard(false);
      
      alert('Business profile saved successfully!');
    } catch (error) {
      console.error('Error saving profile:', error);
      setError('Error saving profile: ' + error.message);
      alert('Error saving profile: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProfile = async (profileId) => {
    if (confirm('Are you sure you want to delete this profile?')) {
      try {
        await deleteDoc(doc(db, 'businessProfiles', profileId));
        console.log('Profile deleted:', profileId);
      } catch (error) {
        console.error('Error deleting profile:', error);
        setError('Error deleting profile: ' + error.message);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex items-center">
            <i className="fas fa-exclamation-triangle text-red-500 mr-2"></i>
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Website Analysis Card */}
        <div className="border rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-3">
            <i className="fas fa-globe text-green-600 mr-2"></i>
            Quick Website Analysis
          </h3>
          <form className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Website URL
              </label>
              <input 
                type="url" 
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="https://example.com"
              />
            </div>
            <button 
              type="button"
              className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition duration-200"
            >
              <i className="fas fa-search mr-2"></i>
              Analyze Website
            </button>
          </form>
        </div>

        {/* Manual Profile Creation */}
        <div className="border rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-3">
            <i className="fas fa-edit text-purple-600 mr-2"></i>
            Manual Profile Setup
          </h3>
          <button 
            onClick={() => setShowWizard(true)}
            className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition duration-200"
          >
            <i className="fas fa-plus-circle mr-2"></i>
            Create Business Profile
          </button>
          <p className="text-xs text-gray-500 mt-2 text-center">
            For businesses without websites or custom needs
          </p>
        </div>
      </div>

      {/* Active Profiles List */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">Active Business Profiles</h3>
        {profiles.length === 0 ? (
          <div className="text-center text-gray-500 py-8 border rounded-lg">
            <i className="fas fa-building text-3xl mb-2 opacity-50"></i>
            <p>No business profiles yet</p>
            <p className="text-sm">Create your first profile to enable context-aware lead generation</p>
          </div>
        ) : (
          <div className="space-y-3">
            {profiles.map(profile => (
              <div key={profile.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="font-semibold">{profile.companyName}</h4>
                  <span className="status-badge status-completed">Active</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{profile.industry}</p>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Services: {profile.services?.slice(0, 2).join(', ')}{profile.services?.length > 2 ? '...' : ''}</span>
                  <div>
                    <button className="text-blue-600 hover:text-blue-800 mr-2">
                      <i className="fas fa-edit mr-1"></i>Edit
                    </button>
                    <button 
                      onClick={() => handleDeleteProfile(profile.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <i className="fas fa-trash mr-1"></i>Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Profile Wizard Modal */}
      {showWizard && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Create Business Profile</h3>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[70vh]">
              <form onSubmit={handleSaveProfile}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Company Name *
                    </label>
                    <input
                      type="text"
                      name="companyName"
                      value={formData.companyName}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Your Company LLC"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Industry *
                    </label>
                    <input
                      type="text"
                      name="industry"
                      value={formData.industry}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Digital Marketing, Consulting, etc."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Core Services *
                    </label>
                    {formData.services.map((service, index) => (
                      <div key={index} className="flex space-x-2 mb-2">
                        <input
                          type="text"
                          value={service}
                          onChange={(e) => updateService(index, e.target.value)}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          placeholder={`Service ${index + 1}`}
                          required
                        />
                        {formData.services.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeService(index)}
                            className="px-3 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200"
                          >
                            <i className="fas fa-times"></i>
                          </button>
                        )}
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={addService}
                      className="mt-2 px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm"
                    >
                      <i className="fas fa-plus mr-1"></i> Add Service
                    </button>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Target Customers
                    </label>
                    <input
                      type="text"
                      name="targetCustomers"
                      value={formData.targetCustomers}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Small businesses, startups, enterprises"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Geographic Focus
                    </label>
                    <input
                      type="text"
                      name="geography"
                      value={formData.geography}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="National, Local, Specific regions"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Unique Value Proposition
                    </label>
                    <textarea
                      name="valueProposition"
                      value={formData.valueProposition}
                      onChange={handleInputChange}
                      rows="3"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="What makes your business unique?"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Key Offers/Promotions
                    </label>
                    <textarea
                      name="offers"
                      value={formData.offers}
                      onChange={handleInputChange}
                      rows="2"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Free consultation, special discounts, etc."
                    />
                  </div>
                </div>
              </form>
            </div>
            
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end space-x-3">
              <button
                onClick={() => setShowWizard(false)}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition duration-200"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveProfile}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200 disabled:opacity-50"
              >
                {loading ? (
                  <div className="loading mx-auto"></div>
                ) : (
                  <>
                    <i className="fas fa-save mr-2"></i>Save Profile
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .loading {
          display: inline-block;
          width: 16px;
          height: 16px;
          border: 2px solid #f3f3f3;
          border-top: 2px solid #3498db;
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
