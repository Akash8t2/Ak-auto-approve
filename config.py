import os
from dotenv import load_dotenv

load_dotenv()  # .env से वैरिएबल लोड करता है

class Config:
    # Telegram API
    API_ID = int(os.environ.get("API_ID", 26785208))
    API_HASH = os.environ.get("API_HASH", "0ddf86040a271eaa552c3fe159d1e541")
    SESSION_STRING = os.environ.get("SESSION_STRING", "")

    # Bot Owner
    OWNER_ID = int(os.environ.get("OWNER_ID", 5397621246))

    # Settings
    SLEEP_TIME = float(os.environ.get("SLEEP_TIME", "1.5"))
    MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
    DEFAULT_LIMIT = int(os.environ.get("DEFAULT_LIMIT", "100"))
