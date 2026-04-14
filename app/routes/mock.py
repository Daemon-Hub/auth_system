from fastapi import APIRouter, Depends

from ..models import User
from ..security.deps import require_permission


router = APIRouter(prefix="/mock")


MOCK_POSTS = [
    {"id": 1, "title": "Новость дня", "status": "published"},
    {"id": 2, "title": "Черновик статьи", "status": "draft"}
]

MOCK_COMMENTS = [
    {"id": 1, "post_id": 1, "author": "john_doe", "text": "Отличная статья!", "is_blocked": False},
    {"id": 2, "post_id": 1, "author": "troll_99", "text": "Спам контент", "is_blocked": True}
]

MOCK_USERS = [
    {"id": 1, "email": "admin@test.com", "role": "admin"},
    {"id": 2, "email": "moderator@test.com", "role": "moderator"},
    {"id": 3, "email": "user@test.com", "role": "user"}
]

MOCK_ANALYTICS = {"views_today": 1500, "users_online": 42}


# ====================== Свободный доступ ====================== #

@router.get("/posts")
async def get_posts(
    user: User = Depends(require_permission("posts", "read"))
):
    return {"data": MOCK_POSTS}

@router.get("/comments")
async def get_comments(
    user: User = Depends(require_permission("comments", "read"))
):
    return {"data": MOCK_COMMENTS}


# ============== user, moderator, admin (НЕ guest) ============== #

@router.post("/posts")
async def create_post(
    user: User = Depends(require_permission("posts", "create"))
):
    return {
        "message": "Post successfully created", 
        "author": user.email
    }

@router.post("/comments")
async def create_comment(
    user: User = Depends(require_permission("comments", "create"))
):
    return {
        "message": "Comment added", 
        "author": user.email
    }
    
@router.get("/users")
async def get_users(
    user: User = Depends(require_permission("users", "read"))
):
    return {
        "data": MOCK_USERS, 
        "access_granted_to": user.email
    }

# ===================== moderator, admin ===================== #

@router.put("/posts/{post_id}/moderate")
async def moderate_post(
    post_id: int,
    user: User = Depends(require_permission("posts", "moderate"))
):
    return {
        "message": f"Post {post_id} sent for moderation/approved", 
        "moderated_by": user.email
    }

@router.get("/roles")
async def get_roles(
    user: User = Depends(require_permission("roles", "read"))
):
    return {
        "data": ["admin", "moderator", "user", "guest"], 
        "access_granted_to": user.email
    }

@router.get("/permissions")
async def get_permissions(
    user: User = Depends(require_permission("permissions", "read"))
):
    return {
        "data": ["users.read", "posts.create", "..."], 
        "access_granted_to": user.email
    }

@router.get("/analytics")
async def get_analytics(
    user: User = Depends(require_permission("analytics", "read"))
):
    return {
        "data": MOCK_ANALYTICS, 
        "access_granted_to": user.email
    }

@router.post("/analytics/export")
async def export_analytics(
    user: User = Depends(require_permission("analytics", "export"))
):
    return {
        "message": "Analytics CSV exported", 
        "exported_by": user.email
    }
  
# ======================= ТОЛЬКО admin ======================= #

@router.put("/users/{user_id}/manage")
async def manage_user(
    user_id: int,
    user: User = Depends(require_permission("users", "manage"))
):
    return {
        "message": f"Full management applied to user {user_id}", 
        "managed_by": user.email
    }

@router.get("/system/logs")
async def get_logs(
    user: User = Depends(require_permission("system", "logs"))
):
    return {
        "data": ["12:00 User logged in", "12:05 DB backup started"], 
        "access_granted_to": user.email
    }

@router.patch("/system/settings")
async def update_system_settings(
    user: User = Depends(require_permission("system", "settings"))
):
    return {
        "message": "System settings updated", 
        "updated_by": user.email
    }

@router.post("/system/backup")
async def trigger_backup(
    user: User = Depends(require_permission("system", "backup"))
):
    return {
        "message": "Database backup started", 
        "triggered_by": user.email 
    }

