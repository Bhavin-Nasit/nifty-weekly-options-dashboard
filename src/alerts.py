import requests
from src.config import DISCORD_WEBHOOK_URL

_last_alerts = set()


def send_discord_alert(message: str, key: str | None = None):
    if not DISCORD_WEBHOOK_URL:
        return

    alert_key = key or message
    if alert_key in _last_alerts:
        return

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=8)
        if response.status_code < 300:
            _last_alerts.add(alert_key)
    except Exception:
        pass
