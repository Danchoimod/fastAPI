from src.models import GlobalBaseModel
from pydantic import Field
#entity
class User(GlobalBaseModel):
    username: str = Field(..., unique=True)
    email: str = Field(..., unique=True)
    hashed_password: str
    is_active: bool = True
