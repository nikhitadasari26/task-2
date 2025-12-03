import base64
import time
import pyotp

PERIOD_SECONDS = 30
DIGITS = 6

def hex_to_base32(hex_seed: str) -> str:
    b = bytes.fromhex(hex_seed)
    return base64.b32encode(b).decode("utf-8")

def generate_totp_code(hex_seed: str) -> str:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, interval=PERIOD_SECONDS, digits=DIGITS)
    return totp.now()

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    b32 = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, interval=PERIOD_SECONDS, digits=DIGITS)
    return totp.verify(code, valid_window=valid_window)

def seconds_remaining_in_period() -> int:
    now = int(time.time())
    elapsed = now % PERIOD_SECONDS
    return PERIOD_SECONDS - elapsed
