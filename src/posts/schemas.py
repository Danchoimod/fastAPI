from pydantic import BaseModel
from typing import Optional

class PostBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class PostCreate(PostBase):
    title: str

class Post(PostBase):
    id: int

    class Config:
        from_attributes = True
