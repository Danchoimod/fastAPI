from enum import Enum

#định nghĩa tính nhất quán emum 
class ItemType(str, Enum):
    TEXT = "text"
    TODO = "todo"
    IMAGE = "image"
