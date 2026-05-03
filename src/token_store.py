import os
from pathlib import Path

TOKEN_FILE = Path(os.getenv("KITE_TOKEN_FILE", "data/kite_access_token.txt"))


def get_access_token_from_store():
    env_token = os.getenv("KITE_ACCESS_TOKEN", "").strip()
    if env_token:
        return env_token

    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text(encoding="utf-8").strip()

    return ""


def save_access_token(token: str):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(token.strip(), encoding="utf-8")
