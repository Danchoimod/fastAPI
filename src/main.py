from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.note.router import router as note_router
from src.config import settings
from src.database import connect_to_mongo, close_mongo_connection
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware


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
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)


# Thêm CORS Middleware để cho phép Frontend (Next.js) gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://aurabook-kappa.vercel.app"
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.gemini.router import router as gemini_router
from src.storage.router import router as storage_router

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(note_router, prefix=f"{settings.API_V1_STR}/notes", tags=["notes"])

app.include_router(auth_router, prefix=settings.API_V1_STR)

app.include_router(gemini_router, prefix=f"{settings.API_V1_STR}/gemini", tags=["gemini"])

app.include_router(storage_router, prefix=settings.API_V1_STR)
