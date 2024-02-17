from fastapi import APIRouter,Path 
from models import UUIDResponse
import uuid

router = APIRouter()


@router.get("/api/{user_name}", response_model=UUIDResponse)
async def get_uuid(user_name: str = Path(..., title="User Name", description="The name of the user")):
    # Generate a random UUID
    random_uuid = uuid.uuid4()
    return {"user_name": user_name, "uuid": random_uuid}