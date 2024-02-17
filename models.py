from pydantic import BaseModel
import uuid


class UUIDResponse(BaseModel):
    user_name: str
    uuid: uuid.UUID

class ImageData(BaseModel):
    image_path: str
    width: int
    height: int

class Imagebase64(BaseModel):
    base64_string: str
