from bson import ObjectId
from bson.errors import InvalidId
import time
from typing import List, Optional, Sequence

from src.database import get_db
from src.note.models import Note, NoteItem
from src.note.schemas import NoteCreate, NoteUpdate, NoteSummary, NoteDetail, NoteItemBase
from src.note.constants import (
    NOTES_COLLECTION,
    NOTE_ITEMS_COLLECTION,
    ACTIVE_STATUS,
    DELETED_STATUS
)


# CÁC HÀM TRỢ GIÚP NỘI BỘ (PRIVATE HELPERS)

def _now() -> float:
    """
    Lấy thời gian hiện tại dưới dạng số thực Unix Timestamp (float).
    Ví dụ: 1716000000.0. Dễ lưu trữ, đồng bộ và sắp xếp hơn kiểu chuỗi.
    """
    return time.time()


def _to_object_id(note_id: str) -> Optional[ObjectId]:
    """
    Chuyển đổi chuỗi ID dạng chữ (str) thành đối tượng ObjectId của MongoDB.
    Nếu ID không hợp lệ, trả về None thay vì gây lỗi dừng chương trình.
    """
    try:
        return ObjectId(note_id)
    except (InvalidId, TypeError):
        return None


def _build_item_documents(
    note_id: str,
    owner_id: str,
    items: Sequence[NoteItemBase],
) -> list[dict]:
    """
    Chuẩn bị danh sách tài liệu (document) công việc con (NoteItem) để chèn vào database.
    Tự động gán thêm các thông tin hệ thống: note_id cha, chủ sở hữu, trạng thái và mốc thời gian.
    """
    timestamp = _now()
    documents = []

    for index, item in enumerate(items):
        item_dict = item.model_dump()
        item_dict.update({
            "note_id": note_id,
            "owner_id": owner_id,
            "order": item_dict.get("order", index),
            "status": ACTIVE_STATUS,
            "created_at": timestamp,
            "updated_at": timestamp,
        })
        documents.append(item_dict)

    return documents


async def _find_active_note(note_id: str) -> Optional[dict]:
    """
    Tìm kiếm một ghi chú (Note) đang hoạt động (chưa bị xóa mềm) theo ID.
    """
    object_id = _to_object_id(note_id)
    if object_id is None:
        return None

    db = await get_db()
    return await db[NOTES_COLLECTION].find_one({
        "_id": object_id,
        "status": {"$ne": DELETED_STATUS},
    })

# CÁC DỊCH VỤ NGHIỆP VỤ CHÍNH (BUSINESS SERVICES)

async def create_note(note_in: NoteCreate) -> Note:
    """
    Tạo mới một ghi chú cùng các công việc con (nếu có).
    Lưu ghi chú cha vào 'notes', lưu các công việc con vào 'note_items'.
    """
    db = await get_db()
    
    # 1. Tách thông tin ghi chú cha và loại bỏ mảng items để chèn riêng
    note_dict = note_in.model_dump(exclude={"items"})
    
    timestamp = _now()
    note_dict["status"] = ACTIVE_STATUS
    note_dict["created_at"] = timestamp
    note_dict["updated_at"] = timestamp

    # 2. Chèn ghi chú cha vào collection 'notes'
    result = await db[NOTES_COLLECTION].insert_one(note_dict)
    note_id = result.inserted_id

    # 3. Nếu có danh sách công việc con kèm theo, chuẩn bị và chèn vào 'note_items'
    if note_in.items:
        item_documents = _build_item_documents(str(note_id), note_in.owner_id, note_in.items)
        await db[NOTE_ITEMS_COLLECTION].insert_many(item_documents)

    note_dict["_id"] = note_id
    return Note(**note_dict)


async def get_user_notes(user_id: str) -> List[NoteSummary]:
    """
    Truy vấn toàn bộ ghi chú của người dùng kèm theo tổng số công việc
    và số lượng công việc đã hoàn thành (is_done=True) để hiển thị lên Sidebar.
    
    Sử dụng Aggregation Pipeline để nối bảng (JOIN) và tính toán trực tiếp trên Database.
    """
    db = await get_db()
    
    pipeline = [
        # Bước 1: Lọc ghi chú của user hiện tại và chưa bị xóa mềm
        {"$match": {"owner_id": user_id, "status": {"$ne": DELETED_STATUS}}},
        
        # Bước 2: Nối bảng 'note_items' (lookup) theo note_id dạng chuỗi chữ (string)
        {"$lookup": {
            "from": NOTE_ITEMS_COLLECTION,
            "let": {"note_id_str": {"$toString": "$_id"}}, # Chuyển _id của notes từ ObjectId -> string
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$note_id", "$$note_id_str"]}}},
                {"$match": {"status": {"$ne": DELETED_STATUS}}} # Bỏ qua các mục con đã bị xóa
            ],
            "as": "items" # Gán kết quả mảng nối được vào trường 'items'
        }},
        
        # Bước 3: Định dạng dữ liệu và tính toán thống kê (project)
        {"$project": {
            "title": 1,
            "order": 1,
            "items_count": {"$size": "$items"}, # Tổng số công việc con
            "done_count": {"$size": {"$filter": { # Số công việc con đã làm xong (is_done=True)
                "input": "$items",
                "as": "item",
                "cond": {"$eq": ["$$item.is_done", True]}
            }}}
        }},
        
        # Bước 4: Sắp xếp theo thứ tự kéo thả tăng dần
        {"$sort": {"order": 1}}
    ]
    
    cursor = db[NOTES_COLLECTION].aggregate(pipeline)
    notes = await cursor.to_list(length=100)
    return [NoteSummary(**n) for n in notes]


async def get_note_detail(note_id: str) -> Optional[NoteDetail]:
    """
    Lấy thông tin chi tiết của một ghi chú cụ thể bao gồm toàn bộ danh sách công việc con.
    """
    db = await get_db()
    
    # 1. Tìm ghi chú cha đang hoạt động
    note = await _find_active_note(note_id)
    if not note:
        return None

    # 2. Truy vấn danh sách các công việc con tương ứng, sắp xếp theo thứ tự hiển thị
    cursor = db[NOTE_ITEMS_COLLECTION].find({
        "note_id": str(note_id),
        "status": {"$ne": DELETED_STATUS}
    }).sort([("order", 1)])
    items = await cursor.to_list(length=200)

    # 3. Hợp nhất dữ liệu cha và con để trả về DTO NoteDetail
    note_data = dict(note)
    note_data["items"] = items
    return NoteDetail(**note_data)


async def update_note(note_id: str, note_update: NoteUpdate) -> Optional[NoteDetail]:
    """
    Cập nhật tiêu đề ghi chú cha và đồng bộ hóa danh sách công việc con.
    """
    db = await get_db()
    
    # 1. Kiểm tra sự tồn tại của ghi chú
    note = await _find_active_note(note_id)
    if not note:
        return None

    # 2. Cập nhật ghi chú cha nếu có dữ liệu mới truyền lên
    update_data = note_update.model_dump(exclude={"items"}, exclude_none=True)
    if update_data:
        update_data["updated_at"] = _now()
        await db[NOTES_COLLECTION].update_one(
            {"_id": note["_id"]},
            {"$set": update_data}
        )

    # 3. Đồng bộ hóa các công việc con (nếu mảng items được truyền lên từ Client)
    if note_update.items is not None:
        await sync_note_items(note_id, note["owner_id"], note_update.items)

    return await get_note_detail(note_id)


async def sync_note_items(note_id: str, owner_id: str, items_in: List[NoteItemBase]) -> List[NoteItem]:
    """
    Đồng bộ hóa các công việc con bằng phương án Re-create đơn giản và hiệu quả:
    Xóa toàn bộ công việc cũ của ghi chú này rồi chèn mới lại từ đầu.
    """
    db = await get_db()

    # 1. Xóa toàn bộ công việc cũ của ghi chú này
    await db[NOTE_ITEMS_COLLECTION].delete_many({"note_id": str(note_id)})

    # 2. Chuẩn bị tài liệu mới và chèn vào database
    item_documents = _build_item_documents(str(note_id), owner_id, items_in)
    if item_documents:
        await db[NOTE_ITEMS_COLLECTION].insert_many(item_documents)

    # 3. Trả về danh sách công việc mới đã được lưu thành công
    cursor = db[NOTE_ITEMS_COLLECTION].find({"note_id": str(note_id)}).sort([("order", 1)])
    new_items = await cursor.to_list(length=200)
    return [NoteItem(**item) for item in new_items]


async def delete_note(note_id: str) -> bool:
    """
    Xóa mềm (Soft Delete) ghi chú và toàn bộ công việc con kèm theo:
    Không xóa thực sự khỏi DB mà chỉ gắn trạng thái status = "deleted".
    """
    db = await get_db()
    
    # 1. Kiểm tra tính hợp lệ của ID
    object_id = _to_object_id(note_id)
    if object_id is None:
        return False

    # 2. Cập nhật trạng thái "deleted" trên ghi chú cha
    result = await db[NOTES_COLLECTION].update_one(
        {"_id": object_id, "status": {"$ne": DELETED_STATUS}},
        {"$set": {"status": DELETED_STATUS, "updated_at": _now()}}
    )

    if result.modified_count == 0:
        return False

    # 3. Cập nhật trạng thái "deleted" trên tất cả công việc con tương ứng
    await db[NOTE_ITEMS_COLLECTION].update_many(
        {"note_id": str(note_id)},
        {"$set": {"status": DELETED_STATUS, "updated_at": _now()}}
    )
    return True
