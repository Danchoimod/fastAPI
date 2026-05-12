from typing import Optional
from pydantic import BaseModel, Field

class PostModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str
    description: str
