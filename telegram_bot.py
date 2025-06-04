import os
import csv
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# Загружаем переменные окружения
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
CSV_FILE = 'chat_logs.csv'

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = (
    "You are a helpful assistant who answers questions about knowledge. "
    "You will receive questions about education, such as “What is physics? What does it study?” "
    "and other questions about education. You need to give clear, understandable, and detailed answers."
)

# Инициализация CSV при первом запуске
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'user_id', 'username', 'user_message', 'bot_response'])

# Обработка входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "anonymous"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nПользователь: {user_message}")
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"Произошла ошибка: {e}"

    await update.message.reply_text(bot_reply)

    with open(CSV_FILE, mode='a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, user_id, username, user_message, bot_reply])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am a bot that answers your questions about education. Just write your question, and I will try to answer it as clearly as possible. 🎓"
    )

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
