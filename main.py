import os
import re
import requests
from uuid import uuid4

from yt_dlp import YoutubeDL
from telegram import Update, InlineQueryResultArticle, InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent
from telegram.ext import Application, ContextTypes, InlineQueryHandler, ChosenInlineResultHandler
from dotenv import load_dotenv

def validate_url(url):
    url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    match = re.match(url_pattern, url)
    return not match == None

async def get_video_info(query):
    with YoutubeDL({"noplaylist": True, "extract_flat": True, "skip_download": True}) as ydl:
        is_url = validate_url(query)
        if is_url:
            try:
                video_info = ydl.extract_info(query, download=False)
                return video_info["title"], video_info["thumbnails"][0]["url"]
            except:
                return "No results", None
            
        entries = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"]
        if len(entries) == 0:
            return "No results", None
            
        video_info = entries[0]
        return video_info["title"], video_info["thumbnails"][0]["url"]

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    if not query:
        return

    title, thumbnail_url = await get_video_info(query)
    # print(thumbnail_url)

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(":3", callback_data="button_click")]])

    result = InlineQueryResultArticle(
        id=str(uuid4()),
        title=title,
        thumbnail_url=thumbnail_url,
        input_message_content=InputTextMessageContent("Downloading..."),
        reply_markup=keyboard,
    )

    await update.inline_query.answer([result])

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