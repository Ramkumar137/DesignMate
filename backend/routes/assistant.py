from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from services.gemini_service import GeminiService
from utils.response_formatter import success_response

router = APIRouter()

# Initialize Gemini service
try:
    gemini_service = GeminiService()
except RuntimeError as e:
    print(f"Warning: {e}")
    gemini_service = None


class ChatRequest(BaseModel):
    message: str
    context: str | None = None


@router.post("/chat")
async def chat_with_assistant(request: ChatRequest):
    """
    Chat with the AI assistant using Gemini API
    """
    if not gemini_service:
        raise HTTPException(
            status_code=500, 
            detail="Gemini service is not available. Please check GEMINI_API_KEY environment variable."
        )
    
    try:
        response = gemini_service.ask(request.message, request.context)
        return success_response({"response": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def assistant_health():
    """
    Check if the assistant service is healthy
    """
    return success_response({
        "status": "healthy" if gemini_service else "unhealthy",
        "gemini_available": gemini_service is not None
    })


@router.options("/chat")
async def chat_options():
    # Explicit CORS preflight support
    return Response(status_code=204)

