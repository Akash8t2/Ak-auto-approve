import os
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
OWNER_ID = int(os.environ["OWNER_ID"])
SLEEP_TIME = 1.5  # Anti-Flood delay

# Initialize Client
app = Client(
    name="SecureBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# Command filter
def cmd(command):
    return filters.command(command, prefixes=["."]) & filters.user(OWNER_ID)

# -------------------- Commands --------------------
@app.on_message(cmd("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply(
        "✅ बॉट चालू है!\n\n"
        "उपलब्ध कमांड्स:\n"
        ".help - सभी कमांड्स दिखाएं\n"
        ".ping - बॉट की गति जांचें"
    )

@app.on_message(cmd("help"))
async def help_cmd(client: Client, message: Message):
    help_text = (
        "**बॉट कमांड्स:**\n"
        "`.approve [limit]` - स्वीकृत करें अनुरोध\n"
        "`.decline [limit]` - अस्वीकृत करें अनुरोध\n"
        "`.status` - लंबित अनुरोधों की संख्या\n"
        "`.ping` - बॉट की गति जांचें"
    )
    await message.reply(help_text)

@app.on_message(cmd("ping"))
async def ping_cmd(client: Client, message: Message):
    start = time.time()
    reply = await message.reply("🏓 पिंग...")
    delta = (time.time() - start) * 1000
    await reply.edit(f"🏓 पोंग! `{delta:.2f}ms`")

# ----------- Join Request Management -----------
async def handle_requests(client: Client, message: Message, action: str):
    try:
        limit = int(message.command[1]) if len(message.command) > 1 else 100
        count = 0
        
        async for request in client.get_chat_join_requests(message.chat.id):
            if count >= limit:
                break
                
            try:
                if action == "approve":
                    await client.approve_chat_join_request(
                        chat_id=message.chat.id,
                        user_id=request.user.id
                    )
                elif action == "decline":
                    await client.decline_chat_join_request(
                        chat_id=message.chat.id,
                        user_id=request.user.id
                    )
                
                count += 1
                await asyncio.sleep(SLEEP_TIME)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                await message.reply(f"त्रुटि: {str(e)}")
                continue
        
        action_text = "स्वीकृत" if action == "approve" else "अस्वीकृत"
        await message.reply(f"✅ {count} अनुरोध {action_text}!")

    except Exception as e:
        await message.reply(f"⚠️ गंभीर त्रुटि: {str(e)}")

@app.on_message(cmd("approve"))
async def approve_requests(client: Client, message: Message):
    await handle_requests(client, message, "approve")

@app.on_message(cmd("decline"))
async def decline_requests(client: Client, message: Message):
    await handle_requests(client, message, "decline")

@app.on_message(cmd("status"))
async def status_requests(client: Client, message: Message):
    try:
        count = 0
        async for _ in client.get_chat_join_requests(message.chat.id):
            count += 1
        await message.reply(f"ℹ️ लंबित अनुरोध: {count}")
    except Exception as e:
        await message.reply(f"⚠️ त्रुटि: {str(e)}")

# -------------------- Main --------------------
async def main():
    await app.start()
    print("✅ बॉट सफलतापूर्वक शुरू हुआ!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
