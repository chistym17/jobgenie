from fastapi import APIRouter
from .jobs import router as jobs_router
from .users import router as users_router

router = APIRouter()

router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
router.include_router(users_router, tags=["auth"])
