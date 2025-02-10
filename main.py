import os

from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import Application, ContextTypes, InlineQueryHandler, ChosenInlineResultHandler
from dotenv import load_dotenv

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.chosen_inline_result.query

async def chosen_inline_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("sss2")

def main() -> None:
    load_dotenv()

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(ChosenInlineResultHandler(chosen_inline_result))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()