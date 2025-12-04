#!/usr/bin/env python3
# Cron script to log 2FA codes every minute

from pathlib import Path
import time
import base64
import datetime
import sys

# function to generate TOTP (uses pyotp)
try:
    import pyotp
except Exception:
    print("ERROR: pyotp not installed", file=sys.stderr)
    sys.exit(1)

SEED_PATH = Path("/data/seed.txt")
OUT_FMT = "%Y-%m-%d %H:%M:%S"

def load_hex_seed():
    if not SEED_PATH.exists():
        return None
    try:
        s = SEED_PATH.read_text(encoding="utf-8").strip()
        if not s:
            return None
        return s
    except Exception as e:
        print(f"ERROR reading seed: {e}", file=sys.stderr)
        return None

def hex_to_base32(hex_seed):
    try:
        b = bytes.fromhex(hex_seed)
        return base64.b32encode(b).decode("utf-8")
    except Exception as e:
        raise

def main():
    hex_seed = load_hex_seed()
    now = datetime.datetime.utcnow().strftime(OUT_FMT)
    if not hex_seed:
        print(f"{now} - ERROR: seed not found")
        return
    try:
        b32 = hex_to_base32(hex_seed)
        totp = pyotp.TOTP(b32)
        code = totp.now()
        print(f"{now} - 2FA Code: {code}")
    except Exception as e:
        print(f"{now} - ERROR generating code: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()