import os
import re
import requests
import tempfile
from uuid import uuid4

from yt_dlp import YoutubeDL
from telegram import Update, InlineQueryResultArticle, InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent, InputMediaVideo
from telegram.ext import Application, ContextTypes, InlineQueryHandler, ChosenInlineResultHandler
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def validate_url(url: str) -> bool:
    url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    match = re.match(url_pattern, url)
    return not match == None

async def download_video(query: str, temp_dir: str) -> (bool, str, str):
    with YoutubeDL({
            "noplaylist": True,
            "format": "best",
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "quiet": True,
        }) as ydl:

        is_url = validate_url(query)

        try:
            if is_url:
                video_info = ydl.extract_info(query)
            else:
                entries = ydl.extract_info(f"ytsearch:{query}")["entries"]

                if len(entries) == 0:
                    return False, "", ""

                video_info = entries[0]
        except:
            return False, "", ""

        file_path = ydl.prepare_filename(video_info)
        
        return True, file_path, video_info.get("title", "Video")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    if not query:
        return

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(":3", callback_data="button_click")]])

    result = InlineQueryResultArticle(
        id=str(uuid4()),
        title="Download video",
        input_message_content=InputTextMessageContent("Downloading..."),
        reply_markup=keyboard,
    )

    await update.inline_query.answer([result])

async def chosen_inline_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.chosen_inline_result.query
    user_id = update.chosen_inline_result.from_user.id

    with tempfile.TemporaryDirectory() as temp_dir:
        found, file_path, title = await download_video(query, temp_dir)

        if found:
            try:
                msg = await context.bot.send_video(chat_id=user_id, video=open(file_path, "rb"), caption=title)
                await context.bot.edit_message_media(
                    inline_message_id=update.chosen_inline_result.inline_message_id,
                    media=InputMediaVideo(media=msg.video.file_id)
                )
            except:
                await context.bot.edit_message_text(
                    inline_message_id=update.chosen_inline_result.inline_message_id,
                    text="Failed to download the video :("
                )
        else:
            await context.bot.edit_message_text(
                inline_message_id=update.chosen_inline_result.inline_message_id,
                text="Video not found :("
            )


def main() -> None:

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(ChosenInlineResultHandler(chosen_inline_result))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()