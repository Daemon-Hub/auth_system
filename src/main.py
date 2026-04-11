from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .settings import settings
from .database import create_tables
from .routes.user import router

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()] 
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
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
