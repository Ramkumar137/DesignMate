import os
import json
from typing import Optional


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Load a secret from env first, then backend/config.local.json if present."""
    value = os.getenv(name)
    if value:
        return value
    # Fallback to config.local.json next to this file's directory parent (backend)
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(backend_dir, "config.local.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and name in data and data[name]:
                    return str(data[name])
    except Exception:
        # Silent fallback
        pass
    return default


