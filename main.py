import os
import time
from display_progress import progress_for_pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Configure these via environment variables or directly (not recommended to hardcode tokens)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = os.getenv("API_ID", "")
API_HASH = os.getenv("API_HASH", "")

Bot = Client(
    "Thumb-Bot",
    bot_token=BOT_TOKEN or None,
    api_id=int(API_ID) if str(API_ID).isdigit() else None,
    api_hash=API_HASH or None,
)

START_TXT = (
    "Hi {}, I am video thumbnail changer Bot by @uchkiyotaka .\n\n"
    "Send a video/file to get started."
)

START_BTN = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Source Code", url="https://github.com/uchmadara/cover-change-bot")]]
)


@Bot.on_message(filters.command(["start"]))
async def start(client, message):
    text = START_TXT.format(message.from_user.mention)
    reply_markup = START_BTN
    await message.reply_text(
        text=text, disable_web_page_preview=True, reply_markup=reply_markup
    )


# global variable to store path of the recent sent thumbnail
thumb = None


@Bot.on_message(filters.private & (filters.video | filters.document))
async def thumb_change(client, m):
    global thumb
    msg = await m.reply("`Downloading..`")
    c_time = time.time()
    file_dl_path = await client.download_media(
        message=m, progress=progress_for_pyrogram, progress_args=("Downloading file..", msg, c_time)
    )
    await msg.delete()

    prompt = "Now send the thumbnail" + (" or /keep to keep the previous thumb" if thumb else "")
    answer = await client.ask(m.chat.id, prompt, filters=filters.photo | filters.text)

    if answer is None:
        return

    if getattr(answer, "photo", None):
        # remove previous thumb if exists
        try:
            if thumb and os.path.exists(thumb):
                os.remove(thumb)
        except Exception:
            pass

        thumb = await client.download_media(message=answer.photo)

        msg = await m.reply("`Uploading..`")
        c_time = time.time()

        try:
            if m.document:
                await client.send_document(
                    chat_id=m.chat.id,
                    document=file_dl_path,
                    thumb=thumb,
                    caption=m.caption if m.caption else None,
                    progress=progress_for_pyrogram,
                    progress_args=("Uploading file..", msg, c_time),
                )
            elif m.video:
                await client.send_video(
                    chat_id=m.chat.id,
                    video=file_dl_path,
                    thumb=thumb,
                    caption=m.caption if m.caption else None,
                    progress=progress_for_pyrogram,
                    progress_args=("Uploading file..", msg, c_time),
                )
        finally:
            await msg.delete()
            try:
                if os.path.exists(file_dl_path):
                    os.remove(file_dl_path)
            except Exception:
                pass


if __name__ == "__main__":
    Bot.run()
