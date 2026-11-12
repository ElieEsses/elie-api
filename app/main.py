from config import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.books import router as books_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        config.frontend_url
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/health", tags=["Health"])
def root():
    return {"status": "healthy"}

app.include_router(books_router)