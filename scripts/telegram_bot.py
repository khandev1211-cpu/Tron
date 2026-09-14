import os
import telebot
from telebot import types
import redis
import json
from dotenv import load_dotenv

load_dotenv()

# Config
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("TELEGRAM_CHAT_ID") # Using this as whitelist
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

bot = telebot.TeleBot(TOKEN)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, protocol=2)

def send_alert(message, pattern):
    """Sends Alert with Markdown and 'Vanity It!' Button"""
    markup = types.InlineKeyboardMarkup()
    # Callback data carries the pattern to be mined
    vanity_btn = types.InlineKeyboardButton("🛠️ Vanity It! (Start GPU)", callback_data=f"mine:{pattern}")
    markup.add(vanity_btn)

    try:
        bot.send_message(ADMIN_ID, f"🚨 *SENTINEL MATCH DETECTED*\n\n{message}",
                         parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        print(f"Telegram Alert Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('mine:'))
def handle_vanity_request(call):
    # Security: Strict User Validation
    if str(call.from_user.id) != str(ADMIN_ID):
        bot.answer_callback_query(call.id, "❌ Unauthorized! Security violation logged.")
        return

    pattern = call.data.replace("mine:", "")

    # Push to FIFO Queue in Redis
    task = {"pattern": pattern, "chat_id": call.message.chat.id}
    r.lpush("gpu_queue", json.dumps(task))

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"{call.message.text}\n\n⏳ *GPU TASK QUEUED:* {pattern}",
                          parse_mode="Markdown")
    bot.answer_callback_query(call.id, "🚀 Mining Task added to RTX 4090 Queue!")

def run_bot():
    print("[+] Sentinel Telegram Agent Active...")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    run_bot()
