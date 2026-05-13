from src.posts.schemas import PostCreate, Post
from src.database import get_db
from bson import ObjectId

# đây là nơi nghiệp vụ , lẫn truy vấn @Service
class PostService:
    async def get_post(self, post_id: str):
        db = await get_db()
        post = await db["posts"].find_one({"_id": ObjectId(post_id)})
        return post

    async def create_post(self, post: PostCreate):
        db = await get_db()
        post_data = post.dict()
        await db["posts"].insert_one(post_data)
        return post_data

post_service = PostService()
