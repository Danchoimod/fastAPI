from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.posts.router import router as posts_router
from src.auth.router import router as auth_router
from src.config import settings
from src.database import connect_to_mongo, close_mongo_connection
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

# 1. LIFESPAN: Tương đương với @PostConstruct và @PreDestroy trong Spring
# Nó quản lý vòng đời của ứng dụng.
# Giống như việc kết nối DB khi khởi động Spring
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

# Cấu hình đường dẫn cho Swagger UI (openapi.json)
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(posts_router, prefix="/posts", tags=["posts"])
app.include_router(auth_router, prefix=settings.API_V1_STR)

# Giống @RestController
@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
