#!/usr/bin/env python3
import os, sys, base64
from datetime import datetime, timezone
import pyotp

SEED_PATH = '/data/seed.txt'

def read_hex_seed():
    try:
        return open(SEED_PATH).read().strip()
    except:
        return None

def hex_to_base32(hex_seed):
    b = bytes.fromhex(hex_seed)
    return base64.b32encode(b).decode('utf-8')

def main():
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    hex_seed = read_hex_seed()
    if not hex_seed:
        print(f"{ts} - ERROR: seed not found")
        return
    try:
        b32 = hex_to_base32(hex_seed)
        code = pyotp.TOTP(b32).now()
        print(f"{ts} - 2FA Code: {code}")
    except Exception as e:
        print(f"{ts} - ERROR: {e}")

if __name__ == '__main__':
    main()
