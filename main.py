import asyncio
import signal
import time
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError
from config import Config

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Client(
    name="SecureBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.SESSION_STRING
)

# Command Filter
def cmd(command):
    return filters.command(command, prefixes=["."]) & filters.user(Config.OWNER_ID)

# -------------------- Basic Commands --------------------
@app.on_message(cmd("start"))
async def start_cmd(_, message: Message):
    await message.reply(
        "🤖 **बॉट सक्रिय है!**\n\n"
        "📍 **उपयोग:**\n"
        "- `.approve` : स्वीकार अनुरोध\n"
        "- `.decline` : अस्वीकार अनुरोध\n"
        "- `.help` : सभी कमांड्स देखें"
    )

@app.on_message(cmd("help"))
async def help_cmd(_, message: Message):
    help_text = (
        "📜 **सभी कमांड्स:**\n\n"
        "`.approve [संख्या]` - अनुरोध स्वीकारें\n"
        "`.decline [संख्या]` - अनुरोध अस्वीकारें\n"
        "`.status` - लंबित अनुरोध गिनती\n"
        "`.ping` - बॉट की गति जांचें\n"
        "`.help` - यह सहायता संदेश"
    )
    await message.reply(help_text)

@app.on_message(cmd("ping"))
async def ping_cmd(_, message: Message):
    start = time.time()
    reply = await message.reply("🏓 पिंग...")
    delta = (time.time() - start) * 1000
    await reply.edit(f"🏓 पोंग! `{delta:.2f}ms`")

# -------------------- Core Logic --------------------
async def handle_request(chat_id: int, user_id: int, action: str):
    for attempt in range(Config.MAX_RETRIES):
        try:
            if action == "approve":
                await app.approve_chat_join_request(chat_id, user_id)
            elif action == "decline":
                await app.decline_chat_join_request(chat_id, user_id)
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value + 2)
        except RPCError as e:
            logger.error(f"Attempt {attempt+1} failed: {str(e)}")
            await asyncio.sleep(2)
    return False

async def process_requests(message: Message, action: str):
    try:
        limit = int(message.command[1]) if len(message.command) > 1 else Config.DEFAULT_LIMIT
        count = success = 0
        
        async for request in app.get_chat_join_requests(message.chat.id):
            if count >= limit:
                break
                
            if await handle_request(message.chat.id, request.user.id, action):
                success += 1
                
            count += 1
            await asyncio.sleep(Config.SLEEP_TIME)

        action_text = "स्वीकृत" if action == "approve" else "अस्वीकृत"
        await message.reply(f"✅ {success}/{count} अनुरोध {action_text}!")

    except Exception as e:
        await message.reply(f"⚠️ त्रुटि:\n`{str(e)}`")
        logger.exception("Processing Error")

@app.on_message(cmd("approve"))
async def approve_requests(_, message: Message):
    await process_requests(message, "approve")

@app.on_message(cmd("decline"))
async def decline_requests(_, message: Message):
    await process_requests(message, "decline")

@app.on_message(cmd("status"))
async def status_requests(_, message: Message):
    try:
        count = sum(1 async for _ in app.get_chat_join_requests(message.chat.id))
        await message.reply(f"📊 **लंबित अनुरोध:** `{count}`")
    except Exception as e:
        await message.reply(f"⚠️ त्रुटि:\n`{str(e)}`")

# -------------------- Shutdown Handler --------------------
async def shutdown(signal, loop):
    logger.info("⚠️ शटडाउन सिग्नल प्राप्त हुआ...")
    await app.stop()
    loop.stop()

async def main():
    await app.start()
    logger.info("✅ बॉट सफलतापूर्वक शुरू हुआ!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    
    # Signal Handlers
    for sig in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(
            sig, 
            lambda: asyncio.create_task(shutdown(sig, loop))
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
        logger.info("✅ बॉट सुरक्षित रूप से बंद हुआ")
