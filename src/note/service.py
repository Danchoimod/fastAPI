from bson import ObjectId
from bson.errors import InvalidId
import time
from typing import List, Optional, Sequence

from src.database import get_db
from src.note.schemas import NoteCreate, Note, NoteUpdate, NoteSummary, NoteDetail, NoteItem, NoteItemBase
from src.note.constants import (
    NOTES_COLLECTION,
    NOTE_ITEMS_COLLECTION,
    ACTIVE_STATUS,
    DELETED_STATUS
) #import từ Final class 


def _now() -> float:
    return time.time() # tạo hàm lấy thời gian


def _to_object_id(note_id: str) -> Optional[ObjectId]: #hàm 
    try:
        return ObjectId(note_id)
    except (InvalidId, TypeError):
        return None


def _build_item_documents( #khi có dấu _function thì lớp đó là private class ngược lại
    note_id: str,
    owner_id: str,
    items: Sequence[NoteItemBase],
) -> list[dict]:
    timestamp = _now()
    documents = []

    for index, item in enumerate(items): # duyệt mảng 
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
    object_id = _to_object_id(note_id)
    if object_id is None:
        return None

    db = await get_db()
    return await db[NOTES_COLLECTION].find_one({
        "_id": object_id,
        "status": {"$ne": DELETED_STATUS},
    })

async def create_note(note_in: NoteCreate) -> Note:
    db = await get_db()
    note_dict = note_in.model_dump(exclude={"items"})

    timestamp = _now()
    note_dict["status"] = ACTIVE_STATUS
    note_dict["created_at"] = timestamp
    note_dict["updated_at"] = timestamp

    result = await db[NOTES_COLLECTION].insert_one(note_dict)
    note_id = result.inserted_id

    if note_in.items:
        item_documents = _build_item_documents(str(note_id), note_in.owner_id, note_in.items)
        await db[NOTE_ITEMS_COLLECTION].insert_many(item_documents)

    note_dict["_id"] = note_id
    return Note(**note_dict)

async def get_user_notes(user_id: str) -> List[NoteSummary]:
    db = await get_db()
    
    pipeline = [
        {"$match": {"owner_id": user_id, "status": {"$ne": DELETED_STATUS}}},
        {"$lookup": {
            "from": NOTE_ITEMS_COLLECTION,
            "let": {"note_id_str": {"$toString": "$_id"}},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$note_id", "$$note_id_str"]}}},
                {"$match": {"status": {"$ne": DELETED_STATUS}}}
            ],
            "as": "items"
        }},
        {"$project": {
            "title": 1,
            "order": 1,
            "items_count": {"$size": "$items"},
            "done_count": {"$size": {"$filter": {
                "input": "$items",
                "as": "item",
                "cond": {"$eq": ["$$item.is_done", True]}
            }}}
        }},
        {"$sort": {"order": 1}}
    ]
    
    cursor = db[NOTES_COLLECTION].aggregate(pipeline)
    notes = await cursor.to_list(length=100)
    return [NoteSummary(**n) for n in notes]

async def get_note_detail(note_id: str) -> Optional[NoteDetail]:
    db = await get_db()
    note = await _find_active_note(note_id)
    if not note:
        return None

    cursor = db[NOTE_ITEMS_COLLECTION].find({
        "note_id": str(note_id),
        "status": {"$ne": DELETED_STATUS}
    }).sort([("order", 1)])
    items = await cursor.to_list(length=200)

    note_data = dict(note)
    note_data["items"] = items
    return NoteDetail(**note_data)

async def update_note(note_id: str, note_update: NoteUpdate) -> Optional[NoteDetail]:
    db = await get_db()
    note = await _find_active_note(note_id)
    if not note:
        return None

    update_data = note_update.model_dump(exclude={"items"}, exclude_none=True)
    if update_data:
        update_data["updated_at"] = _now()
        await db[NOTES_COLLECTION].update_one(
            {"_id": note["_id"]},
            {"$set": update_data}
        )

    if note_update.items is not None:
        await sync_note_items(note_id, note["owner_id"], note_update.items)

    return await get_note_detail(note_id)

async def sync_note_items(note_id: str, owner_id: str, items_in: List[NoteItemBase]) -> List[NoteItem]:
    db = await get_db()

    await db[NOTE_ITEMS_COLLECTION].delete_many({"note_id": str(note_id)})

    item_documents = _build_item_documents(str(note_id), owner_id, items_in)
    if item_documents:
        await db[NOTE_ITEMS_COLLECTION].insert_many(item_documents)

    cursor = db[NOTE_ITEMS_COLLECTION].find({"note_id": str(note_id)}).sort([("order", 1)])
    new_items = await cursor.to_list(length=200)
    return [NoteItem(**item) for item in new_items]

async def delete_note(note_id: str) -> bool: # -> khẳng định sẽ trả đúng/sai
    db = await get_db()
    object_id = _to_object_id(note_id)
    if object_id is None:
        return False

    result = await db[NOTES_COLLECTION].update_one(
        {"_id": object_id, "status": {"$ne": DELETED_STATUS}},
        {"$set": {"status": DELETED_STATUS, "updated_at": _now()}}
    )

    if result.modified_count == 0:
        return False

    await db[NOTE_ITEMS_COLLECTION].update_many(
        {"note_id": str(note_id)},
        {"$set": {"status": DELETED_STATUS, "updated_at": _now()}}
    )
    return True
