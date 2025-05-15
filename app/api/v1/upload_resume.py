## api to upload and parse users resume via gemini llm

import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from app.services.resume_parser import ResumeParser
from app.db.models import ResumeResponse
import tempfile
import shutil
from bson import ObjectId
from datetime import datetime
import json
from typing import Dict, Any

router = APIRouter(prefix="/resume", tags=["Resume Parsing"])
parser = ResumeParser()

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError ("Type %s not serializable" % type(obj))

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...), user_email: str = Form(...)) -> Dict[str, Any]:
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        resume_id, task_id = await parser.process_resume(tmp_path, user_email=user_email)
        
        try:
            os.unlink(tmp_path)
            print(f"Temporary file cleaned up: {tmp_path}")
        except Exception as cleanup_err:
            print(f"Warning: Failed to clean up temporary file: {cleanup_err}")

        resume_data = await parser.resumes_collection.find_one({"_id": ObjectId(resume_id)})
        if not resume_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve saved resume data")
            
        resume_data["_id"] = str(resume_data["_id"])
        resume_data["created_at"] = resume_data["created_at"].isoformat()
        resume_data["updated_at"] = resume_data["updated_at"].isoformat()
        
        response_data = {
            "resume": resume_data,
            "task_id": task_id,
            "message": "Resume uploaded and processing started"
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
