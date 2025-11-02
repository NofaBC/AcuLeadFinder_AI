from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Autonomous LeadGen Agent", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Autonomous LeadGen Agent API", "version": "v1"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "v1"}

@app.get("/jobs")
async def list_jobs():
    return {"jobs": []}

@app.post("/jobs")
async def create_job():
    return {"jobId": "demo_1", "status": "queued"}
