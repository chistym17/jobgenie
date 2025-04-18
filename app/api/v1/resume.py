from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.resume_parser import ResumeParser
from app.db.models import ResumeResponse
import tempfile
import shutil
from bson import ObjectId
from datetime import datetime
import json

router = APIRouter(prefix="/resume", tags=["Resume Parsing"])
parser = ResumeParser()

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError ("Type %s not serializable" % type(obj))

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        resume_id = await parser.process_resume(tmp_path)
        
        resume_data = await parser.resumes_collection.find_one({"_id": ObjectId(resume_id)})
        if not resume_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve saved resume data")
            
        resume_data["_id"] = str(resume_data["_id"])
        
        resume_data["created_at"] = resume_data["created_at"].isoformat()
        resume_data["updated_at"] = resume_data["updated_at"].isoformat()
        
        return JSONResponse(content=resume_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
