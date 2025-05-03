from fastapi import APIRouter
from .fetch_jobs import router as jobs_router
from .upload_resume import router as upload_resume_router
from .users import router as users_router

router = APIRouter()

router.include_router(jobs_router)
router.include_router(upload_resume_router)
router.include_router(users_router)
