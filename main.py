import asyncio  
import signal  
import time  
import logging  
from pyrogram import Client, filters  
from pyrogram.types import Message  
from pyrogram.errors import FloodWait, RPCError  
from config import Config  
  
# -------------------- Logging Setup --------------------  
logging.basicConfig(  
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  
    datefmt="%d-%b-%y %H:%M:%S"  
)  
logger = logging.getLogger(__name__)  
  
# -------------------- Client Initialization --------------------  
app = Client(  
    name="SecureBot",  
    api_id=Config.API_ID,  
    api_hash=Config.API_HASH,  
    session_string=Config.SESSION_STRING  
)  
  
# -------------------- Command Filter --------------------  
def cmd(command):  
    return filters.command(command, prefixes=["."]) & filters.user(Config.OWNER_ID)  
  
# -------------------- Basic Commands --------------------  
@app.on_message(cmd("start"))  
async def start_cmd(_, message: Message):  
    await message.reply(  
        "🤖 **बॉट सक्रिय है!**\n\n"  
        "📍 **मुख्य कमांड्स:**\n"  
        "• `.approve` - स्वीकार अनुरोध\n"  
        "• `.decline` - अस्वीकार अनुरोध\n"  
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
            wait_time = e.value + 2  
            logger.warning(f"FloodWait: {wait_time} सेकेंड इंतजार कर रहे हैं...")  
            await asyncio.sleep(wait_time)  
        except RPCError as e:  
            logger.error(f"कोशिश {attempt+1}/{Config.MAX_RETRIES} विफल: {str(e)}")  
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
  
        action_emoji = "✅" if action == "approve" else "❌"  
        action_text = "स्वीकृत" if action == "approve" else "अस्वीकृत"  
        await message.reply(f"{action_emoji} सफल: {success}/{count} अनुरोध {action_text}!")  
  
    except Exception as e:  
        error_msg = f"⚠️ गंभीर त्रुटि:\n`{str(e)}`"  
        await message.reply(error_msg)  
        logger.exception(error_msg)  
  
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
        await message.reply(f"📊 लंबित अनुरोध: {count}")  
    except Exception as e:  
        error_msg = f"⚠️ स्टेटस चेक विफल:\n`{str(e)}`"  
        await message.reply(error_msg)  
        logger.exception(error_msg)  
  
# -------------------- Shutdown Handler --------------------  
async def graceful_shutdown(sig, loop):  
    logger.info(f"🚨 सिग्नल प्राप्त: {sig.name} | बॉट बंद हो रहा है...")  
    await app.stop()  
      
    # सभी लंबित टास्क्स को कैंसल करें  
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]  
    [task.cancel() for task in tasks]  
      
    await asyncio.gather(*tasks, return_exceptions=True)  
    loop.stop()  
  
# -------------------- Main Function --------------------  
async def main():  
    await app.start()  
    logger.info("🚀 बॉट सफलतापूर्वक शुरू हुआ!")  
    await asyncio.Event().wait()  # अनिश्चित काल तक चलता रहे  
  
# -------------------- Entry Point --------------------  
if __name__ == "__main__":  
    loop = asyncio.new_event_loop()  
    asyncio.set_event_loop(loop)  
      
    # सिग्नल हैंडलर सेटअप (Fixed Version)  
    signals = (signal.SIGTERM, signal.SIGINT)  
    for sig in signals:  
        loop.add_signal_handler(  # <-- यहाँ सुधार हुआ  
            sig,  
            lambda sig=sig: asyncio.create_task(graceful_shutdown(sig, loop))  
        )  # Closing parenthesis जोड़ें  
      
    try:  
        loop.run_until_complete(main())  
    except KeyboardInterrupt:  
        pass  
    finally:  
        if not loop.is_closed():  
            loop.close()  
        logger.info("🎉 बॉट सुरक्षित रूप से बंद हुआ")
