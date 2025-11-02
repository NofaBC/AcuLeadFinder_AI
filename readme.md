# Environment Setup Guide

## Quick Start

1. Copy `.env.example` to `.env`
2. Fill in your actual API keys and configuration
3. For Vercel deployment, add these variables in your project settings

## Required Variables

### OpenAI
- `OPENAI_API_KEY`: Get from https://platform.openai.com/api-keys

### SendGrid  
- `SENDGRID_API_KEY`: Get from https://app.sendgrid.com/settings/api_keys
- `ALLOWED_SENDER`: Must be a verified sender in SendGrid

### Firebase
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_CLIENT_EMAIL`: Service account email from Firebase console
- `FIREBASE_PRIVATE_KEY`: Service account private key from Firebase console

## Optional Variables

Most variables have sensible defaults. The only truly required ones are:
- `OPENAI_API_KEY`
- `SENDGRID_API_KEY` 
- Firebase variables (if using Firestore persistence)

## Vercel Deployment

Add environment variables in:
1. Go to your Vercel project
2. Settings → Environment Variables
3. Add each variable from `.env.example`

## Local Development

```bash
cp .env.example .env
# Edit .env with your values
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn api.index:app --reload
