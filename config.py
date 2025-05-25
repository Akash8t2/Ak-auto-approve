import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API Credentials
    API_ID = int(os.environ.get("API_ID", 26785208))
    API_HASH = os.environ.get("API_HASH", "0ddf86040a271eaa552c3fe159d1e541")
    SESSION_STRING = os.environ.get("SESSION_STRING", "")
    
    # Bot Owner
    OWNER_ID = int(os.environ.get("OWNER_ID", 5397621246))
    
    # Settings
    SLEEP_TIME = 1.5  # Anti-Flood Delay
    DEFAULT_LIMIT = 100
    MAX_RETRIES = 3
