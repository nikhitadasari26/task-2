# submit_final.py
import json, requests, subprocess, sys
from pathlib import Path

API = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"
STUDENT_ID = "23P31A0514"

root = Path('.').resolve()

def read_text(path):
    return Path(path).read_text(encoding='utf-8')

# 1) gather values
try:
    repo = subprocess.run(["git","remote","get-url","origin"], capture_output=True, text=True, check=True).stdout.strip()
except Exception as e:
    print("Failed to read git remote URL:", e)
    sys.exit(1)

try:
    commit = subprocess.run(["git","rev-parse","--verify","HEAD"], capture_output=True, text=True, check=True).stdout.strip()
except Exception as e:
    print("Failed to read commit hash:", e)
    sys.exit(1)

encsig = read_text("encrypted_commit_signature.txt").strip()
enc_seed = read_text("encrypted_seed.txt").strip()
student_pub = read_text("student_public.pem")   # keep real newlines here

payload = {
    "github_repo_url": repo,
    "repository_url": repo,
    "commit_hash": commit,
    "encrypted_signature": encsig,
    "encrypted_seed": enc_seed,
    "student_id": STUDENT_ID,
    "public_key": student_pub,
    "student_public_key": student_pub
}

# write payload to file for inspection
with open("body_final.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, separators=(',', ':'), ensure_ascii=False)

print("Posting body_final.json to instructor API...")
try:
    # verify=False because Windows Schannel had revocation-check problems earlier
    r = requests.post(API, json=payload, verify=False, timeout=30)
    print("Status:", r.status_code)
    print(r.text)
except Exception as e:
    print("Request failed:", e)
    sys.exit(1)
