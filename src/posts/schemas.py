from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]
#đâu ra của dữ liệu thay vì toàn bộ object, DTO (Data Transfer Object)
#@Valid, @NotBlank, @Size
class PostBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class PostCreate(PostBase):
    title: str

class Post(PostBase):
    id: PyObjectId = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True
