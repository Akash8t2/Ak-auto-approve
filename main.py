import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, RPCError
from config import Config

app = Client(
    name="SecureBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.SESSION_STRING
)

def cmd(command):
    return filters.command(command, prefixes=["."]) & filters.user(Config.OWNER_ID)

# -------------------- Basic Commands --------------------
@app.on_message(cmd("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply(
        "🤖 **बॉट सक्रिय है!**\n\n"
        "📍 **उपयोग:**\n"
        "- `.approve` : स्वीकार अनुरोध\n"
        "- `.decline` : अस्वीकार अनुरोध\n"
        "- `.help` : सभी कमांड्स देखें"
    )

@app.on_message(cmd("help"))
async def help_cmd(client: Client, message: Message):
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
async def ping_cmd(client: Client, message: Message):
    start = time.time()
    reply = await message.reply("🏓 पिंग...")
    delta = (time.time() - start) * 1000
    await reply.edit(f"🏓 पोंग! `{delta:.2f}ms`")

# -------------------- Core Logic --------------------
async def handle_requests(message: Message, action: str):
    try:
        limit = int(message.command[1]) if len(message.command) > 1 else Config.DEFAULT_LIMIT
        count = 0
        
        async for request in app.get_chat_join_requests(message.chat.id):
            for attempt in range(Config.MAX_RETRIES):
                try:
                    if count >= limit:
                        return await message.reply(f"♻️ {count} अनुरोध {action} किए!")
                    
                    if action == "approve":
                        await app.approve_chat_join_request(message.chat.id, request.user.id)
                    elif action == "decline":
                        await app.decline_chat_join_request(message.chat.id, request.user.id)
                    
                    count += 1
                    await asyncio.sleep(Config.SLEEP_TIME)
                    break
                
                except FloodWait as e:
                    await asyncio.sleep(e.value + 2)
                except RPCError as e:
                    if attempt < Config.MAX_RETRIES - 1:
                        await asyncio.sleep(2)
                    else:
                        raise e

        action_emoji = "✅" if action == "approve" else "❌"
        await message.reply(f"{action_emoji} {count} अनुरोध सफलतापूर्वक {action}!")

    except Exception as e:
        await message.reply(f"⚠️ त्रुटि:\n`{str(e)}`")

@app.on_message(cmd("approve"))
async def approve_requests(client: Client, message: Message):
    await handle_requests(message, "approve")

@app.on_message(cmd("decline"))
async def decline_requests(client: Client, message: Message):
    await handle_requests(message, "decline")

@app.on_message(cmd("status"))
async def status_requests(client: Client, message: Message):
    try:
        count = sum(1 async for _ in app.get_chat_join_requests(message.chat.id))
        await message.reply(f"📊 **लंबित अनुरोध:** `{count}`")
    except Exception as e:
        await message.reply(f"⚠️ त्रुटि:\n`{str(e)}`")

# -------------------- Startup --------------------
async def main():
    await app.start()
    print("✅ बॉट सफलतापूर्वक शुरू हुआ!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
