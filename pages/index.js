import { useState, useEffect } from 'react';
import { auth, db } from '@/lib/firebase';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { collection, query, where, orderBy, onSnapshot, addDoc, updateDoc, doc, deleteDoc } from 'firebase/firestore';

import Layout from '@/components/Layout';
import LoginModal from '@/components/LoginModal';
import Dashboard from '@/components/Dashboard';
import BusinessProfile from '@/components/BusinessProfile';
import CampaignManager from '@/components/CampaignManager';
import DraftReview from '@/components/DraftReview';

export default function Home() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({
    activeCampaigns: 0,
    runningJobs: 0,
    readyDrafts: 0,
    emailsSent: 0
  });

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const updateStats = async () => {
    if (!user) return;

    try {
      // Get campaigns count
      const campaignsQuery = query(
        collection(db, 'campaigns'),
        where('userId', '==', user.uid),
        where('status', '==', 'active')
      );
      
      const jobsQuery = query(
        collection(db, 'jobs'),
        where('userId', '==', user.uid),
        where('status', '==', 'running')
      );

      const draftsQuery = query(
        collection(db, 'drafts'),
        where('userId', '==', user.uid),
        where('status', '==', 'draft')
      );

      const sentQuery = query(
        collection(db, 'drafts'),
        where('userId', '==', user.uid),
        where('status', '==', 'sent')
      );

      // In a real app, you'd use onSnapshot for real-time updates
      // For simplicity, we'll set mock stats
      setStats({
        activeCampaigns: 1,
        runningJobs: 1,
        readyDrafts: 2,
        emailsSent: 0
      });
    } catch (error) {
      console.error('Error updating stats:', error);
    }
  };

  useEffect(() => {
    if (user) {
      updateStats();
    }
  }, [user]);

  const handleLogout = async () => {
    if (confirm('Are you sure you want to logout?')) {
      try {
        await signOut(auth);
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="loading"></div>
      </div>
    );
  }

  if (!user) {
    return <LoginModal />;
  }

  return (
    <Layout 
      user={user} 
      activeTab={activeTab} 
      onTabChange={setActiveTab}
      onLogout={handleLogout}
      stats={stats}
    >
      {activeTab === 'dashboard' && <Dashboard user={user} />}
      {activeTab === 'profiles' && <BusinessProfile user={user} />}
      {activeTab === 'campaigns' && <CampaignManager user={user} />}
      {activeTab === 'drafts' && <DraftReview user={user} />}
    </Layout>
  );
}
