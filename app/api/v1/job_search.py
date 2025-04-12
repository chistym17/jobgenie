from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services.job_scraper.linkedin_scraper import LinkedInJobScraper

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
        
        title_filter = " OR ".join(preferences.jobTitle)
        
        experience_map = {
            "Entry Level": "0-2",
            "Mid Level": "2-5",
            "Senior Level": "5-10",
            "Executive": "10+"
        }
        
        type_map = {
            "Full-time": "FULL_TIME",
            "Part-time": "PART_TIME",
            "Contract": "CONTRACTOR",
            "Internship": "INTERN",
        }
        
        experience_level_filter = ",".join([experience_map[exp] for exp in preferences.experienceLevel])
        type_filter = ",".join([type_map[job_type] for job_type in preferences.jobType])

        print(title_filter,type_filter,experience_level_filter)

        
        result = scraper.search_jobs(   
        title_filter=title_filter,
        seniority_filter=experience_level_filter,
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
