from src.posts.schemas import PostCreate

class PostService:
    def get_post(self, post_id: int):
        return {"id": post_id, "title": "Sample Post", "description": "Domain-based logic"}

    def create_post(self, post: PostCreate):
        return {"id": 1, **post.dict()}

post_service = PostService()
