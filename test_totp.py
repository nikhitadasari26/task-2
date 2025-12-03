from pathlib import Path
from app.totp_utils import generate_totp_code, verify_totp_code, seconds_remaining_in_period

if __name__ == "__main__":
    hex_seed = "27b07ca6e4b9428393ae6336f226c7f8004fc0ccb42404fcfd79374a1731c494"
    code = generate_totp_code(hex_seed)
    print("Code:", code, "valid_for:", seconds_remaining_in_period())
    print("Verify:", verify_totp_code(hex_seed, code))
