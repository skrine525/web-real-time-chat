from fastapi.routing import APIRouter
from fastapi import  Depends
from app.utils.auth import get_current_user
from app.schemas import user as user_schema


router = APIRouter(prefix="/users") 


@router.get("/me", response_model=user_schema.User)
async def get_me(current_user: user_schema.User = Depends(get_current_user)):
    return current_user