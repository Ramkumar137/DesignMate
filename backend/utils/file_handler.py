import os
from pathlib import Path
from fastapi import UploadFile
import secrets
from PIL import Image
import io


OUTPUT_PATH = Path(os.getenv("OUTPUT_PATH", "./static/outputs"))
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
LATEST_FILENAME = os.getenv("LATEST_FILENAME", "latest.png")




async def save_upload_file(upload_file: UploadFile) -> str:
# create secure filename
    ext = Path(upload_file.filename).suffix or ".png"
    token = secrets.token_hex(8)
    fname = f"sketch_{token}{ext}"
    fpath = OUTPUT_PATH / fname


    contents = await upload_file.read()
    with open(fpath, "wb") as f:
        f.write(contents)
    return str(fpath)




def save_image_to_outputs(image: Image.Image, prefix: str = "out") -> str:
    token = secrets.token_hex(8)
    fname = f"{prefix}_{token}.png"
    fpath = OUTPUT_PATH / fname
    image.save(fpath, format="PNG")
    return str(fpath)


def save_image_and_latest(image: Image.Image, prefix: str = "out") -> tuple[str, str]:
    """Save with a unique filename and also overwrite the stable latest file.

    Returns (unique_file_path, latest_file_path)
    """
    unique = save_image_to_outputs(image, prefix=prefix)
    latest_path = OUTPUT_PATH / LATEST_FILENAME
    try:
        image.save(latest_path, format="PNG")
    except Exception:
        pass
    return unique, str(latest_path)




def image_to_base64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()