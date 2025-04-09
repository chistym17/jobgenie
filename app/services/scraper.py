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
        location_filter: str,
        ai_work_arrangement_filter: Optional[str] = None,  
        ai_experience_level_filter: Optional[str] = None, 
        seniority_filter: Optional[str] = None, 
        limit: int = 10,
        offset: int = 0
    ):
        """
        Search for jobs using LinkedIn API with advanced filtering options
        
        Args:
            title_filter: Job title to search for
            location_filter: Location filter (use OR for multiple locations)
            ai_work_arrangement_filter: Work arrangement filter
                Options: On-site, Hybrid, Remote OK, Remote Solely
                Multiple values: "Hybrid,Remote OK"
            ai_experience_level_filter: Experience level filter
                Options: 0-2, 2-5, 5-10, 10+
                Multiple values: "0-2,2-5"
            seniority_filter: Seniority level filter
                Options: Entry level, Mid-Senior level, Director, etc.
                Multiple values: "Entry level,Mid-Senior level"
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of job listings or None if error
        """
        params = {
            'limit': limit,
            'offset': offset,
            'title_filter': title_filter,
            'location_filter': location_filter
        }
        
        if ai_work_arrangement_filter:
            params['ai_work_arrangement_filter'] = ai_work_arrangement_filter
            
        if ai_experience_level_filter:
            params['ai_experience_level_filter'] = ai_experience_level_filter
            
        if seniority_filter:
            params['seniority_filter'] = seniority_filter
            
        endpoint = '/active-jb-24h'
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
        location_filter="United States OR United Kingdom OR India OR Canada",
        ai_work_arrangement_filter="Remote OK,Remote Solely",  
        ai_experience_level_filter="5-10,10+",  
        seniority_filter="Mid-Senior level,Director"
    )
    print("Full API response:")
    print(result)
    
    if result:
        print(f"\nFound {len(result)} jobs")

        print(result[0])
        
        for job in result[:10]: 
            print(f"\nTitle: {job.get('title', 'N/A')}")
            print(f"Company: {job.get('organization', 'N/A')}")
            print(f"Location: {', '.join(job.get('locations_derived', ['N/A']))}")
            print(f"Work Arrangement: {job.get('ai_work_arrangement', 'N/A')}")
            print(f"Experience Level: {job.get('ai_experience_level', 'N/A')}")
            print(f"Seniority: {job.get('seniority', 'N/A')}")
            print(f"Job ID: {job.get('id', 'N/A')}")
            print(f"URL: {job.get('url', 'N/A')}")
            print(f"Posted: {job.get('date_posted', 'N/A')}")
            print(f"Industry: {job.get('linkedin_org_industry', 'N/A')}")
            print(f"Company Size: {job.get('linkedin_org_size', 'N/A')}")
            print(f"Company Employees: {job.get('linkedin_org_employees', 'N/A')}")
            print(f"Company URL: {job.get('linkedin_org_url', 'N/A')}")
            print(f"Employment Type: {', '.join(job.get('employment_type', []))}")
            
            locations = job.get('locations_raw', [])
            if locations:
                location = locations[0]
                print(f"\nLocation Details:")
                print(f"Address: {location.get('address', {}).get('addressLocality', 'N/A')}")
                print(f"Country: {location.get('address', {}).get('addressCountry', 'N/A')}")
                print(f"Latitude: {location.get('latitude', 'N/A')}")
                print(f"Longitude: {location.get('longitude', 'N/A')}")
    else:
        print("\nNo response received from API")