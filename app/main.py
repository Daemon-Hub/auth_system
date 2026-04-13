from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .settings import settings
from .database import create_tables, AsyncSessionLocal
from .routes.user import router
from .init_rbac_data import init_rbac_data
from .init_users_with_roles import init_users_with_roles

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()] 
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    
    async with AsyncSessionLocal() as db:
        await init_rbac_data(db)
        await init_users_with_roles(db)
        
    yield
    

app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,       
    allow_credentials=True,
    allow_methods=["*"],         
    allow_headers=["*"],         
)
