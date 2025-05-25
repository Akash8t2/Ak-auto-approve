import asyncio
import signal
import time
import logging
import os

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError

# -------------------- Config Class --------------------
# सुनिश्चित करें कि आपकी config.py में निम्नलिखित वैरिएबल्स सेट हैं:
#
# class Config:
#     API_ID = int(os.getenv("API_ID", "0"))
#     API_HASH = os.getenv("API_HASH", "")
#     SESSION_STRING = os.getenv("SESSION_STRING", "")     # 반드시 "session:..." 형식
#     OWNER_ID = int(os.getenv("OWNER_ID", "0"))
#     MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
#     SLEEP_TIME = float(os.getenv("SLEEP_TIME", "0.5"))
#     DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", "100"))

from config import Config

# -------------------- Logging Setup --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S"
)
logger = logging.getLogger(__name__)

# -------------------- Validate Session String --------------------
if not Config.SESSION_STRING:
    logger.error("⚠️ SESSION_STRING खाली है! कृपया config.py या Heroku Config Vars में सही सेट करें।")
    exit(1)

# अगर SESSION_PREFIX ("session:") नहीं है, तो जोड़ दें
session_str = Config.SESSION_STRING
if not session_str.startswith("session:"):
    session_str = f"session:{session_str}"

# -------------------- Client Initialization --------------------
app = Client(
    name="SecureBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=session_str
)

# -------------------- Command Filter --------------------
def cmd(command):
    return filters.command(command, prefixes=["."]) & filters.user(Config.OWNER_ID)

# -------------------- Debug Logger for Incoming Messages --------------------
@app.on_message(filters.incoming)
async def log_messages(_, message: Message):
    text = message.text or "<non-text message>"
    logger.info(f"नया मैसेज from {message.from_user.id if message.from_user else 'unknown'}: {text}")

# -------------------- Basic Commands --------------------
@app.on_message(cmd("start"))
async def start_cmd(_, message: Message):
    await message.reply(
        "🤖 **बॉट सक्रिय है!**\n\n"
        "📍 **मुख्य कमांड्स:**\n"
        "• `.approve [संख्या]` - अनुरोध स्वीकारें\n"
        "• `.decline [संख्या]` - अनुरोध अस्वीकारें\n"
        "• `.status` - लंबित अनुरोध गिनती\n"
        "• `.ping` - बॉट की गति जांचें\n"
        "• `.help` - सभी कमांड्स देखें"
    )

@app.on_message(cmd("help"))
async def help_cmd(_, message: Message):
    help_text = (
        "📜 **सभी कमांड्स:**\n\n"
        "• `.approve [संख्या]` - अनुरोध स्वीकारें\n"
        "• `.decline [संख्या]` - अनुरोध अस्वीकारें\n"
        "• `.status` - लंबित अनुरोध गिनती\n"
        "• `.ping` - बॉट की गति जांचें\n"
        "• `.help` - यह सहायता संदेश"
    )
    await message.reply(help_text)

@app.on_message(cmd("ping"))
async def ping_cmd(_, message: Message):
    start_ts = time.time()
    reply = await message.reply("🏓 पिंग...")
    elapsed = (time.time() - start_ts) * 1000
    await reply.edit(f"🏓 पोंग! `{elapsed:.2f}ms`")

# -------------------- Core Logic --------------------
async def handle_request(chat_id: int, user_id: int, action: str) -> bool:
    """
    join request को approve/decline करते समय FloodWait या RPCError को हैंडल करता है।
    return True अगर सफल, False अगर MAX_RETRIES बाद भी फेल हो।
    """
    for attempt in range(1, Config.MAX_RETRIES + 1):
        try:
            if action == "approve":
                await app.approve_chat_join_request(chat_id, user_id)
            else:
                await app.decline_chat_join_request(chat_id, user_id)
            return True
        except FloodWait as e:
            wait_time = e.value + 1
            logger.warning(f"FloodWait: {wait_time} सेकेंड इंतजार कर रहे हैं (यूज़र {user_id})...")
            await asyncio.sleep(wait_time)
        except RPCError as e:
            logger.error(f"कोशिश {attempt}/{Config.MAX_RETRIES} विफल (यूज़र {user_id}): {e}")
            await asyncio.sleep(1)
    return False

async def process_requests(message: Message, action: str):
    """
    एक साथ कई join requests को process करता है (approve या decline)।
    """
    try:
        limit = int(message.command[1]) if len(message.command) > 1 else Config.DEFAULT_LIMIT
    except (IndexError, ValueError):
        limit = Config.DEFAULT_LIMIT

    processed = 0
    success = 0

    async for req in app.get_chat_join_requests(message.chat.id):
        if processed >= limit:
            break

        ok = await handle_request(message.chat.id, req.user.id, action)
        if ok:
            success += 1
        processed += 1

        # अगली कार्रवाई से पहले थोड़ी देर रुकें
        await asyncio.sleep(Config.SLEEP_TIME)

    emoji = "✅" if action == "approve" else "❌"
    text = "स्वीकृत" if action == "approve" else "अस्वीकृत"
    await message.reply(f"{emoji} सफल: {success}/{processed} अनुरोध {text}!")

@app.on_message(cmd("approve"))
async def approve_requests(_, message: Message):
    await process_requests(message, "approve")

@app.on_message(cmd("decline"))
async def decline_requests(_, message: Message):
    await process_requests(message, "decline")

@app.on_message(cmd("status"))
async def status_requests(_, message: Message):
    try:
        count = 0
        async for _ in app.get_chat_join_requests(message.chat.id):
            count += 1
        await message.reply(f"📊 लंबित अनुरोध: {count}")
    except Exception as e:
        logger.exception(f"स्टेटस चेक विफल: {e}")
        await message.reply(f"⚠️ स्टेटस चेक विफल:\n`{e}`")

# -------------------- Graceful Shutdown --------------------
async def graceful_shutdown(sig, loop):
    logger.info(f"🚨 सिग्नल प्राप्त: {sig.name} | बॉट बंद हो रहा है...")
    try:
        await app.stop()
    except Exception as e:
        logger.error(f"स्टॉप करते समय त्रुटि: {e}")

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
    logger.info("🎉 बॉट सुरक्षित रूप से बंद हुआ")

# -------------------- Main Function --------------------
async def main():
    await app.start()
    logger.info("🚀 बॉट सफलतापूर्वक शुरू हुआ और awaiting events...")

    # अनंतकाल तक चलता रहे
    await asyncio.Event().wait()

# -------------------- Entry Point --------------------
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # सिग्नल हैंडलर सेटअप (Linux/Heroku पर काम करेगा)
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(graceful_shutdown(s, loop))
        )

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        if not loop.is_closed():
            loop.close()
