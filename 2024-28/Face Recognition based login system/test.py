import base64
from deepface import DeepFace #type: ignore 
import numpy as np
import cv2
import os
from pathlib import Path
from numpy.linalg import norm
from dotenv import load_dotenv
import json
import logging
from typing import Optional, Tuple, Union

load_dotenv()


"""Constants"""
# Paths and storage
base_dir = Path(__file__).resolve().parent
user_storage_dir = Path(os.getenv("STORAGE_DIR") or (base_dir / "data")).resolve()
user_storage_dir.mkdir(parents=True, exist_ok=True)

user_file = os.getenv("USER_FILE") or str(user_storage_dir / "users.json")

embedding_dir = os.getenv("EMBEDDINGS_DIR") or os.getenv("EMBEDDING_DIR") or str(user_storage_dir / "embeddings")
Path(embedding_dir).mkdir(parents=True, exist_ok=True)

jwt_secret_key = os.getenv("JWT_SECRET_KEY")

# Tunables
DEFAULT_SIM_THRESHOLD: float = float(os.getenv("FACE_SIM_THRESHOLD", "0.75"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.WARNING))


"""User management"""

def load_users():
    """Load users JSON safely. Returns an empty dict on any error."""
    if not user_file:
        return {}

    path = Path(user_file)
    if not path.exists() or path.stat().st_size == 0:
        return {}

    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
    except Exception:
        return {}

def save_users(users):
    """Persist users JSON safely. Creates parent dirs if needed and ignores IO errors."""
    if not user_file:
        return

    path = Path(user_file)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as f:
            json.dump(users, f, indent=4)
    except Exception:
        pass
        
    
"""Image Embedding generation"""

def normalize_vector(v: np.ndarray) -> np.ndarray:
    """L2-normalize a vector safely with epsilon to avoid division by zero."""
    try:
        n = float(norm(v))
    except Exception:
        return v
    if not np.isfinite(n) or n == 0.0:
        return v
    return v / (n + 1e-8)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors with normalization and safety checks."""
    a_n = normalize_vector(a)
    b_n = normalize_vector(b)
    try:
        sim = float(np.dot(a_n, b_n))
    except Exception:
        return -1.0
    if not np.isfinite(sim):
        return -1.0
    return sim

# Decode base64 image
def decode_base64_image(image: Union[str, bytes, bytearray, memoryview]) -> Optional[np.ndarray]:
    """Decode a base64 string (optionally data URL) or raw bytes into an OpenCV image.

    Returns None if decoding fails.
    """
    try:
        if isinstance(image, (bytes, bytearray, memoryview)):
            data = image
        else:
            # Accept data URLs like "data:image/png;base64,..."
            payload = image.split(',')[-1].strip()
            data = base64.b64decode(payload, validate=False)
        arr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None

# Get embeddings from image
def get_embeddings(image: Union[np.ndarray, str]) -> Optional[np.ndarray]:
    """Compute a face embedding using DeepFace and return a normalized vector or None."""
    try:
        out = DeepFace.represent(
            img_path=image,
            model_name="Facenet",
            enforce_detection=True,
            detector_backend='opencv',
        )
        embedding = np.array((out or [{}])[0].get('embedding', []), dtype=np.float32)
        if embedding.size == 0:
            return None
        return normalize_vector(embedding)
    except Exception:
        return None
    

def compare_embeddings(emb1: np.ndarray, emb2: np.ndarray, threshold: float = DEFAULT_SIM_THRESHOLD) -> bool:
    """Return True if cosine similarity >= threshold, else False."""
    sim = cosine_similarity(emb1, emb2)
    return sim >= float(threshold)



