from sqlalchemy.ext.asyncio import AsyncSession

from .models.user import User
from .services.rbac import RBACService
from .crud.user import create_user, get_user_by_email

async def create_users_with_roles(db: AsyncSession) -> list[User]:
    admin_user = await get_user_by_email("admin@example.com", db)
    if not admin_user:
        admin_user = await create_user(
            User(
                first_name="Admin",
                last_name="User",
                patronymic="",
                email="admin@example.com",
                password="hashed_password"
            ), 
            db
        )
        RBACService.add_roles_to_user(
            db, admin_user.id,
            [await RBACService.get_role_by_name(db, "admin")]
        )
        
    moderator_user = await get_user_by_email("moderator@example.com", db)
    if not moderator_user:
        moderator_user = await create_user(
            User(
                first_name="Moderator",
                last_name="User",
                patronymic="",
                email="moderator@example.com",
                password="hashed_password"
            ),
            db
        )
        RBACService.add_roles_to_user(
            db, moderator_user.id,
            [await RBACService.get_role_by_name(db, "moderator")]
        )
        
    editor_user = await get_user_by_email("editor@example.com", db)
    if not editor_user:
        editor_user = await create_user(
            User(
                first_name="Editor",
                last_name="User",
                patronymic="",
                email="editor@example.com",
            password="hashed_password"
            ),
            db
        )
        RBACService.add_roles_to_user(
            db, editor_user.id,
            [await RBACService.get_role_by_name(db, "editor")]
        )
    
    user_user = await get_user_by_email("user@example.com", db)
    if not user_user:
        user_user = await create_user(
            User(
                first_name="User",
                last_name="User",
                patronymic="",
                email="user@example.com",
                password="hashed_password"
            ), 
            db
        )
        RBACService.add_roles_to_user(
            db, user_user.id,
            [await RBACService.get_role_by_name(db, "user")]
        )
        
    return [admin_user, moderator_user, editor_user, user_user]


def print_users_info(users: list[User]):
    for user in users:
        print("\n" + "="*50)
        print(f"{user.first_name}")
        print(f"Email: {user.email}")
        print(f"Password: {user.password}")
        print("="*50 + "\n")
    


async def init_users_with_roles(db: AsyncSession):
    print("Initializing users with roles...")    
    users = await create_users_with_roles(db)
    print_users_info(users)
    