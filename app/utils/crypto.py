import base64
from pathlib import Path
from typing import Any
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

def load_private_key(path: str, password: bytes | None = None) -> Any:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Private key not found: {path}")
    data = p.read_bytes()
    return load_pem_private_key(data, password=password)

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP-SHA256.
    Returns the 64-character hex seed string (lowercase).
    """
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64)
    except Exception as e:
        raise ValueError(f"Invalid base64 ciphertext: {e}")

    try:
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        raise ValueError(f"RSA decryption failed: {e}")

    try:
        txt = plaintext.decode("utf-8").strip()
    except Exception as e:
        raise ValueError(f"Failed to decode decrypted bytes as UTF-8: {e}")

    if len(txt) != 64:
        raise ValueError(f"Decrypted seed length is {len(txt)} (expected 64)")
    if any(c not in "0123456789abcdefABCDEF" for c in txt):
        raise ValueError("Decrypted seed contains non-hex characters")

    return txt.lower()
