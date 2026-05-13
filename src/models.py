# Cấu hình để tất cả các Model trong dự án đều tự hiểu ID từ MongoDB
# tính kế thừa (lớp cha)

# src/models.py
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from typing import Annotated, Optional

# Định nghĩa kiểu dữ liệu ObjectId thành chuỗi (String)
PyObjectId = Annotated[str, BeforeValidator(str)]

class GlobalBaseModel(BaseModel):
    # Tất cả các Model kế thừa từ đây sẽ tự động có trường id
    id: Optional[PyObjectId] = Field(None, alias="_id")

    # Cấu hình Pydantic
    model_config = ConfigDict(
        # Cho phép dùng cả tên "id" và "_id"
        populate_by_name=True,
        # Hỗ trợ chuyển đổi từ object (giống như từ Entity sang DTO)
        from_attributes=True,
    )
