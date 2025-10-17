import io
import base64
from PIL import Image
import torch
from models.model_loader import ModelLoader
from utils.file_handler import save_image_to_outputs, save_image_and_latest
import os
from services.hf_enhance_service import HFEnhanceService
from controlnet_aux import CannyDetector
from PIL import Image as PILImage
from services.hf_generate_service import HFGenerateService

device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize pipeline via singleton loader on the best available device
pipe = ModelLoader.instance().load(device=device)

def pil_image_from_bytes(bytes_data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(bytes_data)).convert("RGB")

def generate_from_sketch(
        sketch_bytes: bytes,
        prompt: str,
        guidance: float = 7.5,
        num_inference_steps: int = 30
) -> dict:
    """
    Returns dict: { 'image_path': str, 'image_base64': str }
    """
    # pipeline = ModelLoader.instance().load()


    # prepare input
    sketch = pil_image_from_bytes(sketch_bytes)
    # Normalize resolution for stability
    try:
        sketch = sketch.resize((512, 512), PILImage.LANCZOS)
    except Exception:
        pass
    # Optionally use HF text/img2img generation instead of local ControlNet
    if os.getenv("GENERATION_BACKEND", "local").lower() == "hf":
        try:
            hf_gen = HFGenerateService()
            if hf_gen.is_enabled():
                generated = hf_gen.generate(prompt, sketch)
                if generated is not None:
                    image = generated
                    # Skip local pipeline entirely
                    enhancer = HFEnhanceService()
                    if enhancer.is_enabled():
                        try:
                            image = enhancer.enhance(image, prompt=prompt)
                        except Exception as e:
                            print(f"HF enhance after HF gen failed: {e}")
                    # save + return
                    out_path = save_image_to_outputs(image)
                    abs_path = os.path.abspath(out_path)
                    parts = abs_path.replace("\\", "/").split("/static/")
                    web_path = f"/static/{parts[1]}" if len(parts) == 2 else out_path.replace("\\", "/")
                    include_b64 = os.getenv("RETURN_BASE64", "false").lower() in {"1", "true", "yes"}
                    if include_b64:
                        buff = io.BytesIO(); image.save(buff, format="PNG")
                        return {"image_path": web_path, "image_base64": base64.b64encode(buff.getvalue()).decode()}
                    return {"image_path": web_path}
        except Exception as e:
            print(f"HF generation fallback to local due to: {e}")

    # ControlNet: Canny conditioning to preserve structure (best-effort)
    try:
        canny = CannyDetector()
        sketch = canny(sketch)
    except Exception:
        pass


# If your pipeline expects a specific conditioning, adapt here.
# This is a straight-forward call; adjust to your ControlNet conditioning API.
    generator = torch.Generator(device=pipe.device)


    # Strengthen conditioning for higher quality UI/3D outputs
    style_suffix = (
        ", clean layout, consistent spacing, modern typography, high contrast,"
        " photorealistic 3D product render, studio lighting, detailed materials"
    )
    negative_suffix = ", cartoon, distorted, low quality, text overlay, fake texture"
    conditioned_prompt = f"{prompt}{style_suffix}"

    with torch.autocast(device_type=str(pipe.device), dtype=torch.float16 if str(pipe.device).startswith("cuda") else torch.float32):
        output = pipe(
            prompt=conditioned_prompt,
            negative_prompt=negative_suffix,
            image=sketch,
            guidance_scale=guidance,
            num_inference_steps=num_inference_steps,
            generator=generator,
        )


    image = output.images[0]

    # Optional enhancement via Hugging Face Inference API
    enhancer = HFEnhanceService()
    if enhancer.is_enabled():
        try:
            # Guide enhancer with a stronger instruction while passing original intent
            enhance_prompt = (
                f"Refine and modernize this design. {prompt}. Maintain structure, "
                f"improve aesthetics, add realistic 3D materials and lighting."
            )
            image = enhancer.enhance(image, prompt=enhance_prompt)
        except Exception as enhance_error:
            # Never fail the request because of enhancement; return base image
            print(f"HF enhancement error: {enhance_error}")


    # save file (unique + latest)
    out_path, latest_path = save_image_and_latest(image)

    # Normalize to web path under /static
    try:
        # If path is within backend/static, expose under /static
        abs_path = os.path.abspath(out_path)
        # Find 'static' segment and rebuild as /static/...
        parts = abs_path.replace("\\", "/").split("/static/")
        if len(parts) == 2:
            web_path = f"/static/{parts[1]}"
        else:
            # Fallback to original
            web_path = out_path.replace("\\", "/")
    except Exception:
        web_path = out_path.replace("\\", "/")

    # Also compute stable web path for latest
    try:
        latest_abs = os.path.abspath(latest_path)
        lparts = latest_abs.replace("\\", "/").split("/static/")
        latest_web = f"/static/{lparts[1]}" if len(lparts) == 2 else latest_path.replace("\\", "/")
    except Exception:
        latest_web = web_path


    # Optionally include base64 (can be very large). Default off.
    include_b64 = os.getenv("RETURN_BASE64", "false").lower() in {"1", "true", "yes"}
    if include_b64:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()
        return {"image_path": web_path, "latest_path": latest_web, "image_base64": img_b64}
    return {"image_path": web_path, "latest_path": latest_web}