from typing import Optional
from pydantic import BaseModel, Field
#@Entity / @Table
class PostModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str
    description: str
