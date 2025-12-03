#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
import requests
from typing import Optional

API_TIMEOUT = 20

def load_public_key_as_single_line(pem_path: str) -> str:
    """
    Return the PEM text unchanged (preserve real newlines).
    The API expects a normal PEM string with real newlines inside the JSON value.
    """
    p = Path(pem_path)
    if not p.exists():
        raise FileNotFoundError(f"PEM file not found: {pem_path}")
    # Read file exactly, preserve newlines
    raw = p.read_text(encoding="utf-8")
    return raw


def request_seed(student_id: str, github_repo_url: str, api_url: str,
                 public_pem_path: str = "student_public.pem",
                 out_path: str = "encrypted_seed.txt",
                 timeout: Optional[int] = API_TIMEOUT) -> str:
    public_key_single = load_public_key_as_single_line(public_pem_path)

    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_single
    }

    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        raise RuntimeError(f"Network/requests error while contacting API: {e}") from e

    try:
        data = resp.json()
    except ValueError:
        raise RuntimeError(f"API returned non-JSON response (status {resp.status_code}): {resp.text}")

    if resp.status_code != 200 or data.get("status") != "success":
        raise RuntimeError(f"API error: status_code={resp.status_code}, body={json.dumps(data, indent=2)}")

    encrypted_seed = data.get("encrypted_seed")
    if not encrypted_seed:
        raise RuntimeError(f"No 'encrypted_seed' in API response: {json.dumps(data, indent=2)}")

    Path(out_path).write_text(encrypted_seed, encoding="utf-8")
    print(f"Wrote encrypted seed to {out_path} (DO NOT commit this file).")
    return encrypted_seed

def main():
    parser = argparse.ArgumentParser(description="Request encrypted seed from instructor API")
    parser.add_argument("--student-id", required=True, help="Your student id (exact)")
    parser.add_argument("--repo", required=True, help="Exact GitHub repo URL you will submit")
    parser.add_argument("--api", default="https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws",
                        help="Instructor API URL")
    parser.add_argument("--public", default="student_public.pem", help="Path to student_public.pem")
    parser.add_argument("--out", default="encrypted_seed.txt", help="Output file (do NOT commit)")
    args = parser.parse_args()

    enc = request_seed(args.student_id, args.repo, args.api, public_pem_path=args.public, out_path=args.out)
    print("Encrypted seed saved. First 80 chars:", enc[:80])

if __name__ == "__main__":
    main()
