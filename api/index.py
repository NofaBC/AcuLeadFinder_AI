from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Autonomous LeadGen Agent API", "version": "v1"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "v1"}
