// components/ProfileManager.js - Updated to work without Firebase
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

  // ... rest of the component remains the same
