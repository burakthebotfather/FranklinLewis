import asyncio
import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

import gspread
from google.oauth2.service_account import Credentials

# === CONFIG ===
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # <-- Вставь токен
TABLE_ID = "YOUR_GOOGLE_SHEET_ID"      # <-- Вставь TABLE_ID
SERVICE_ACCOUNT_FILE = "credentials.json"  # Файл сервисного аккаунта (не загружать в GitHub!)

ALLOWED_CHATS = [-1002079167705, -1002387655137, -1002423500927, -1002178818697]

logging.basicConfig(level=logging.INFO)

# === GOOGLE SHEETS AUTH ===
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)

# === STATE ===
active_shifts = {}  # {user_id: {"start_time": datetime, "message_id": int, "chat_id": int}}

# === COMMAND: start_shift ===
async def start_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ALLOWED_CHATS:
        return

    user = update.effective_user
    now = datetime.now()
    active_shifts[user.id] = {
        "start_time": now,
        "message_id": None,
        "chat_id": update.effective_chat.id
    }

    keyboard = [[InlineKeyboardButton("Завершить смену", callback_data=f"end_shift:{user.id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = await update.message.reply_text(
        f"🚀 {user.first_name}, смена начата в {now.strftime('%H:%M:%S')}",
        reply_markup=reply_markup
    )
    active_shifts[user.id]["message_id"] = msg.message_id

    # Планируем автозавершение через 3 часа
    context.job_queue.run_once(end_shift_auto, when=3 * 3600, data={"user_id": user.id}, name=str(user.id))

# === CALLBACK: end_shift ===
async def end_shift_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split(":")[1])
    if user_id in active_shifts:
        await finish_shift(user_id, context, manual=True)
        await query.edit_message_text("✅ Смена завершена!")

# === AUTO END SHIFT ===
async def end_shift_auto(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data["user_id"]
    if user_id in active_shifts:
        await finish_shift(user_id, context, manual=False)

# === FINISH SHIFT & WRITE TO GOOGLE SHEETS ===
async def finish_shift(user_id, context, manual=True):
    shift_data = active_shifts.pop(user_id, None)
    if shift_data:
        start_time = shift_data["start_time"]
        end_time = datetime.now()
        duration = str(end_time - start_time).split(".")[0]

        try:
            sheet = client.open_by_key(TABLE_ID).sheet1
            sheet.append_row([
                str(user_id),
                start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
                duration,
                "manual" if manual else "auto"
            ])
            logging.info("✅ Данные записаны в Google Sheets")
        except Exception as e:
            logging.error(f"Ошибка записи в Google Sheets: {e}")

# === TEST GOOGLE SHEETS ===
async def test_google_sheets():
    try:
        sheet = client.open_by_key(TABLE_ID).sheet1
        sheet.append_row(["Тестовая запись", "123"])
        print("✅ Запись успешно добавлена!")
    except Exception as e:
        print(f"Ошибка: {e}")

# === MAIN ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start_shift", start_shift))
    app.add_handler(CallbackQueryHandler(end_shift_callback, pattern="^end_shift"))

    print("✅ Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    # Для теста Google Sheets раскомментируй:
    # asyncio.run(test_google_sheets())
    main()
