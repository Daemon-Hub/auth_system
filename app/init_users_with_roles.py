from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .models.user import User
from .services.rbac import RBACService
from .services.user import UserService
from .security.password import hash_password

async def create_users_with_roles(db: AsyncSession) -> List[User]:
    password = hash_password("hashed_password")
    admin_user = await UserService.get_user_by_email("admin@example.com", db)
    if not admin_user:
        admin_user = await UserService.create_user_with_roles(
            User(
                first_name="Admin",
                last_name="User",
                patronymic="",
                email="admin@example.com",
                password=password
            ), 
            db,
            ["admin"],
        )
        
    moderator_user = await UserService.get_user_by_email("moderator@example.com", db)
    if not moderator_user:
        moderator_user = await UserService.create_user_with_roles(
            User(
                first_name="Moderator",
                last_name="User",
                patronymic="",
                email="moderator@example.com",
                password=password
            ),
            db,
            ["moderator"],
        )
        
    user_user = await UserService.get_user_by_email("user@example.com", db)
    if not user_user:
        user_user = await UserService.create_user_with_roles(
            User(
                first_name="User",
                last_name="User",
                patronymic="",
                email="user@example.com",
                password=password
            ), 
            db
        )
        
    return [admin_user, moderator_user, user_user]


def print_users_info(users: List[User]):
    for user in users:
        print("\n" + "="*50)
        print(f"{user.first_name}")
        print(f"Email: {user.email}")
        print(f"Password: hashed_password")
        print("="*50 + "\n")
    


async def init_users_with_roles(db: AsyncSession):
    print("Initializing users with roles...")    
    users = await create_users_with_roles(db)
    print_users_info(users)
    