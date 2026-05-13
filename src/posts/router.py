from fastapi import APIRouter, Depends
from src.posts.service import post_service
from src.posts.schemas import Post, PostCreate

router = APIRouter()
#@RestController 
@router.get("/{post_id}", response_model=Post)
async def read_post(post_id: str):
    return await post_service.get_post(post_id)

@router.post("/", response_model=Post)
async def create_post(post: PostCreate):
    return await post_service.create_post(post)
