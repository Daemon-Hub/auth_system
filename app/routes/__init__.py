from .mock import router as mock_router
from .user import router as user_router

routes = [
    mock_router, 
    user_router
]
