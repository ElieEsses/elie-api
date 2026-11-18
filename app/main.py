from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.projects.library.api.books import router as books_router
from app.projects.water.api.water import router as water_router

app = FastAPI(
    title="Elie's Project APIs",
    swagger_ui_parameters={
        "persistAuthorization": True if config.env == "dev" else False
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.frontend_url],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health", tags=["Health"])
def root():
    return {"status": "healthy"}


app.include_router(books_router)
app.include_router(water_router)
