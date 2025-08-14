import os
import re
from uuid import uuid4

from yt_dlp import YoutubeDL
from telegram import Update,  InlineQueryResultVideo, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, ContextTypes, InlineQueryHandler
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def validate_url(url: str) -> bool:
    url_regex = r"^https?://(?:www\.)?instagram\.com/reels?/[A-Za-z0-9_-]+/?(?:\?[^\s#]*)?(?:#[^\s]*)?$"
    match = re.match(url_regex, url)
    return not match == None

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query

    if not query:
        return
    
    if not validate_url(query):
        result = InlineQueryResultArticle(
            id=str(uuid4()),
            title="URL is not valid :c",
            input_message_content=InputTextMessageContent("URL is not valid :c")
        )

    else:
        with YoutubeDL({
                "format": "best",
                "quiet": True,
                "forceurl": True,
                "skip_download": True
            }) as ydl:

            try:
                video = ydl.extract_info(query)

                thumbnail = video.get("thumbnail")
                url = video.get("url")

                result = InlineQueryResultVideo(
                    id=str(uuid4()),
                    title="Share video :3",
                    mime_type="video/mp4",
                    video_url=url,
                    thumbnail_url=thumbnail
                )
            except:
                result = InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="URL is not valid :c",
                    input_message_content=InputTextMessageContent("URL is not valid :c")
                )

    await update.inline_query.answer([result])


def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(InlineQueryHandler(inline_query))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()