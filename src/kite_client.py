from kiteconnect import KiteConnect

from src.config import KITE_API_KEY
from src.token_store import get_access_token_from_store


def get_kite() -> KiteConnect:
    token = get_access_token_from_store()
    if not KITE_API_KEY:
        raise RuntimeError("KITE_API_KEY is missing. Add it in Render environment variables.")
    if not token:
        raise RuntimeError("Kite access token is missing. Generate today's token and save it from the dashboard or update_token.py.")

    kite = KiteConnect(api_key=KITE_API_KEY)
    kite.set_access_token(token)
    return kite
