import asyncio
import time
import os
from pyrogram import Client, filters
from pyrogram.types import Message

# Heroku के Config Vars (Env Vars) से पढ़ें
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
STRING_SESSION = os.getenv("STRING_SESSION", "")

# अगर SESSION_PREFIX (session:) नहीं है, तो जोड़ दें
if STRING_SESSION and not STRING_SESSION.startswith("session:"):
    STRING_SESSION = f"session:{STRING_SESSION}"

# Bot का Client initialize (session_string=STRING_SESSION)
app = Client(
    name="SecureBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

# सिर्फ OWNER_ID वाले यूज़र के लिए कमांड्स
def cmd(command):
    return filters.command(command, prefixes=["."]) & filters.user(OWNER_ID)

# ------------------ Commands ------------------

@app.on_message(cmd("start"))
async def start_cmd(client, message):
    await message.reply("✅ बॉट चालू है!\n\nटाइप करें `.help` पूरी जानकारी के लिए।")

@app.on_message(cmd("help"))
async def help_cmd(client, message):
    await message.reply(
        "**बॉट कमांड्स:**\n"
        "`.start` - बॉट को शुरू करें\n"
        "`.help` - यह मेसेज देखें\n"
        "`.ping` - बॉट की गति जांचें\n"
        "`.approve <limit>` - Pending join requests को approve करें\n"
        "`.decline <limit>` - Pending join requests को decline करें\n"
        "`.status` - समूह में कितने pending requests हैं"
    )

@app.on_message(cmd("ping"))
async def ping_cmd(client, message):
    start_time = time.time()
    reply = await message.reply("पिंग कर रहे हैं...")
    end_time = time.time()
    await reply.edit(f"🏓 Pong! `{round((end_time - start_time) * 1000)} ms`")

@app.on_message(cmd("approve"))
async def approve_requests(client: Client, message: Message):
    try:
        limit = int(message.command[1]) if len(message.command) > 1 else 100
        count = 0
        skipped = 0

        async for req in client.get_chat_join_requests(message.chat.id):
            if count >= limit:
                break
            try:
                await client.approve_chat_join_request(message.chat.id, req.user.id)
                count += 1
                await asyncio.sleep(0.2)
            except Exception as e:
                skipped += 1
                # Heroku logs में error दिखा दें
                print(f"Skipped user {req.user.id} due to error: {e}")

        await message.reply(f"✅ {count} अनुरोध स्वीकृत!\n⛔ {skipped} स्किप किए गए।")
    except Exception as e:
        await message.reply(f"⚠️ त्रुटि: {str(e)}")

@app.on_message(cmd("decline"))
async def decline_requests(client: Client, message: Message):
    try:
        limit = int(message.command[1]) if len(message.command) > 1 else 100
        count = 0
        skipped = 0

        async for req in client.get_chat_join_requests(message.chat.id):
            if count >= limit:
                break
            try:
                await client.decline_chat_join_request(message.chat.id, req.user.id)
                count += 1
                await asyncio.sleep(0.2)
            except Exception as e:
                skipped += 1
                print(f"Skipped user {req.user.id} due to error: {e}")

        await message.reply(f"❌ {count} अनुरोध अस्वीकृत!\n⛔ {skipped} स्किप किए गए।")
    except Exception as e:
        await message.reply(f"⚠️ त्रुटि: {str(e)}")

@app.on_message(cmd("status"))
async def status_requests(client: Client, message: Message):
    try:
        pending = []
        async for req in client.get_chat_join_requests(message.chat.id):
            pending.append(req.user.id)
        await message.reply(f"ℹ️ Pending Join Requests: `{len(pending)}`")
    except Exception as e:
        await message.reply(f"⚠️ त्रुटि: {str(e)}")

# ------------------ Bot Run ------------------

if __name__ == "__main__":
    print("✅ बॉट शुरू हो रहा है...")
    app.run()
