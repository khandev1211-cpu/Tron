import os
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def _send_alert_async(message, pattern):
    if not TOKEN or not CHAT_ID or "your_token" in TOKEN: return
    bot = Bot(token=TOKEN)
    keyboard = [[InlineKeyboardButton("🚀 Generate Vanity", callback_data=f"gen_{pattern}"),
                  InlineKeyboardButton("❌ Ignore", callback_data="ignore")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=f"🚨 *USDT MATCH DETECTED* 🚨\n\n{message}",
                               parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e: print(f"[Telegram] Alert Error: {e}")

def send_alert(message, pattern):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_send_alert_async(message, pattern))
        loop.close()
    except Exception as e: print(f"[Telegram] Alert Sync Error: {e}")

async def _send_report_async(message):
    if not TOKEN or not CHAT_ID or "your_token" in TOKEN: return
    bot = Bot(token=TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=f"🤖 *AGENT SYSTEM REPORT* 🤖\n\n{message}", parse_mode='Markdown')
    except Exception as e: print(f"[Telegram] Report Error: {e}")

def send_system_report(message):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_send_report_async(message))
        loop.close()
    except Exception as e: print(f"[Telegram] Report Sync Error: {e}")
