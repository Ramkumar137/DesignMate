from fastapi import APIRouter, Body, HTTPException
from services.gemini_service import GeminiService
from utils.response_formatter import success_response


router = APIRouter()




@router.post("/ask")
async def recommend_endpoint(payload: dict = Body(...)):
    """
    payload example: {"prompt": "How to improve this UI?", "context": "...optional..."}
    """
    try:
        prompt = payload.get("prompt")
        context = payload.get("context")
        gs = GeminiService()
        resp = gs.ask(prompt, context)
        return success_response({"answer": resp})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))