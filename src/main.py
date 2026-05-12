from fastapi import FastAPI
from src.posts.router import router as posts_router
from src.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(posts_router, prefix="/posts", tags=["posts"])

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Project (Domain-based Structure)"}
