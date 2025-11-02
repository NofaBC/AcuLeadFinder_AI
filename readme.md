# AcuLeadFinder AI — Autonomous LeadGen Agent (Backend)

Config-driven backend that powers **AcuLeadFinder AI™** and other presets (e.g., APLeadFinder).
Agent loop: **Plan → Search/Enrich → Draft → Approve/Send → Log → Learn**.

## ✨ Features

* Preset-based campaigns (Acu, APLeadFinder, etc.)
* Draft outreach emails with brand voice + opt-out
* Human-in-the-loop approvals and capped batch sending
* Firestore persistence (leads, drafts, runs, jobs)
* SendGrid integration (deliveries, bounces via webhook)
* Robots.txt-aware search/scrape

## 📁 Repo Structure

```
services/agent-runner/
  main.py                # FastAPI app
  routes/                # /health, /campaigns, /jobs, /drafts, /send, /webhooks
  agents/                # leadgen.py, planner.py
  tools/                 # web_search.py, enrich.py, llm.py, email_sendgrid.py, email_templates.py
  memory/                # firestore_store.py, vector_store.py, schemas.py
  policies/              # guardrails.py, compliance.py
  config/presets/        # acu.json, apl.json
  tests/                 # test_leadgen_flow.py, etc.
infra/
  vercel.json            # (optional) API routing
README.md
```

## 🧰 Requirements

* Python 3.11+
* Firebase project (Firestore in **Native** mode)
* SendGrid account (domain authenticated)
* OpenAI API key (GPT-5 or 4o)

## 🔐 Environment

Create `.env` (or use Vercel/Secrets):

```
OPENAI_API_KEY=...
SENDGRID_API_KEY=...
FIREBASE_PROJECT_ID=...
FIREBASE_CLIENT_EMAIL=...
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_DB_URL=            # optional
DEFAULT_MODEL=gpt-5-mini    # or gpt-4o
ALLOWED_SENDER=info@nofabusinessconsulting.com
SEND_CAP_PER_RUN=20
DAILY_SEND_CAP=200
ROBOTS_RESPECT=true
```

## 🚀 Setup & Run (Local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # or: fastapi uvicorn pydantic pydantic-settings google-cloud-firestore openai sendgrid python-dotenv httpx bs4
uvicorn services.agent-runner.main:app --reload
# Health check:
curl http://localhost:8000/health
```

## 🧩 Presets

`config/presets/acu.json` (Behroozi) and `config/presets/apl.json` (generic) define:

* industry, geo, keywords
* brand voice / offer
* from_name / from_email
* send caps & model

Switching verticals = swapping preset, no code changes.

## 🔌 API (v1)

* `GET /health` → `{status:"ok", version:"v1"}`
* `POST /campaigns` → `{ preset: "acu" | "apl", model?, sendCapPerRun? }` → `{campaignId}`
* `GET /campaigns/{id}`
* `POST /jobs` → `{ campaignId, plannedCount }` → `{jobId}`
* `GET /jobs/{id}` → status/cost
* `GET /jobs/{id}/drafts?status=draft|approved|sent`
* `POST /drafts/{id}/approve`
* `POST /drafts/{id}/reject`
* `POST /drafts/{id}/send`            # immediate send
* `POST /jobs/{id}/send-approved`     # batch send up to cap
* `POST /webhooks/sendgrid`           # events (delivered/bounce/spam)

> If hosting API on a different domain, enable CORS.

## 🗄️ Data Model (Firestore)

* `campaigns/{campaignId}`: name, preset, keywords, caps, model, status
* `jobs/{jobId}`: campaignId, status, plannedCount, sentCount, costUSD
* `leads/{leadId}`: jobId, company, contact, email, domain, sourceUrl
* `drafts/{draftId}`: jobId, leadId, subject, body, status, messageId
* `runs/{runId}`: jobId, step, event, data(JSON), ts
* `settings/global`: allowDomains[], blockDomains[], unsubscribeText, legalAddress

Indexes suggested for `drafts.status`, `drafts.jobId`, `leads.jobId`, `jobs.status`.

## 🌐 Deploy

**Option A: Vercel (static + function routes)**

* Place API under `services/agent-runner/` and route via `infra/vercel.json`.
* Add env vars in Vercel Project → Settings → Environment Variables.

**Option B: Fly.io/Render for FastAPI**, Vercel for static UI.
Set UI `API_BASE` to your API URL and configure CORS.

## ✅ Definition of Done (M1)

* Start job → N **drafts** stored with linked leads and run logs
* Approve + send → SendGrid `messageId` stored, status updates to `sent`
* Caps enforced; robots.txt respected; opt-out/footer added
* Presets work without code edits

## 🛡️ Compliance & Guardrails

* Always include opt-out + legal footer
* Respect robots.txt & domain allow-lists
* Warm up new sender domains (progressive `DAILY_SEND_CAP`)
* Store minimal PII; avoid sensitive data

## 🧪 Quick Test Commands

```bash
# Create campaign from preset
curl -X POST http://localhost:8000/campaigns -H 'Content-Type: application/json' \
  -d '{"preset":"acu","model":"gpt-5-mini","sendCapPerRun":20}'

# Create job
curl -X POST http://localhost:8000/jobs -H 'Content-Type: application/json' \
  -d '{"campaignId":"<campaignId>","plannedCount":10}'

# List drafts
curl http://localhost:8000/jobs/<jobId>/drafts?status=draft
```

## 📄 License

Proprietary © NOFA Business Consulting, LLC. All rights reserved.
