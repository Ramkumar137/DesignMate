from fastapi import APIRouter, HTTPException, Response, UploadFile, File, Form
from pydantic import BaseModel
from services.gemini_service import GeminiService
from utils.response_formatter import success_response
import base64
import io
from PIL import Image

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


@router.post("/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    message: str = Form(...)
):
    """
    Analyze an uploaded image and generate a design prompt using Gemini API
    """
    if not gemini_service:
        raise HTTPException(
            status_code=500, 
            detail="Gemini service is not available. Please check GEMINI_API_KEY environment variable."
        )
    
    try:
        # Read and process the image
        image_data = await image.read()
        
        # Convert to base64 for Gemini API
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Create the prompt for image analysis
        analysis_prompt = f"""
        {message}
        
        Please analyze this uploaded image and provide a detailed, professional prompt that could be used to generate a UI/UX design based on this sketch. 
        Focus on:
        - Layout and structure
        - Design elements and components
        - Color schemes and visual hierarchy
        - User experience considerations
        - Modern design principles
        
        Provide a clear, actionable description that could be used as input for an AI design generation system.
        """
        
        # Use Gemini's vision capabilities
        response = gemini_service.analyze_image_with_text(image_base64, analysis_prompt)
        return success_response({"response": response})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.options("/chat")
async def chat_options():
    # Explicit CORS preflight support
    return Response(status_code=204)


@router.options("/analyze-image")
async def analyze_image_options():
    # Explicit CORS preflight support
    return Response(status_code=204)

