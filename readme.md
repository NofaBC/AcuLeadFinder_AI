# Seekan-LG - Autonomous Lead Generation Agent

## Overview
Seekan-LG is an intelligent, autonomous AI-powered lead generation agent that helps businesses discover and connect with potential clients through personalized, compliant outreach. The system combines AI-driven lead discovery with human-in-the-loop approval for optimal results.

## 🚀 Features

### Core Capabilities
- **🤖 Autonomous Operation** - AI-driven lead discovery and outreach
- **🎯 Multi-Vertical Support** - Configurable for different industries via JSON presets
- **👥 Human-in-the-Loop** - Draft approval workflow for quality control
- **📧 Email Automation** - SendGrid integration for reliable delivery
- **🛡️ Safety First** - Comprehensive guardrails and compliance measures
- **📊 Real-time Dashboard** - Professional operator console for monitoring

### Technical Features
- **⚡ FastAPI Backend** - High-performance Python API
- **🔒 JWT Authentication** - Secure operator access
- **📱 Responsive Design** - Works on all devices
- **🔄 Real-time Updates** - Live dashboard with auto-refresh
- **🎨 Professional UI** - Clean, intuitive operator interface

## 🏗️ Architecture

## 🚀 Quick Start

### 1. Access the System
Visit your deployed Vercel URL to access the Seekan-LG operator console.

### 2. Login Credentials

### 3. Basic Workflow
1. **Create Campaign** → Select from available presets (acu/apl)
2. **Start Job** → Launch autonomous lead generation
3. **Review Drafts** → Approve or modify generated emails
4. **Send Outreach** → Deploy approved campaigns

## 📋 API Endpoints

### Core Endpoints
- `GET /` - API status and information
- `GET /health` - Health check
- `GET /presets` - List available configurations
- `POST /campaigns` - Create new campaigns
- `POST /jobs` - Start lead generation jobs
- `GET /jobs/{id}/drafts` - Review generated drafts
- `POST /drafts/{id}/approve` - Approve drafts for sending
- `POST /drafts/{id}/send` - Send approved drafts

### Preset Configurations
- **acu** - Acupuncture services (AcuLeadFinder)
- **apl** - Generic B2B services (APLeadFinder)

## 🔧 Configuration

### Environment Variables
```env
# Required
OPENAI_API_KEY=your-openai-key
SENDGRID_API_KEY=your-sendgrid-key
FIREBASE_PROJECT_ID=your-firebase-project

# Optional with defaults
SEND_CAP_PER_RUN=20
DAILY_SEND_CAP=200
DEFAULT_MODEL=gpt-4o
