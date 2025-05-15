import os
import requests
from typing import Dict, Any

def start_embedder_task(user_email: str) -> Dict[str, Any]:
 
    try:
        worker_url = os.getenv('WORKER_URL')
        if not worker_url:
            raise Exception("Worker URL not configured")

        response = requests.post(
            f"{worker_url}/precompute-embedding",
            json={"email": user_email},
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()  
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error starting embedding task: {e}")
        raise Exception(f"Failed to start embedding computation: {str(e)}")
    except Exception as e:
        print(f"Error starting embedding task: {e}")
        raise 