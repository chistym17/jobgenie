from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import resume
from app.api.v1 import job_search
import uvicorn

app = FastAPI(
    title="Job Assistant API",
    description="API for job search and resume processing",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router, prefix="/api/v1")
app.include_router(job_search.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Job Assistant API is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
