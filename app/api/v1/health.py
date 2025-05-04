from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

router = APIRouter()

client = MongoClient(os.getenv('MONGODB_URI'))

def check_mongodb_connection():
    try:
        client.server_info()
        return True
    except Exception as e:
        return False

@router.get("/health", tags=["health"])
async def health_check():
    db_status = check_mongodb_connection()
    return {
        "server_status": "healthy",
        "database_status": "healthy" if db_status else "unhealthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/server", tags=["health"])
async def check_server():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
