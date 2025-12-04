#!/usr/bin/env python3
# Cron script to log 2FA codes every minute

from datetime import datetime, timezone
import base64
import os
import sys

try:
    import pyotp
except Exception as e:
    print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - ERROR: pyotp not installed: {e}")
    sys.exit(1)

SEED_PATH = "/data/seed.txt"

def load_hex_seed(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            hex_seed = f.read().strip()
            if not hex_seed:
                return None
            return hex_seed
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - ERROR: failed to read seed: {e}")
        return None

def hex_to_base32(hex_string):
    try:
        b = bytes.fromhex(hex_string)
    except Exception:
        return None
    return base64.b32encode(b).decode("utf-8")

def generate_code(hex_seed):
    base32 = hex_to_base32(hex_seed)
    if base32 is None:
        return None
    totp = pyotp.TOTP(base32)
    return totp.now()

def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    hex_seed = load_hex_seed(SEED_PATH)
    if not hex_seed:
        print(f"{now} - ERROR: seed not found")
        return
    code = generate_code(hex_seed)
    if not code:
        print(f"{now} - ERROR: failed to generate code")
        return
    print(f"{now} - 2FA Code: {code}")

if __name__ == "__main__":
    main()