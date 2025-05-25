import asyncio
import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

app = Client(
    name="SecureBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.SESSION_STRING
)

def cmd(command):
    return filters.command(command, prefixes=["."]) & filters.user(Config.OWNER_ID)

# -------------------- Commands --------------------
@app.on_message(cmd("start"))
async def start_cmd(client, message):
    await message.reply("✅ बॉट चालू है!\n\nटाइप करें `.help` पूरी जानकारी के लिए।")

@app.on_message(cmd("help"))
async def help_cmd(client, message):
    help_text = (
        "**बॉट कमांड्स:**\n"
        "`.start` - बॉट को शुरू करें\n"
        "`.help` - यह मेसेज देखें\n"
        "`.ping` - बॉट की गति जांचें\n"
        "`.approve <limit>` - Pending join requests को approve करें\n"
        "`.decline <limit>` - Pending join requests को decline करें\n"
        "`.status` - समूह में कितने pending requests हैं"
    )
    await message.reply(help_text)

@app.on_message(cmd("ping"))
async def ping_cmd(client, message):
    start = time.time()
    reply = await message.reply("पिंग कर रहे हैं...")
    end = time.time()
    await reply.edit(f"🏓 Pong! `{round((end - start) * 1000)} ms`")

# ----------- Join Request Management -----------
async def handle_requests(client, message, action_type):
    try:
        limit = int(message.command[1]) if len(message.command) > 1 else Config.DEFAULT_LIMIT
        count = 0
        
        async for req in client.get_chat_join_requests(message.chat.id):
            if count >= limit:
                break
                
            if action_type == "approve":
                await client.approve_chat_join_request(message.chat.id, req.user.id)
            elif action_type == "decline":
                await client.decline_chat_join_request(message.chat.id, req.user.id)
                
            count += 1
            await asyncio.sleep(Config.SLEEP_TIME)
            
        action_emoji = "✅" if action_type == "approve" else "❌"
        action_text = "स्वीकृत" if action_type == "approve" else "अस्वीकृत"
        await message.reply(f"{action_emoji} {count} अनुरोध {action_text}!")
        
    except Exception as e:
        await message.reply(f"⚠️ त्रुटि: {str(e)}")

@app.on_message(cmd("approve"))
async def approve_requests(client: Client, message: Message):
    await handle_requests(client, message, "approve")

@app.on_message(cmd("decline"))
async def decline_requests(client: Client, message: Message):
    await handle_requests(client, message, "decline")

@app.on_message(cmd("status"))
async def status_requests(client: Client, message: Message):
    try:
        pending = []
        async for req in client.get_chat_join_requests(message.chat.id):
            pending.append(req.user.id)
        await message.reply(f"ℹ️ Pending Join Requests: `{len(pending)}`")
    except Exception as e:
        await message.reply(f"⚠️ त्रुटि: {str(e)}")

if __name__ == "__main__":
    print("✅ बॉट शुरू हो रहा है...")
    app.run()
