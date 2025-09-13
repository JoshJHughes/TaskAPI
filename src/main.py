from fastapi import FastAPI
from src.web.routers import router

app = FastAPI()
app.include_router(router)
