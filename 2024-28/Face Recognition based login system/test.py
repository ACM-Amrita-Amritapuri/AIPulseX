import base64
from deepface import DeepFace #type: ignore 
import numpy as np
import cv2
import os
from pathlib import Path
from numpy.linalg import norm
from dotenv import load_dotenv
import json

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

# Decode base64 image
def decode_base64_image(image):
    data=base64.b64decode(image)
    arr=np.frombuffer(data,np.uint8)
    return cv2.imdecode(arr,cv2.IMREAD_COLOR) 

# Get embeddings from image
def get_embeddings(image):
    try:
        out=DeepFace.represent(img_path=image,model_name="Facenet",enforce_detection=True)
        emb=np.array(out[0]['embedding'],dtype=np.float32)
        emb /=norm(emb)
        return emb
    except Exception as e:
        print(e)
        return None
    

# Compare two embeddings
def compare_embeddings(emb1,emb2,threshold=0.75):
    cos_sim=np.dot(emb1,emb2)/(norm(emb1)* norm(emb2))
    if cos_sim >= threshold:
        return True
    else:
        return False
