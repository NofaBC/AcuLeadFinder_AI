// lib/firestore.js
import { db } from './firebase';
import { 
  collection, 
  doc, 
  setDoc, 
  getDoc, 
  getDocs, 
  updateDoc, 
  deleteDoc, 
  query, 
  where, 
  orderBy,
  serverTimestamp 
} from 'firebase/firestore';
import { auth } from './firebase';

// Save a lead profile
export async function saveLeadProfile(profileData) {
  try {
    const user = auth.currentUser;
    if (!user) throw new Error('User must be authenticated to save profiles');

    const profileId = profileData.id || `profile_${Date.now()}`;
    const profileRef = doc(db, 'users', user.uid, 'leadProfiles', profileId);

    const profile = {
      id: profileId,
      ...profileData,
      userId: user.uid,
      createdAt: serverTimestamp(),
      updatedAt: serverTimestamp()
    };

    await setDoc(profileRef, profile);
    return { success: true, id: profileId };
  } catch (error) {
    console.error('Error saving profile:', error);
    return { success: false, error: error.message };
  }
}

// Get all profiles for current user
export async function getUserProfiles() {
  try {
    const user = auth.currentUser;
    if (!user) throw new Error('User not authenticated');

    const profilesRef = collection(db, 'users', user.uid, 'leadProfiles');
    const q = query(profilesRef, orderBy('createdAt', 'desc'));
    const snapshot = await getDocs(q);
    
    const profiles = [];
    snapshot.forEach(doc => {
      profiles.push({ id: doc.id, ...doc.data() });
    });
    
    return { success: true, profiles };
  } catch (error) {
    console.error('Error fetching profiles:', error);
    return { success: false, error: error.message };
  }
}

// Get a specific profile
export async function getProfile(profileId) {
  try {
    const user = auth.currentUser;
    if (!user) throw new Error('User not authenticated');

    const profileRef = doc(db, 'users', user.uid, 'leadProfiles', profileId);
    const snapshot = await getDoc(profileRef);
    
    if (snapshot.exists()) {
      return { success: true, profile: snapshot.data() };
    } else {
      return { success: false, error: 'Profile not found' };
    }
  } catch (error) {
    console.error('Error fetching profile:', error);
    return { success: false, error: error.message };
  }
}

// Update a profile
export async function updateProfile(profileId, updates) {
  try {
    const user = auth.currentUser;
    if (!user) throw new Error('User not authenticated');

    const profileRef = doc(db, 'users', user.uid, 'leadProfiles', profileId);
    
    await updateDoc(profileRef, {
      ...updates,
      updatedAt: serverTimestamp()
    });
    
    return { success: true };
  } catch (error) {
    console.error('Error updating profile:', error);
    return { success: false, error: error.message };
  }
}

// Delete a profile
export async function deleteProfile(profileId) {
  try {
    const user = auth.currentUser;
    if (!user) throw new Error('User not authenticated');

    const profileRef = doc(db, 'users', user.uid, 'leadProfiles', profileId);
    await deleteDoc(profileRef);
    
    return { success: true };
  } catch (error) {
    console.error('Error deleting profile:', error);
    return { success: false, error: error.message };
  }
}
