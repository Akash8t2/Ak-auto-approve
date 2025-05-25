import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))
STRING_SESSION = os.getenv("STRING_SESSION")

# Optional fix in case session prefix is missing
if not STRING_SESSION.startswith("session:"):
    STRING_SESSION = f"session:{STRING_SESSION}"
