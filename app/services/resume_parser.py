## gemini llm resume parser to parse and save user resume data
import os
from google import genai
from markdownify import markdownify as md
from dotenv import load_dotenv
import PyPDF2
import re
import json
from datetime import datetime
from app.db.models import Resume
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.utils.startembeddertask import start_embedder_task
load_dotenv()

class ResumeParser:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GOOGLE_API_KEY in environment variables.")
        self.genai_client = genai.Client(api_key=self.api_key)
        
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27018")
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client.jobs_db
        self.resumes_collection = self.db.resumes

    def read_pdf(self, file_path: str) -> str:
        """Reads a PDF file and returns its text content."""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            raise

    def extract_resume_data(self, file_text: str) -> dict:
        """Extracts resume data from a PDF file using Gemini."""
        
        prompt = f"""You are a professional resume parser. Please analyze the following resume text and extract the relevant information:

 Resume Text:
{file_text}

Extract the following fields:
- Full Name
- Contact Information (Phone, Email, LinkedIn if available)
- Skills (technical and soft)
- Education (with degrees, institutes, years)
- Work Experience (position, company, description, duration)
- Projects (title, tech stack, description)
- Certifications (if any)
- Job Preferences (location, remote/on-site, role, etc.)

Respond in the following structured JSON format:
{{
  'name': '',
  'contact': {{
     'email': '', 'phone': '', 'linkedin': ''
  }},
  'skills': [],
  'education': [],
  'experience': [],
  'projects': [],
  'certifications': [],
  'preferences': {{}}
}}
"""

        response = self.genai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                prompt
            ]
        )


        try:
            response_text = response.text.strip()

            match = re.search(r"```json(.*?)```", response_text, re.DOTALL)
            json_str = match.group(1).strip() if match else response_text

            cleaned_str = (
                json_str
                .replace("'", '"')
                .replace('None', 'null')
                .replace('True', 'true')
                .replace('False', 'false')
            )

            return json.loads(cleaned_str)

        except Exception as e:
            raise ValueError(f"Failed to parse response JSON: {e}\nRaw response:\n{response.text}")

    async def save_to_mongodb(self, resume_data: dict, user_email: str):
        """Save parsed resume data to MongoDB."""
        resume = Resume(
            user_email=user_email,
            name=resume_data.get('name', ''),
            contact=resume_data.get('contact', {}),
            skills=resume_data.get('skills', []),
            education=resume_data.get('education', []),
            experience=resume_data.get('experience', []),
            projects=resume_data.get('projects', []),
            certifications=resume_data.get('certifications', []),
            preferences=resume_data.get('preferences', {}),
            markdown=self.convert_to_markdown(resume_data),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        
        resume_dict = resume.model_dump()
        
        result = await self.resumes_collection.insert_one(resume_dict)
        return str(result.inserted_id)

    async def process_resume(self, file_path: str,user_email: str) -> str:
        """Process a resume file and save to MongoDB."""
        try:
            file_text = self.read_pdf(file_path)
            resume_data = self.extract_resume_data(file_text)
            
            resume_id = await self.save_to_mongodb(resume_data,user_email)

            response = start_embedder_task(user_email)
            task_id = response.get("task_id")
            

            return resume_id,task_id
            
        except Exception as e:
            raise ValueError(f"Failed to process resume: {str(e)}")

    def convert_to_markdown(self, resume_json: dict) -> str:
        """Converts parsed resume JSON into Markdown for better display."""
        markdown = f"## {resume_json.get('name', 'Candidate')}\n"

        contact = resume_json.get('contact', {})
        markdown += f"**Email:** {contact.get('email', 'N/A')}  \n"
        markdown += f"**Phone:** {contact.get('phone', 'N/A')}  \n"
        markdown += f"**LinkedIn:** {contact.get('linkedin', 'N/A')}  \n\n"

        markdown += "### Skills\n"
        markdown += ", ".join(resume_json.get("skills", [])) + "\n\n"

        markdown += "### Education\n"
        for edu in resume_json.get("education", []):
            markdown += f"- {edu}\n"

        markdown += "\n### Work Experience\n"
        for exp in resume_json.get("experience", []):
            markdown += f"- {exp}\n"

        markdown += "\n### Projects\n"
        for proj in resume_json.get("projects", []):
            markdown += f"- {proj}\n"

        markdown += "\n### Certifications\n"
        for cert in resume_json.get("certifications", []):
            markdown += f"- {cert}\n"

        markdown += "\n### Preferences\n"
        for key, val in resume_json.get("preferences", {}).items():
            markdown += f"- **{key.capitalize()}:** {val}\n"

        return markdown.strip()
