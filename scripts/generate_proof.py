import sys, base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

def sign_message(message: str, private_key_pem: bytes) -> bytes:
    priv = load_pem_private_key(private_key_pem, password=None)
    signature = priv.sign(
        message.encode('utf-8'),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return signature

def encrypt_with_public_key(data: bytes, public_key_pem: bytes) -> bytes:
    pub = load_pem_public_key(public_key_pem)
    ct = pub.encrypt(
        data,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return ct

def main():
    if len(sys.argv) != 4:
        print("Usage: python scripts/generate_proof.py <commit_hash> <student_private.pem> <instructor_public.pem>")
        sys.exit(2)
    commit_hash = sys.argv[1].strip()
    if len(commit_hash) != 40:
        print("Error: commit_hash must be 40 hex characters.")
        sys.exit(2)
    student_priv_path = Path(sys.argv[2])
    instructor_pub_path = Path(sys.argv[3])
    if not student_priv_path.exists() or not instructor_pub_path.exists():
        print("Error: missing key files.")
        sys.exit(2)
    priv_pem = student_priv_path.read_bytes()
    pub_pem = instructor_pub_path.read_bytes()
    sig = sign_message(commit_hash, priv_pem)
    ct = encrypt_with_public_key(sig, pub_pem)
    b64 = base64.b64encode(ct).decode('ascii')
    print(b64)

if __name__ == '__main__':
    main()
