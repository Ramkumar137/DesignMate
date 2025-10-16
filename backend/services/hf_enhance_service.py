import os
import io
import base64
from typing import Optional
import requests
from PIL import Image
from services.config_loader import get_secret


class HFEnhanceService:
    def __init__(self):
        self.api_key = get_secret("HF_API_KEY")
        self.model_id = os.getenv("HF_ENHANCE_MODEL", "timbrooks/instruct-pix2pix")
        self.timeout_seconds = int(os.getenv("HF_TIMEOUT", "60"))

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def _image_to_bytes(self, image: Image.Image) -> bytes:
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()

    def enhance(self, image: Image.Image, prompt: Optional[str] = None) -> Image.Image:
        if not self.is_enabled():
            return image

        api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Many img2img models (e.g., timbrooks/instruct-pix2pix) accept multipart with fields
        #   image: binary, prompt: text
        files = {"image": ("input.png", self._image_to_bytes(image), "image/png")}
        data = {
            # Some models read 'prompt', others read 'inputs'; we include both
            "prompt": prompt or "Improve the visual design while preserving layout and structure",
            "inputs": prompt or "Improve the visual design while preserving layout and structure",
        }

        resp = requests.post(api_url, headers=headers, data=data, files=files, timeout=self.timeout_seconds)
        resp.raise_for_status()

        # HF image models may return raw bytes for image outputs depending on model; attempt to parse
        try:
            # If JSON, attempt base64 or error
            if resp.headers.get("content-type", "").startswith("application/json"):
                data = resp.json()
                if isinstance(data, list) and len(data) and isinstance(data[0], dict) and "image" in data[0]:
                    img_b64 = data[0]["image"]
                    return Image.open(io.BytesIO(base64.b64decode(img_b64))).convert("RGB")
                raise RuntimeError(f"HF API returned JSON: {data}")
            return Image.open(io.BytesIO(resp.content)).convert("RGB")
        except Exception as e:
            # If enhancement fails, fall back to original image
            print(f"HF enhancement failed: {e}")
            return image


