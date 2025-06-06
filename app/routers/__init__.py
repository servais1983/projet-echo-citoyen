from fastapi import APIRouter
from app.routers import auth, notifications, stats, templates, users, webhooks

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
router.include_router(stats.router, prefix="/stats", tags=["stats"])
router.include_router(templates.router, prefix="/templates", tags=["templates"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"]) 