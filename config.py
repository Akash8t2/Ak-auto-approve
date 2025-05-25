import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API
    API_ID = int(os.environ.get("API_ID", 26785208))
    API_HASH = os.environ.get("API_HASH", "0ddf86040a271eaa552c3fe159d1e541")
    SESSION_STRING = os.environ.get("SESSION_STRING", "")
    
    # Owner
    OWNER_ID = int(os.environ.get("OWNER_ID", 5397621246))
    
    # Settings
    SLEEP_TIME = 1.5  # Anti-flood delay
    DEFAULT_LIMIT = 100  # Default request limit
