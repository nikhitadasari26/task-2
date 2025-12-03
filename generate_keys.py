from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Parameters
KEY_SIZE = 4096
PUBLIC_EXPONENT = 65537
PRIVATE_PATH = "student_private.pem"
PUBLIC_PATH = "student_public.pem"

def main():
    # generate private key
    private_key = rsa.generate_private_key(
        public_exponent=PUBLIC_EXPONENT,
        key_size=KEY_SIZE
    )

    # serialize private key (PEM, PKCS8, no encryption)
    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open(PRIVATE_PATH, "wb") as f:
        f.write(priv_pem)
    print(f"Wrote {PRIVATE_PATH}")

    # generate public key
    public_key = private_key.public_key()
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(PUBLIC_PATH, "wb") as f:
        f.write(pub_pem)
    print(f"Wrote {PUBLIC_PATH}")

if __name__ == "__main__":
    main()
