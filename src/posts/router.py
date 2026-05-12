from fastapi import APIRouter, Depends
from src.posts.service import post_service
from src.posts.schemas import Post, PostCreate

router = APIRouter()

@router.get("/{post_id}", response_model=Post)
def read_post(post_id: int):
    return post_service.get_post(post_id)

@router.post("/", response_model=Post)
def create_post(post: PostCreate):
    return post_service.create_post(post)
