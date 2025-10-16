from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from utils.response_formatter import success_response
from models.inference import generate_from_sketch


router = APIRouter()




@router.post("/run")
async def generate_endpoint(
sketch: UploadFile = File(...),
prompt: str = Form(...),
guidance: float = Form(7.5),
steps: int = Form(30),
):
    try:
        sketch_bytes = await sketch.read()
        result = generate_from_sketch(sketch_bytes, prompt, guidance, steps)
        return success_response(result)
    except Exception as e:
        # Log the error server-side and return structured error
        print(f"/generate/run error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.options("/run")
async def generate_options():
    # Allow CORS preflight explicitly
    return {"ok": True}