from fastapi import APIRouter
from utils.response_formatter import success_response

router = APIRouter()

@router.get("/")
async def get_history(limit: int = 50):
    # For now, return empty history since we're using localStorage
    # This endpoint can be used later when implementing database storage
    return success_response({"history": []})