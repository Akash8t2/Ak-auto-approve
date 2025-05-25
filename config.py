import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API
    API_ID = int(os.environ.get("API_ID", ))
    API_HASH = os.environ.get("API_HASH", "")
    SESSION_STRING = os.environ.get("SESSION_STRING", "")
    
    # Owner
    OWNER_ID = int(os.environ.get("OWNER_ID", ))
    
    # Other settings
    SLEEP_TIME = 1.5  # Anti-flood
