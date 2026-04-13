from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas.rbac.permission import PermissionCreate
from .schemas.rbac.role import RoleCreate
from .models.rbac import RolePermission
from .services.rbac import RBACService


ROLES_DEFINITIONS = [
    RoleCreate(
        name="admin",
        description="Полный доступ ко всем ресурсам и управлению правами"
    ),
    RoleCreate(
        name="moderator",
        description="Модерация контента и управление пользователями"
    ),
    RoleCreate(
        name="editor",
        description="Создание и редактирование контента"
    ),
    RoleCreate(
        name="user",
        description="Базовый доступ для обычных пользователей"
    ),
    RoleCreate(
        name="guest",
        description="Ограниченный доступ для неавторизованных пользователей"
    ),
]


PERMISSIONS_DEFINITIONS = [
    # Users
    PermissionCreate(name="users.read", resource="users", action="read", description="Чтение данных пользователей"),
    PermissionCreate(name="users.create", resource="users", action="create", description="Создание пользователей"),
    PermissionCreate(name="users.update", resource="users", action="update", description="Обновление данных пользователей"),
    PermissionCreate(name="users.delete", resource="users", action="delete", description="Удаление пользователей"),
    PermissionCreate(name="users.manage", resource="users", action="manage", description="Полное управление пользователями"),
    
    # Roles
    PermissionCreate(name="roles.read", resource="roles", action="read", description="Чтение ролей"),
    PermissionCreate(name="roles.create", resource="roles", action="create", description="Создание ролей"),
    PermissionCreate(name="roles.update", resource="roles", action="update", description="Обновление ролей"),
    PermissionCreate(name="roles.delete", resource="roles", action="delete", description="Удаление ролей"),
    PermissionCreate(name="roles.manage", resource="roles", action="manage", description="Полное управление ролями"),
    PermissionCreate(name="roles.assign", resource="roles", action="assign", description="Назначение ролей пользователям"),
    
    # Permissions
    PermissionCreate(name="permissions.read", resource="permissions", action="read", description="Чтение разрешений"),
    PermissionCreate(name="permissions.create", resource="permissions", action="create", description="Создание разрешений"),
    PermissionCreate(name="permissions.update", resource="permissions", action="update", description="Обновление разрешений"),
    PermissionCreate(name="permissions.delete", resource="permissions", action="delete", description="Удаление разрешений"),
    
    # Posts 
    PermissionCreate(name="posts.read", resource="posts", action="read", description="Чтение постов"),
    PermissionCreate(name="posts.create", resource="posts", action="create", description="Создание постов"),
    PermissionCreate(name="posts.update", resource="posts", action="update", description="Обновление постов"),
    PermissionCreate(name="posts.delete", resource="posts", action="delete", description="Удаление постов"),
    PermissionCreate(name="posts.publish", resource="posts", action="publish", description="Публикация постов"),
    PermissionCreate(name="posts.moderate", resource="posts", action="moderate", description="Модерация постов"),
    
    # Comments
    PermissionCreate(name="comments.read", resource="comments", action="read", description="Чтение комментариев"),
    PermissionCreate(name="comments.create", resource="comments", action="create", description="Создание комментариев"),
    PermissionCreate(name="comments.update", resource="comments", action="update", description="Обновление комментариев"),
    PermissionCreate(name="comments.delete", resource="comments", action="delete", description="Удаление комментариев"),
    PermissionCreate(name="comments.moderate", resource="comments", action="moderate", description="Модерация комментариев"),
    
    # Analytics
    PermissionCreate(name="analytics.read", resource="analytics", action="read", description="Просмотр аналитики"),
    PermissionCreate(name="analytics.export", resource="analytics", action="export", description="Экспорт аналитики"),
    
    # System
    PermissionCreate(name="system.settings", resource="system", action="settings", description="Управление настройками системы"),
    PermissionCreate(name="system.logs", resource="system", action="logs", description="Доступ к логам системы"),
    PermissionCreate(name="system.backup", resource="system", action="backup", description="Создание бекапов"),
]


ROLE_PERMISSIONS = {
    "admin": ["*"],  # Все разрешения
    "moderator": [
        "users.read", "users.update",
        "roles.read", 
        "permissions.read",
        "posts.read", "posts.update", "posts.delete", "posts.publish", "posts.moderate",
        "comments.read", "comments.update", "comments.delete", "comments.moderate",
        "analytics.read", "analytics.export",
    ],    
    "editor": [
        "posts.read", "posts.create", "posts.update",
        "comments.read", "comments.create", "comments.update",
    ],
    "user": [
        "users.read",
        "posts.read", "posts.create", "posts.update",
        "comments.read", "comments.create", "comments.update",
    ],
    "guest": [
        "posts.read",
        "comments.read",
    ],
}


async def init_roles_and_permissions(db: AsyncSession) -> dict:
    result = {
        "roles_created": 0,
        "permissions_created": 0,
        "role_permissions_assigned": 0
    }
    
    # Создаем роли
    created_roles = {}
    for role_definition in ROLES_DEFINITIONS:
        existing_role = await RBACService.get_role_by_name(db, role_definition.name)
        if not existing_role:
            role = await RBACService.create_role(db, role_definition)
            created_roles[role.name] = role.id
            result["roles_created"] += 1
        else:
            created_roles[existing_role.name] = existing_role.id
    
    # Создаем разрешения
    created_permissions = {}
    for perm_definition in PERMISSIONS_DEFINITIONS:
        existing_perm = await RBACService.get_permission_by_name(db, perm_definition.name)
        if not existing_perm:
            permission = await RBACService.create_permission(db, perm_definition)
            created_permissions[permission.name] = permission.id
            result["permissions_created"] += 1
        else:
            created_permissions[existing_perm.name] = existing_perm.id
    
    all_permission_ids = list(created_permissions.values())
    
    # Назначаем разрешения ролям
    for role_name, permission_names in ROLE_PERMISSIONS.items():
        role_id = created_roles.get(role_name)
        if not role_id:
            continue
        
        # Если "*" - назначаем все разрешения
        if "*" in permission_names:
            permission_ids = all_permission_ids
        else:
            permission_ids = [
                created_permissions[perm_name]
                for perm_name in permission_names
                if perm_name in created_permissions
            ]
        
        existing_rps = await db.execute(
            select(RolePermission).where(RolePermission.role_id == role_id)
        )
        existing_perm_ids = {rp.permission_id for rp in existing_rps.scalars().all()}
        
        for perm_id in permission_ids:
            if perm_id not in existing_perm_ids:
                rp = RolePermission(role_id=role_id, permission_id=perm_id)
                db.add(rp)
                result["role_permissions_assigned"] += 1
        
        await db.commit()
    
    return result


def print_init_results(results: dict):
    print("\n" + "="*50)
    print("RBAC System Initialization Results")
    print("="*50)
    print(f"Roles created: {results['roles_created']}")
    print(f"Permissions created: {results['permissions_created']}")
    print(f"Role permissions assigned: {results['role_permissions_assigned']}")
    print("="*50 + "\n")


async def init_rbac_data(db: AsyncSession) -> dict:
    print("Initializing RBAC system...")
    results = await init_roles_and_permissions(db)
    print_init_results(results)
    return results
