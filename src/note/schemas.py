from pydantic import BaseModel, Field
from typing import Optional, List
from src.models import GlobalBaseModel
from src.note.models import ItemType, Note, NoteItem

class NoteItemBase(BaseModel):
    type: ItemType = ItemType.TEXT
    content: str
    is_done: bool = False
    order: int = 0

class NoteItemCreate(NoteItemBase):
    note_id: str
    owner_id: str

class NoteItemUpdate(BaseModel):
    type: Optional[ItemType] = None
    content: Optional[str] = None
    is_done: Optional[bool] = None
    order: Optional[int] = None
    status: Optional[int] = None

class NoteBase(BaseModel):
    title: Optional[str] = Field(None, description="Tiêu đề ghi chú")
    order: int = 0

class NoteCreate(NoteBase):
    owner_id: str
    items: Optional[List[NoteItemBase]] = None # Có thể tạo note kèm items ban đầu

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[int] = None
    order: Optional[int] = None
    items: Optional[List[NoteItemBase]] = None

class NoteSummary(GlobalBaseModel):
    title: Optional[str] = None
    order: int = 0
    items_count: int = 0
    done_count: int = 0

class NoteDetail(Note):
    items: List[NoteItem] = Field(default_factory=list)

