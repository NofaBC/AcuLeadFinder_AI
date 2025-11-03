const functions = require('firebase-functions');
const admin = require('firebase-admin');
const express = require('express');
const cors = require('cors');

admin.initializeApp();
const app = express();
const db = admin.firestore();

// Middleware
app.use(cors({ origin: true }));
app.use(express.json());

// Authentication middleware
const authenticate = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split('Bearer ')[1];
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }
    
    const decodedToken = await admin.auth().verifyIdToken(token);
    req.user = decodedToken;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'online', 
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// Presets endpoint
app.get('/presets', authenticate, async (req, res) => {
  try {
    const presets = {
      acu: 'AcuLeadFinder (Acupuncture)',
      ap: 'APLeadFinder (All-purpose)',
      local: 'Local Service Finder',
      saas: 'SaaS Lead Generator',
      ecommerce: 'E-commerce Partnership Finder'
    };
    res.json({ presets });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Business Profiles endpoints
app.post('/business-profiles', authenticate, async (req, res) => {
  try {
    const profileData = {
      ...req.body,
      userId: req.user.uid,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    };
    
    const docRef = await db.collection('businessProfiles').add(profileData);
    res.json({ id: docRef.id, ...profileData });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/business-profiles', authenticate, async (req, res) => {
  try {
    const snapshot = await db.collection('businessProfiles')
      .where('userId', '==', req.user.uid)
      .get();
    
    const profiles = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    
    res.json({ profiles });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Campaigns endpoints
app.post('/campaigns', authenticate, async (req, res) => {
  try {
    const campaignData = {
      ...req.body,
      userId: req.user.uid,
      status: 'active',
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      stats: {
        leadsGenerated: 0,
        emailsSent: 0,
        repliesReceived: 0
      }
    };
    
    const docRef = await db.collection('campaigns').add(campaignData);
    res.json({ id: docRef.id, ...campaignData });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/campaigns', authenticate, async (req, res) => {
  try {
    const snapshot = await db.collection('campaigns')
      .where('userId', '==', req.user.uid)
      .get();
    
    const campaigns = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    
    res.json({ campaigns });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Jobs endpoints
app.post('/jobs', authenticate, async (req, res) => {
  try {
    const jobData = {
      ...req.body,
      userId: req.user.uid,
      status: 'running',
      progress: 0,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      startedAt: admin.firestore.FieldValue.serverTimestamp()
    };
    
    const docRef = await db.collection('jobs').add(jobData);
    
    // Start the background job processing
    await processJob(docRef.id, jobData);
    
    res.json({ id: docRef.id, ...jobData });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

async function processJob(jobId, jobData) {
  // This would contain your actual lead generation logic
  // For now, we'll simulate the process
  const batch = db.batch();
  
  for (let i = 0; i < jobData.plannedCount; i++) {
    const draftData = {
      jobId: jobId,
      campaignId: jobData.campaignId,
      userId: jobData.userId,
      status: 'draft',
      leadName: `Lead ${i + 1}`,
      leadCompany: `Company ${i + 1}`,
      subject: `Partnership Opportunity`,
      content: `This is a generated draft for lead ${i + 1}`,
      createdAt: admin.firestore.FieldValue.serverTimestamp()
    };
    
    const draftRef = db.collection('drafts').doc();
    batch.set(draftRef, draftData);
  }
  
  await batch.commit();
  
  // Update job status
  await db.collection('jobs').doc(jobId).update({
    status: 'completed',
    completedAt: admin.firestore.FieldValue.serverTimestamp(),
    progress: 100
  });
}

// Drafts endpoints
app.get('/drafts', authenticate, async (req, res) => {
  try {
    const { status } = req.query;
    let query = db.collection('drafts').where('userId', '==', req.user.uid);
    
    if (status) {
      query = query.where('status', '==', status);
    }
    
    const snapshot = await query.get();
    const drafts = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    
    res.json({ drafts });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.patch('/drafts/:id', authenticate, async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = {
      ...req.body,
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    };
    
    await db.collection('drafts').doc(id).update(updateData);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Website analysis endpoint
app.post('/analyze-website', authenticate, async (req, res) => {
  try {
    const { url } = req.body;
    
    // This would contain your actual website analysis logic
    // For now, return mock data
    const analysisResult = {
      companyName: 'Extracted Company Name',
      industry: 'Detected Industry',
      services: ['Service 1', 'Service 2', 'Service 3'],
      targetCustomers: 'Small businesses, enterprises',
      geography: 'National',
      valueProposition: 'Extracted value proposition',
      offers: ['Free consultation', 'Special discount']
    };
    
    res.json(analysisResult);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Export the Express app as Firebase Functions
exports.api = functions.https.onRequest(app);

// Background function for scheduled jobs
exports.scheduledJobProcessor = functions.pubsub
  .schedule('every 5 minutes')
  .onRun(async (context) => {
    // Process pending jobs
    const pendingJobs = await db.collection('jobs')
      .where('status', '==', 'running')
      .get();
    
    // Process each job
    pendingJobs.forEach(async (jobDoc) => {
      await processJob(jobDoc.id, jobDoc.data());
    });
    
    return null;
  });
