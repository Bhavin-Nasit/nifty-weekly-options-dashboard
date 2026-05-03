import time

previous_snapshot = {}
last_update_time = None


def update_snapshot(live_ticks):
    global previous_snapshot, last_update_time

    current_snapshot = {}

    for token, tick in live_ticks.items():
        current_snapshot[int(token)] = {
            "oi": int(tick.get("oi") or 0),
            "ltp": float(tick.get("last_price") or 0),
            "volume": int(tick.get("volume") or 0),
        }

    if not current_snapshot:
        return None

    if not previous_snapshot:
        previous_snapshot = current_snapshot
        last_update_time = time.time()
        return None

    delta = {}
    for token, curr in current_snapshot.items():
        prev = previous_snapshot.get(token, {"oi": curr["oi"], "ltp": curr["ltp"], "volume": curr["volume"]})
        delta[token] = {
            "oi": curr["oi"],
            "ltp": curr["ltp"],
            "volume": curr["volume"],
            "oi_change": curr["oi"] - prev.get("oi", 0),
            "ltp_change": curr["ltp"] - prev.get("ltp", 0),
            "volume_change": curr["volume"] - prev.get("volume", 0),
        }

    previous_snapshot = current_snapshot
    last_update_time = time.time()
    return delta
