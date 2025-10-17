import os
import threading
from diffusers import StableDiffusionControlNetPipeline
import torch


# Singleton loader
class ModelLoader:
    _instance = None
    _lock = threading.Lock()


    def __init__(self):
        self.pipeline = None
        self.model_path = os.getenv("MODEL_PATH", "./models/SketchToUI_Model")


    @classmethod
    def instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance


    def load(self, device: str | None = None):
        if self.pipeline is not None:
            return self.pipeline


    # choose device
        device = device or ("cuda" if torch.cuda.is_available() else "cpu")


        # Example: load from local folder (ensure all required files exist)
        # You may need to adapt this depending on how you saved the pipeline.
        self.pipeline = StableDiffusionControlNetPipeline.from_pretrained(
        self.model_path,
        safety_checker=None,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        )
        self.pipeline = self.pipeline.to(device)
        self.pipeline.enable_attention_slicing()
        return self.pipeline