# AcuLeadFinder AI™  

Local lead discovery & compliant outreach for acupuncture clinics.

---

## Overview
AcuLeadFinder AI™ helps clinics find nearby prospects and send warm, compliant outreach.  
This repo currently ships a **SaaS-ready `index.html`** (no build step) and is designed to pair with simple API routes (Vercel serverless) when you’re ready.

- Frontend: vanilla HTML/CSS/JS (drop-in)
- Backend (optional, recommended): Vercel Serverless API routes
- Email (optional): SendGrid API
- Storage (optional): Vercel Postgres (for saving config & metrics)

---

## Features
- Dashboard (snapshot + recent leads table)
- Settings (clinic profile, radius, search terms)
- Outreach (preview or send emails to up to 50 recipients)
- Health check indicator (`/api/health`)
- Same-origin API calls (`/api/*`) → zero CORS if hosted on Vercel

---

## Repo Structure
```
AcuLeadFinder_AI/
├─ index.html                 # SaaS-ready UI (works standalone)
└─ (optional, when you add API)
   └─ app/
      └─ api/
         ├─ health/route.ts   # GET /api/health
         ├─ config/route.ts   # GET/PUT /api/config
         └─ outreach/route.ts # POST /api/outreach
```

> If you prefer Flask on Render later, move `index.html` to `aculeadfinder_backend/src/static/index.html`. The UI is the same.

---

## Quick Start (Frontend Only)
1. Push this repo to GitHub as **`AcuLeadFinder_AI`**.
2. In Vercel:
   - **New Project → Import** your repo.
   - Framework: **Other** (static).
   - Build Command: **None**
   - Output Directory: **/**
   - Deploy.
3. Open your site. You can click around; API calls will show as “not reachable” until you add the backend.

---

## Add the Backend (Vercel Serverless, recommended)

### 1) Create API routes
Add these files:

**`app/api/health/route.ts`**
```ts
import { NextResponse } from 'next/server';
export async function GET() {
  return NextResponse.json({ ok: true, service: 'aculeadfinder', time: new Date().toISOString() });
}
```

**`app/api/config/route.ts`** (uses Vercel Postgres; see “Storage” below)
```ts
import { sql } from '@vercel/postgres';
import { NextResponse } from 'next/server';

async function ensureTable() {
  await sql`CREATE TABLE IF NOT EXISTS app_config (
    id INT PRIMARY KEY,
    payload JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  )`;
  await sql`INSERT INTO app_config (id, payload) VALUES (1, '{}'::jsonb) ON CONFLICT (id) DO NOTHING`;
}

export async function GET() {
  await ensureTable();
  const { rows } = await sql`SELECT payload, updated_at FROM app_config WHERE id = 1`;
  return NextResponse.json(rows[0] ?? { payload: {}, updated_at: null });
}

export async function PUT(req: Request) {
  const body = await req.json().catch(() => ({}));
  await ensureTable();
  await sql`UPDATE app_config SET payload = ${body}::jsonb, updated_at = NOW() WHERE id = 1`;
  return NextResponse.json(body);
}
```

**`app/api/outreach/route.ts`** (SendGrid mailer)
```ts
import { NextResponse } from 'next/server';
import sg from '@sendgrid/mail';

sg.setApiKey(process.env.SENDGRID_API_KEY || '');

const FROM_EMAIL = process.env.SMTP_FROM_EMAIL || 'info@avicennamedicine.com';
const FROM_NAME  = process.env.SMTP_FROM_NAME  || 'Dr. Farah Behroozi, L.Ac.';

export async function POST(req: Request) {
  const data = await req.json().catch(() => ({}));
  let recipients: string[] = data.recipients || [];
  if (typeof recipients === 'string') recipients = [recipients];

  if (!recipients.length) return NextResponse.json({ error: 'recipients is required' }, { status: 400 });
  if (recipients.length > 50) return NextResponse.json({ error: 'max 50 recipients' }, { status: 400 });

  const name = data.name_hint || 'there';
  const condition = data.condition || 'your needs';

  const subject = `Personalized acupuncture care in Potomac — ${FROM_NAME}`;
  const html = `
  <div style="font-family:system-ui,Arial,sans-serif;line-height:1.6">
    <p>Hi ${name},</p>
    <p>I noticed you might be exploring acupuncture or natural support for ${condition}.
       I'm ${FROM_NAME} in Potomac, MD. I provide gentle, evidence-informed care for pain, stress,
       and whole-body wellness.</p>
    <p>I’d be happy to offer a complimentary consult to answer questions and see if we’re a good fit.</p>
    <p><strong>Contact:</strong> <a href="mailto:${FROM_EMAIL}">${FROM_EMAIL}</a></p>
    <p>Warmly,<br/>${FROM_NAME}</p>
    <hr/><small>If you received this in error, reply “stop”.</small>
  </div>`.trim();

  const text = `Hi ${name},

I noticed you might be exploring acupuncture or natural support for ${condition}.
I'm ${FROM_NAME} in Potomac, MD. I’d be happy to offer a complimentary consult.

Email: ${FROM_EMAIL}

Warmly,
${FROM_NAME}
`;

  if (data.preview_only) {
    return NextResponse.json({ status:'preview', to: recipients, subject, html_length: html.length, text_length: text.length });
  }
  if (!process.env.SENDGRID_API_KEY) return NextResponse.json({ error: 'SENDGRID_API_KEY not set' }, { status: 500 });

  try {
    await sg.sendMultiple({ to: recipients, from: { email: FROM_EMAIL, name: FROM_NAME }, subject, text, html } as any);
    return NextResponse.json({ status: 'sent', count: recipients.length });
  } catch (e:any) {
    return NextResponse.json({ status:'error', message: e?.message || String(e) }, { status: 500 });
  }
}
```

### 2) Install deps
Create `package.json` (or add deps if it already exists):
```json
{
  "private": true,
  "scripts": { "dev": "next dev", "build": "next build", "start": "next start" },
  "dependencies": {
    "@vercel/postgres": "0.10.0",
    "@sendgrid/mail": "^8.1.0",
    "next": "14.2.5",
    "react": "18.2.0",
    "react-dom": "18.2.0"
  }
}
```

### 3) Storage (Vercel Postgres)
- In Vercel: Project → **Storage** → **Add** → **Postgres** → Create DB.  
Vercel injects the env vars automatically for the project.

### 4) Email (SendGrid)
- Create API key with “Mail Send: Full Access”.
- Vercel → Project → **Settings → Environment Variables**:
  ```
  SENDGRID_API_KEY = <paste key>
  SMTP_FROM_EMAIL  = info@avicennamedicine.com
  SMTP_FROM_NAME   = Dr. Farah Behroozi, L.Ac.
  ```
- Redeploy.

---

## Seeding & Testing

**Health**
```bash
curl -s https://<your-domain>/api/health
```

**Seed config**
```bash
curl -sX PUT https://<your-domain>/api/config   -H "Content-Type: application/json"   -d '{
    "business": {
      "name": "Dr. Farah Behroozi, L.Ac.",
      "address": "10220 River Rd #206, Potomac, MD 20854",
      "email": "info@avicennamedicine.com"
    },
    "radius_miles": 30,
    "search_terms": [
      "Acupuncture near me","Chinese medicine","natural pain relief",
      "holistic healing","back pain acupuncture","facial acupuncture",
      "stress relief acupuncture","Dr. Farah Behroozi"
    ]
  }'
```

**Preview outreach (no send)**
```bash
curl -sX POST https://<your-domain>/api/outreach   -H "Content-Type: application/json"   -d '{"recipients":["you@example.com"],"name_hint":"Farah","condition":"back pain","preview_only":true}'
```

**Real send**
```bash
curl -sX POST https://<your-domain>/api/outreach   -H "Content-Type: application/json"   -d '{"recipients":["you@example.com"],"name_hint":"Farah","condition":"back pain"}'
```

---

## Configuration Notes
- All UI calls are same-origin: `/api/*`  
- No CORS needed when frontend + backend live on the same Vercel project.
- If you later separate front/back into different domains, add CORS headers on the API.

---

## Roadmap
- Replace “Run Discovery (stub)” with real discovery (SerpAPI/Reddit/Yelp integrations).
- Metrics persistence (sends, opens, booked), stored in Postgres.
- Admin auth for `/api/config` & bulk outreach.
- Cron-like schedules via external scheduler (or Vercel Cron if available to you).

---

## Troubleshooting
- **API shows “not reachable”**: You haven’t added the serverless routes yet or the project didn’t detect Next.js. Add `app/api/*` files and `package.json`, redeploy.
- **Send fails**: Check `SENDGRID_API_KEY` and DNS/Sender verification on SendGrid. Try “Single Sender” if you don’t control DNS.
- **Config doesn’t persist**: Ensure the Postgres database is attached to this project.

---

## Branding & License
- Product name: **AcuLeadFinder AI™** (use ™ symbol in marketing)
- You own your content and branding. Add a LICENSE file as desired for collaborators.

---

### Need a one-click Next.js version?
Ask and we’ll provide a minimal `next.config.js`, `app/page.tsx` (migrating this UI), and the `app/api/*` routes so the whole SaaS runs natively on Vercel with a single deploy.
