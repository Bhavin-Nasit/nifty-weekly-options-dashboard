from kiteconnect import KiteTicker
from src.config import KITE_API_KEY
from src.token_store import get_access_token_from_store

live_ticks = {}


def start_websocket(tokens):
    access_token = get_access_token_from_store()

    kws = KiteTicker(KITE_API_KEY, access_token)

    def on_ticks(ws, ticks):
        for t in ticks:
            live_ticks[t['instrument_token']] = t

    def on_connect(ws, response):
        ws.subscribe(tokens)
        ws.set_mode(ws.MODE_FULL, tokens)

    kws.on_ticks = on_ticks
    kws.on_connect = on_connect

    kws.connect(threaded=True)

    return live_ticks
