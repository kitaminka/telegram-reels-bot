import os
import re
import requests
import tempfile
from uuid import uuid4

from yt_dlp import YoutubeDL
from telegram import Update, InlineQueryResultArticle, InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent
from telegram.ext import Application, ContextTypes, InlineQueryHandler, ChosenInlineResultHandler
from dotenv import load_dotenv

def validate_url(url: str) -> bool:
    url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    match = re.match(url_pattern, url)
    return not match == None

async def get_video_info(query: str) -> (bool, str, str):
    with YoutubeDL({
            "noplaylist": True,
            "extract_flat": True,
            "skip_download": True,
            "quiet": True
        }) as ydl:

        is_url = validate_url(query)
        if is_url:
            try:
                video_info = ydl.extract_info(query, download=False)
                return True, video_info["title"], video_info["thumbnails"][0]["url"]
            except:
                return False, "No results", None
            
        entries = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"]
        if len(entries) == 0:
            return False, "No results", None
            
        video_info = entries[0]
        return True, video_info["title"], video_info["thumbnails"][0]["url"]

async def download_video(url, dir_path) -. (str, str):
    with yt_dlp.YoutubeDL({
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": os.path.join(dir_path, "%(title)s.%(ext)s"),
            "quiet": True,
        }) as ydl:

        video_info = await ydl.extract_info(url, download=True)
        file_path = await ydl.prepare_filename(video_info)
    
        return file_path, video_info["title"]

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    if not query:
        return

    found, title, thumbnail_url = await get_video_info(query)

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(":3", callback_data="button_click")]])

    if found:
        message_content = InputTextMessageContent("Downloading...")
    else:
        message_content = InputTextMessageContent("Failed to download the video.")

    result = InlineQueryResultArticle(
        id=str(uuid4()),
        title=title,
        thumbnail_url=thumbnail_url,
        input_message_content=message_content,
        reply_markup=keyboard,
    )

    await update.inline_query.answer([result])

async def chosen_inline_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.chosen_inline_result.query
    user_id = update.chosen_inline_result.from_user.id

    with tempfile.TemporaryDirectory() as temp_dir:
        await download_video(temp_dir, query)


def main() -> None:
    load_dotenv()

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(ChosenInlineResultHandler(chosen_inline_result))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()