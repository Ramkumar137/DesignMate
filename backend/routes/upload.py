from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.file_handler import save_upload_file
from utils.response_formatter import success_response, error_response


router = APIRouter()




@router.post("/sketch")
async def upload_sketch(file: UploadFile = File(...)):
    try:
        saved_path = await save_upload_file(file)
        return success_response({"path": saved_path}, message="Uploaded")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))