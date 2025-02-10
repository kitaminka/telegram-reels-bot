import os
import yt_dlp
import logging
import tempfile
from html import escape
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineQueryResultVideo, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaVideo, Video
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler, ChosenInlineResultHandler

inline_message_id_storage = None

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

with tempfile.TemporaryDirectory() as temp_dir:
    print(temp_dir)

    def download_video(url):

        os.makedirs(temp_dir, exist_ok=True)
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            # 'merge_output_format': 'mp4',
            # 'postprocessors': [{
            #     'key': 'FFmpegVideoConvertor',
            #     'preferedformat': 'mp4',  # Convert to MP4 if necessary
            # }],
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            return file_path, info.get("title", "Video")

    async def chosen_inline_result(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global inline_message_id_storage


        # Store the inline_message_id for later use
        inline_message_id_storage = update.chosen_inline_result.inline_message_id
        print(inline_message_id_storage)
        await edit_test(update, context)

    async def edit_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("test1")
        query = update.chosen_inline_result.query
        user_id = update.chosen_inline_result.from_user.id
        file_path, title = download_video(query)
        
            # print(msg.video.file_id)

            # await context.bot.edit_message_text(
            #     inline_message_id=inline_message_id_storage,
            #      text='Updated content after 10 seconds'
            # )
        # with open(file_path, 'rb') as video_file:
        print(user_id)
        print(context.bot.id)
        msg1 = await context.bot.send_message(chat_id=user_id, text="aaaaa")
        # msg = await context.bot.send_video(chat_id=user_id, video=open(file_path, 'rb'), caption=title)
        print("test")
        await context.bot.edit_message_media(
            chat_id=user_id,
            message_id=msg1.id,
            media=InputMediaVideo(media=open(file_path, 'rb'))
        )
        # await context.bot.edit_message_media(
        #     inline_message_id=inline_message_id_storage,
        #     media=InputMediaVideo(media=msg.video.file_id)
        # )

    async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.inline_query.query

        if not query:
            return

        try:
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(":3", callback_data="button_click")]])

            result2 = InlineQueryResultArticle(
                id=str(uuid4()),
                title=f"Download and send",
                input_message_content=InputTextMessageContent(
                    f"Downloading..."
                ),
                reply_markup=keyboard,
            )
            result = InlineQueryResultVideo(
                id=str(uuid4()),
                title=f"Download and send",
                mime_type="video/mp4",
                thumbnail_url="https://static.wikia.nocookie.net/tmfatefanon/images/5/5e/Castolfo.jpg/revision/latest/scale-to-width-down/284?cb=20180217213909",
                video_url="http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
                reply_markup=keyboard,
            )

            await update.inline_query.answer([result])


            # print(msg)
            # result = InlineQueryResultCachedVideo(
            #     id=str(uuid4()),
            #     title=f"Downloaded",
            #     video_file_id=msg.video.file_id,
            # )
            # await update.inline_query.answer([result])

        except Exception as e:
            print(f"Error: {e}")

    def main() -> None:
        """Run the bot."""
        # Create the Application and pass it your bot's token.
        application = Application.builder().token("").build()

        # on inline queries - show corresponding inline results
        application.add_handler(InlineQueryHandler(inline_query))
        application.add_handler(ChosenInlineResultHandler(chosen_inline_result))

        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)


    if __name__ == "__main__":
        main()