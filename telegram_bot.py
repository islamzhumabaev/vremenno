import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Загрузка переменных окружения
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = (
    "You are a helpful assistant who answers questions about knowledge. "
    "You will receive questions about education, such as “What is physics? What does it study?” "
    "and other questions about education. You need to give clear, understandable, and detailed answers."
)

import json

def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Получаем JSON как строку из переменной окружения
    google_creds_json = os.getenv("GOOGLE_CREDENTIALS")
    
    if not google_creds_json:
        raise ValueError("Переменная окружения GOOGLE_CREDENTIALS не найдена")
    
    # Преобразуем строку JSON в словарь
    creds_dict = json.loads(google_creds_json)

    # Авторизуемся без использования файла
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet


# Обработка сообщений
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

    # Лог в Google Sheets
    sheet = connect_to_sheet()
    sheet.append_row([timestamp, str(user_id), username, user_message, bot_reply])

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
