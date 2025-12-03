# decrypt_local_test.py
from pathlib import Path
from app.utils.crypto import load_private_key, decrypt_seed

ENC = Path("encrypted_seed.txt")
PRIV = Path("student_private.pem")

if not ENC.exists():
    raise SystemExit("encrypted_seed.txt missing")
if not PRIV.exists():
    raise SystemExit("student_private.pem missing")

enc_b64 = ENC.read_text(encoding="utf-8").strip()
priv = load_private_key(str(PRIV))
hex_seed = decrypt_seed(enc_b64, priv)
print("Decrypted seed:", hex_seed)
print("Length:", len(hex_seed))
