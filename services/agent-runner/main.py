from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Autonomous LeadGen Agent", version="v1")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
try:
    from routes.health import router as health_router
    from routes.jobs import router as jobs_router
    from routes.drafts import router as drafts_router
    from routes.send import router as send_router
    
    app.include_router(health_router)
    app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
    app.include_router(drafts_router, prefix="/drafts", tags=["drafts"])
    app.include_router(send_router, prefix="/webhooks", tags=["webhooks"])
    
except ImportError as e:
    print(f"Import error: {e}")

@app.get("/")
async def root():
    return {
        "message": "Autonomous LeadGen Agent API",
        "version": "v1",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "version": "v1"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
