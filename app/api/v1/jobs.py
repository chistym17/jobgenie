from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27018/'))
db = client['jobs_db']
collection = db['jobs']

@router.get("/jobs", response_model=List[Dict])
async def get_all_jobs():
    """
    Get all jobs from the database
    """
    try:
        jobs = list(collection.find({}, {'_id': 0}))
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")
