import io
import base64
import os
from typing import Optional
import requests
from PIL import Image
from services.config_loader import get_secret


class HFGenerateService:
    def __init__(self):
        self.api_key = get_secret("HF_API_KEY")
        # Default to SDXL base text2img; many img2img-capable models accept an image field too
        self.model_id = os.getenv("HF_GEN_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
        self.timeout_seconds = int(os.getenv("HF_TIMEOUT", "60"))

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def _image_to_bytes(self, image: Image.Image) -> bytes:
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()

    def generate(self, prompt: str, sketch: Optional[Image.Image] = None) -> Optional[Image.Image]:
        if not self.is_enabled():
            return None

        api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        data = {
            "inputs": prompt,
            "prompt": prompt,
        }
        files = None
        if sketch is not None:
            # Try img2img by including an image field; models that don't support it may ignore
            files = {
                "image": ("sketch.png", self._image_to_bytes(sketch), "image/png")
            }

        resp = requests.post(api_url, headers=headers, data=data if files else None, json=(None if files else data), files=files, timeout=self.timeout_seconds)
        resp.raise_for_status()

        # Try to interpret result as image
        ctype = resp.headers.get("content-type", "")
        if ctype.startswith("application/json"):
            payload = resp.json()
            # Some HF endpoints return a list of dicts with base64 images
            if isinstance(payload, list) and payload and isinstance(payload[0], dict) and "image" in payload[0]:
                img_b64 = payload[0]["image"]
                return Image.open(io.BytesIO(base64.b64decode(img_b64))).convert("RGB")
            # If JSON without image, consider unsupported
            return None

        try:
            return Image.open(io.BytesIO(resp.content)).convert("RGB")
        except Exception:
            return None


