# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from app.utils.crypto import load_private_key, decrypt_seed  # uses your crypto.py
import time

# === LOCAL DEV NOTE ===
# For local testing on Windows we use ./data so file appears in the repo.
# BEFORE building Docker change DATA_DIR to Path("/data") or use env var.
DATA_DIR = Path("/data")   # <--- use "./data" for local dev; change to "/data" for Docker
SEED_PATH = DATA_DIR / "seed.txt"

app = FastAPI()

class DecryptRequest(BaseModel):
    encrypted_seed: str

@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(req: DecryptRequest):
    # 1) load private key file from repo root
    priv_path = Path("student_private.pem")
    if not priv_path.exists():
        raise HTTPException(status_code=500, detail="student_private.pem not found")

    try:
        private_key = load_private_key(str(priv_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load private key: {e}")

    # 2) decrypt
    try:
        hex_seed = decrypt_seed(req.encrypted_seed, private_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {e}")

    # 3) persist to DATA_DIR/seed.txt
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SEED_PATH.write_text(hex_seed.strip().lower(), encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save seed: {e}")

    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok"}
# TOTP endpoints (added)
from app.totp_utils import generate_totp_code, verify_totp_code
import time
class VerifyRequest(BaseModel):
    code: str

@app.get("/generate-2fa")
async def generate_2fa():
    if not SEED_PATH.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    hex_seed = SEED_PATH.read_text().strip()
    code = generate_totp_code(hex_seed)
    valid_for = 30 - (int(time.time()) % 30)
    return {"code": code, "valid_for": valid_for}

@app.post("/verify-2fa")
async def verify_2fa(req: VerifyRequest):
    if not req.code:
        raise HTTPException(status_code=400, detail="Missing code")
    if not SEED_PATH.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    hex_seed = SEED_PATH.read_text().strip()
    valid = verify_totp_code(hex_seed, req.code, valid_window=1)
    return {"valid": valid}
