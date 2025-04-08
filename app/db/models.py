from pydantic import BaseModel
from typing import List, Dict, Optional

class ContactInfo(BaseModel):
    email: Optional[str]
    phone: Optional[str]
    linkedin: Optional[str]

class ResumeResponse(BaseModel):
    name: Optional[str]
    contact: ContactInfo
    skills: List[str]
    education: List[str]
    experience: List[str]
    projects: List[str]
    certifications: List[str]
    preferences: Dict[str, str]
    markdown: str
