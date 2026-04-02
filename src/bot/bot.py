import logging
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

BASE_DIR = Path(__file__).resolve().parent.parent
EXE_PATH = BASE_DIR / "v2ray_auto_scanner.exe"
OUTPUT_FAST = BASE_DIR / "output" / "fast_nodes.txt"
LOG_FILE = BASE_DIR / "bot.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для генерации v2ray конфигов.\n"
        "/scan — запустить сканер и получить свежие конфиги\n"
        "/last — прислать последние сохранённые конфиги"
    )


async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not EXE_PATH.exists():
        msg = f"[!] Не найден exe: {EXE_PATH}"
        logging.error(msg)
        await update.message.reply_text(msg)
        return

    await update.message.reply_text("Запускаю сканирование, готовлю новые конфиги...")

    logging.info("Запуск сканера: %s (запрос из chat_id=%s)", EXE_PATH, chat_id)

    try:
        result = subprocess.run(
            [str(EXE_PATH)],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logging.info("Сканер завершился с кодом %s", result.returncode)
        if result.stdout:
            logging.info("STDOUT:\n%s", result.stdout)
        if result.stderr:
            logging.warning("STDERR:\n%s", result.stderr)
    except Exception as e:
        logging.exception("Ошибка при запуске сканера")
        await update.message.reply_text(f"[!] Ошибка запуска сканера: {e}")
        return

    if not OUTPUT_FAST.exists():
        msg = "[!] Сканер завершился, но fast_nodes.txt не найден."
        logging.error(msg)
        await update.message.reply_text(msg)
        return

    await update.message.reply_text("Сканирование завершено, отправляю новые конфиги...")

    with open(OUTPUT_FAST, "rb") as f:
        await context.bot.send_document(
            chat_id=chat_id,
            document=f,
            filename="fast_nodes.txt",
            caption="Скопируй документ в буфер обмена и сделай импорт в v2ray клиенте (V2BOX, v2RayTun и т.д.)",
        )


async def last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not OUTPUT_FAST.exists():
        await update.message.reply_text("[!] Ещё ни разу не запускался сканер, fast_nodes.txt нет.")
        return

    await update.message.reply_text("Отправляю последние конфиги...")

    with open(OUTPUT_FAST, "rb") as f:
        await context.bot.send_document(
            chat_id=chat_id,
            document=f,
            filename="fast_nodes.txt",
            caption="Последние сохранённые конфиги",
        )


def main():
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        print("[!] BOT_TOKEN не настроен. Скопируй .env.example в .env и заполни токен!")
        sys.exit(1)

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("scan", scan))
    application.add_handler(CommandHandler("last", last))

    logging.info("Бот запущен. Ожидание команд...")
    application.run_polling()


if __name__ == "__main__":
    main()
