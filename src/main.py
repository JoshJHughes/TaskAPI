from fastapi import FastAPI
from src.web.router import router

app = FastAPI()
app.include_router(router)
