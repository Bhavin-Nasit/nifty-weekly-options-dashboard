import os
from dotenv import load_dotenv

load_dotenv()

KITE_API_KEY = os.getenv("KITE_API_KEY", "")
KITE_API_SECRET = os.getenv("KITE_API_SECRET", "")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

UNDERLYING = os.getenv("UNDERLYING", "NIFTY")
STRIKE_RANGE = int(os.getenv("STRIKE_RANGE", "10"))
OI_ALERT_THRESHOLD = int(os.getenv("OI_ALERT_THRESHOLD", "50000"))
REFRESH_SECONDS = int(os.getenv("REFRESH_SECONDS", "60"))
DANGER_DISTANCE_POINTS = int(os.getenv("DANGER_DISTANCE_POINTS", "100"))
MIN_VOLUME_FOR_SIGNAL = int(os.getenv("MIN_VOLUME_FOR_SIGNAL", "1000"))

NIFTY_SPOT_SYMBOL = "NSE:NIFTY 50"
