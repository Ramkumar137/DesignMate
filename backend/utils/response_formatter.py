from fastapi import HTTPException




def success_response(data: dict | list | str = None, message: str = "success") -> dict:
    return {"status": "ok", "message": message, "data": data}




def error_response(message: str, code: int = 400):
    raise HTTPException(status_code=code, detail=message)