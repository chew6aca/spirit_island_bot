from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import create_tables, delete_tables
from router import router as spirit_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print('Database created')
    yield
    await delete_tables()
    print('Database erased')

app = FastAPI()
app.include_router(spirit_router)
