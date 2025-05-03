
## linkedin job scraper to fetch job data from linkedin using rapidapi--not included in v1
import os
import requests
from dotenv import load_dotenv
from typing import Optional

class LinkedInJobScraper:
    def __init__(self):
        load_dotenv()
        self.base_url = f"https://{os.getenv('RAPIDAPI_HOST')}"
        self.headers = {
            'x-rapidapi-host': os.getenv('RAPIDAPI_HOST'),
            'x-rapidapi-key': os.getenv('RAPIDAPI_KEY')
        }

    def search_jobs(
        self,
        title_filter: str,
        seniority_filter: Optional[str] = None, 
        remote: Optional[bool] = None,
        type_filter: Optional[str] = None,
        limit: int = 2,
        offset: int = 0
    ):
        """
        Search for jobs using LinkedIn API with advanced filtering options
        
        Args:
            title_filter: Job title to search for
            location_filter: Location filter (use OR for multiple locations)
            seniority_filter: Seniority level filter
                Options: Entry level, Mid-Senior level, Director, etc.
                Multiple values: "Entry level,Mid-Senior level"
            remote: Boolean to filter remote jobs
                True: Only remote jobs
                False: Only non-remote jobs
                None: Both remote and non-remote jobs
            type_filter: Job type filter
                Options: CONTRACTOR, FULL_TIME, INTERN, OTHER, PART_TIME, TEMPORARY, VOLUNTEER
                Multiple values: "FULL_TIME,PART_TIME"
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of job listings or None if error
        """
        params = {
            'limit': limit,
            'offset': offset,
            'title_filter': title_filter,
        }
            
        if seniority_filter:
            params['seniority_filter'] = seniority_filter
            
        if remote is not None:
            params['remote'] = str(remote).lower() 
            
        if type_filter:
            params['type_filter'] = type_filter
            
        endpoint = '/active-jb-7d'
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs: {e}")
            return None

    def parse_job_data(self, response):
        """Parse the API response to extract job listings"""
        if not isinstance(response, list):
            print("Error: Response should be a list of jobs")
            return []
            
        return response  

if __name__ == "__main__":
    scraper = LinkedInJobScraper()
    result = scraper.search_jobs(
        title_filter="Software Engineer",
        seniority_filter="Mid-Senior level,Director",
        remote=True,
        type_filter="FULL_TIME,PART_TIME"
    )
    
    if result:
        print(f"\nFound {len(result)} jobs")
        
        for job in result[:10]: 
            print(f"\nTitle: {job.get('title', 'N/A')}")
            print(f"Company: {job.get('organization', 'N/A')}")
            print(f"Location: {', '.join(job.get('locations_derived', ['N/A']))}")
            print(f"Seniority: {job.get('seniority', 'N/A')}")
            print(f"URL: {job.get('url', 'N/A')}")
            print(f"Posted: {job.get('date_posted', 'N/A')}")
            print(f"Company URL: {job.get('linkedin_org_url', 'N/A')}")
            print(f"Employment Type: {', '.join(job.get('employment_type', []))}")
            
    else:
        print("\nNo response received from API")