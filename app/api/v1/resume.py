from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.resume_parser import ResumeParser
from app.db.models import ResumeResponse
import tempfile
import shutil

router = APIRouter(prefix="/resume", tags=["Resume Parsing"])
parser = ResumeParser()

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        file_uri = parser.upload_pdf(tmp_path)
        resume_data = parser.extract_resume_data(file_uri)
        markdown = parser.convert_to_markdown(resume_data)
        resume_data["markdown"] = markdown
        
        return JSONResponse(content=resume_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")
