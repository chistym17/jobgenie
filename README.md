# 🧠 Primary Backend (PB) - JobGenie

The **Primary Backend** of JobGenie is a FastAPI-based service responsible for handling core platform operations like authentication, job scraping, resume parsing, and communication with the frontend.

---

### 🔧 Core Responsibilities

- **Authentication**: Manages user sign-up, login, and JWT-based session handling.
- **Job Scraping**: Uses Firecrawl API to fetch job listings from multiple sources.
- **Resume Handling**: Accepts PDF uploads, converts them to images using `pdf2image`, and prepares them for embedding.
- **API Layer**: Exposes REST endpoints for the frontend to fetch jobs, submit resumes, and manage user sessions.
- **Data Management**: Stores user profiles, jobs, and resume metadata in **MongoDB**.

---

### 🛠️ Tech Stack (Primary Backend)

- **Framework**: FastAPI (Python)
- **Parsing**: pdf2image, PyMuPDF
- **Job Scraping**: Firecrawl API
- **Database**: MongoDB
- **Auth**: JWT

---

> Note: The PB acts as the entry point for all frontend interactions and delegates AI-heavy tasks to the Worker service.
