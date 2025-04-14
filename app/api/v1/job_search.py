from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services.job_scraper.linkedin_scraper import LinkedInJobScraper
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class JobPreference(BaseModel):
    experienceLevel: List[str]
    jobTitle: List[str]
    jobType: List[str]

class JobResponse(BaseModel):
    title: str
    company: str
    location: str
    seniority: str
    url: str
    posted: str
    company_url: str
    employment_type: List[str]

@router.post("/search", response_model=List[JobResponse])
async def search_jobs(preferences: JobPreference):
    try:
        scraper = LinkedInJobScraper()

        print(scraper)
        
        title_filter = " OR ".join(preferences.jobTitle)
        
        type_map = {
            "Full-time": "FULL_TIME",
            "Part-time": "PART_TIME",
            "Contract": "CONTRACTOR",
            "Internship": "INTERN",
        }
        
        type_filter = ",".join([type_map[job_type] for job_type in preferences.jobType])
        
        seniority_map = {
            "Entry Level": "Entry level",
            "Mid Level": "Mid-Senior level",
            "Senior Level": "Senior level",
            "Intern": "Internship",
        }
        
        seniority_filter = ",".join([
            seniority_map.get(exp, exp)  
            for exp in preferences.experienceLevel
        ])

        print(title_filter,type_filter,preferences, seniority_filter)

        
        result = scraper.search_jobs(   
        title_filter=title_filter,
        seniority_filter=seniority_filter,
        remote=True,
        type_filter=type_filter
        )

        print(result)
        
        if not result:
            return []
            
        formatted_jobs = []
        for job in result:
            formatted_jobs.append({
                "title": job.get('title', 'N/A'),
                "company": job.get('organization', 'N/A'),
                "location": ", ".join(job.get('locations_derived', ['N/A'])),
                "seniority": job.get('seniority', 'N/A'),
                "url": job.get('url', 'N/A'),
                "posted": job.get('date_posted', 'N/A'),
                "company_url": job.get('linkedin_org_url', 'N/A'),
                "employment_type": job.get('employment_type', [])
            })
            
        return formatted_jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
