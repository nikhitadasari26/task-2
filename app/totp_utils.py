# app/totp_utils.py
import base64
import pyotp

PERIOD_SECONDS = 30
DIGITS = 6

def hex_to_base32(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode("utf-8")

def generate_totp_code(hex_seed: str) -> str:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, digits=DIGITS, interval=PERIOD_SECONDS)  # SHA-1 default
    return totp.now()

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, digits=DIGITS, interval=PERIOD_SECONDS)
    return bool(totp.verify(code, valid_window=valid_window))
