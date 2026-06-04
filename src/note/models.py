from enum import Enum
from pydantic import Field
from src.models import GlobalBaseModel

# định nghĩa tính nhất quán enum 
class ItemType(str, Enum):
    TEXT = "text"
    TODO = "todo"
    IMAGE = "image"

# Entity NoteItem: Đại diện cho cấu trúc lưu dưới Database
class NoteItem(GlobalBaseModel):
    note_id: str
    owner_id: str
    type: ItemType = ItemType.TEXT
    content: str
    is_done: bool = False
    order: int = 0
    status: int
    created_at: float
    updated_at: float

# Entity Note: Đại diện cho cấu trúc lưu dưới Database
class Note(GlobalBaseModel):
    owner_id: str
    title: str | None = Field(None, description="Tiêu đề ghi chú")
    order: int = 0
    status: int
    created_at: float
    updated_at: float

