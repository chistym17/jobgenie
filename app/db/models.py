from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from bson import ObjectId

class ContactInfo(BaseModel):
    email: Optional[str]
    phone: Optional[str]
    linkedin: Optional[str]

class ResumeResponse(BaseModel):
    name: Optional[str]
    contact: Dict[str, Any]
    skills: List[Any]
    education: List[Any]
    experience: List[Any]
    projects: List[Any]
    certifications: List[Any]
    preferences: Dict[str, Any]
    markdown: str

class Resume(BaseModel):
    id: Optional[ObjectId] = Field(None, alias='_id')
    name: str
    contact: Dict[str, Any]
    skills: List[Any]
    education: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    markdown: str
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }
