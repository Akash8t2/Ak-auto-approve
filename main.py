import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, OWNER_ID, STRING_SESSION

app = Client(name="SecureBot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

def cmd(command):
    return filters.command(command, prefixes=["."]) & filters.user(OWNER_ID)

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
    start = time.time()
    reply = await message.reply("पिंग कर रहे हैं...")
    end = time.time()
    await reply.edit(f"🏓 Pong! `{round((end - start) * 1000)} ms`")

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
                await asyncio.sleep(0.3)
            except Exception as e:
                skipped += 1
                print(f"Skipped user {req.user.id} due to error: {e}")
                continue

        await message.reply(f"✅ {count} अनुरोध स्वीकृत!\n⛔ {skipped} स्किप किए गए (त्रुटि के कारण)।")
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
                await asyncio.sleep(0.3)
            except Exception as e:
                skipped += 1
                print(f"Skipped user {req.user.id} due to error: {e}")
                continue

        await message.reply(f"❌ {count} अनुरोध अस्वीकृत!\n⛔ {skipped} स्किप किए गए (त्रुटि के कारण)।")
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

print("✅ बॉट शुरू हो रहा है...")
app.run()
