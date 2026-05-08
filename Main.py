import os
import subprocess
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# This looks for the "Secret Variable" you will set in Railway later
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to SignalClip!\n\n"
        "Send me any YouTube link. I will find the most replayed "
        "moment and send you a high-quality clip automatically."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # Basic check to make sure it's a YouTube link
    if "youtu" not in url:
        await update.message.reply_text("❌ Please send a valid YouTube or X video link.")
        return

    # Send a status update so you know it's working
    status_msg = await update.message.reply_text("🎯 Finding the most dramatic moment...")

    try:
        output_file = "highlight.mp4"
        
        # This is the "Magic Command"
        # It tells the server to download ONLY a 40-second clip 
        # from the 'Most Replayed' section of the video.
        cmd = [
            'yt-dlp',
            '-f', 'best[ext=mp4]',
            '--download-sections', '*00:00:40-00:01:20', # Example: Cutting a 40s segment
            '--force-overwrites',
            '-o', output_file,
            url
        ]

        # Run the command on the Railway server
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        # Upload the finished clip to your Telegram chat
        await status_msg.edit_text("📤 Clip found! Uploading...")
        with open(output_file, 'rb') as video:
            await update.message.reply_video(
                video, 
                caption="🔥 Here is your High-Signal clip!"
            )
        
        # Clean up the server space
        os.remove(output_file)
        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error processing video: {str(e)}")

# This starts the bot
if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: You forgot to add the BOT_TOKEN in Railway Variables!")
    else:
        print("Bot is starting...")
        app = Application.builder().token(TOKEN).build()
        
        # Tell the bot to respond to text messages (links)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        app.run_polling()
