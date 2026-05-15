from fastapi import APIRouter, HTTPException, status
from src.note.schemas import NoteCreate, Note, NoteUpdate, NoteSummary, NoteDetail
from src.note import service
from typing import List

router = APIRouter(tags=["Notes"])

@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(note_in: NoteCreate):
    """Tạo ghi chú mới"""
    return await service.create_note(note_in)

@router.get("/user/{user_id}", response_model=List[NoteSummary])
async def get_user_notes(user_id: str):
    """Lấy danh sách ghi chú (Summary) của một User"""
    return await service.get_user_notes(user_id)

@router.get("/{note_id}", response_model=NoteDetail)
async def get_note(note_id: str):
    """Lấy chi tiết một ghi chú (bao gồm items)"""
    note = await service.get_note_detail(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Ghi chú không tồn tại")
    return note

@router.put("/{note_id}", response_model=NoteDetail)
async def update_note(note_id: str, note_in: NoteUpdate):
    """Cập nhật ghi chú và items"""
    note = await service.update_note(note_id, note_in)
    if not note:
        raise HTTPException(status_code=404, detail="Không tìm thấy ghi chú để cập nhật")
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: str):
    """Xóa ghi chú và items liên quan (Soft delete)"""
    success = await service.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy ghi chú để xóa")
    return None
