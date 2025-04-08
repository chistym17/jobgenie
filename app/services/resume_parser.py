import os
import google.generativeai as genai
from markdownify import markdownify as md
from dotenv import load_dotenv
import re
import json

load_dotenv()

class ResumeParser:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GOOGLE_API_KEY in environment variables.")
        genai.configure(api_key=self.api_key)

    def upload_pdf(self, file_path: str) -> str:
        """Uploads the resume PDF to Gemini and returns file URI."""
        uploaded_file = genai.upload_file(path=file_path, display_name="Resume")
        return uploaded_file.uri

    def generate_system_prompt(self) -> str:
        """Returns a system prompt to guide Gemini for parsing resumes."""
        return (
            "You are a professional resume parser. "
            "Extract the following fields from the resume provided as a PDF file:\n\n"
            "- Full Name\n"
            "- Contact Information (Phone, Email, LinkedIn if available)\n"
            "- Skills (technical and soft)\n"
            "- Education (with degrees, institutes, years)\n"
            "- Work Experience (position, company, description, duration)\n"
            "- Projects (title, tech stack, description)\n"
            "- Certifications (if any)\n"
            "- Job Preferences (location, remote/on-site, role, etc.)\n\n"
            "Respond in the following structured JSON format:\n"
            "{\n"
            "  'name': '',\n"
            "  'contact': {\n"
            "     'email': '', 'phone': '', 'linkedin': ''\n"
            "  },\n"
            "  'skills': [],\n"
            "  'education': [],\n"
            "  'experience': [],\n"
            "  'projects': [],\n"
            "  'certifications': [],\n"
            "  'preferences': {}\n"
            "}"
        )
    def extract_resume_data(self, file_uri: str) -> dict:
        """Sends the uploaded resume URI to Gemini with a parsing prompt and returns structured JSON."""
        prompt = self.generate_system_prompt()

        model = genai.GenerativeModel("gemini-2.0-flash")

        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [{"text": prompt}]},
                {"role": "user", "parts": [{"file_data": {"file_uri": file_uri}}]}
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
