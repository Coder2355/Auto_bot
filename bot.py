import os
import logging
from flask import Flask, request
from pyrogram import Client, filters
import asyncio
import config  # Import configurations from config.py

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
flask_app = Flask(__name__)

app = Client(
    "anime_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

def extract_info_from_filename(filename):
    """
    Extracts the anime name, episode number, and quality from the filename.
    Example: "Naruto_S01E12_720p.mkv" -> ("Naruto", "S01E12", "720p")
    """
    parts = filename.rsplit("_", 2)
    if len(parts) == 3:
        anime_name, episode, quality = parts
        return anime_name, episode, quality
    return None, None, None

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    start_text = "Hello! I'm the Auto Anime Upload Bot.\n\nI automatically monitor a source channel and upload videos to your target channel."
    await message.reply(start_text)

@app.on_message(filters.command("add_thumb") & filters.photo & filters.private)
async def add_thumbnail(client, message):
    # Check if the user is the bot owner
    if message.from_user.id != config.OWNER_ID:
        await message.reply("You are not authorized to set the thumbnail.")
        return

    # Log the received command
    logger.info(f"Received /add_thumb command from {message.from_user.id}")

    # Download the image to use as the thumbnail
    try:
        photo_file = await message.download()
        if not photo_file:
            await message.reply("Failed to download the photo.")
            return

        # Update the config with the new thumbnail path
        config.THUMBNAIL_PATH = photo_file

        # Optionally, you can update the config file with the new path
        with open("config.py", "a") as config_file:
            config_file.write(f"\nTHUMBNAIL_PATH = '{photo_file}'\n")

        await message.reply("Thumbnail updated successfully.")
        logger.info(f"Thumbnail updated to {photo_file}")

    except Exception as e:
        logger.error(f"Error updating thumbnail: {e}")
        await message.reply("An error occurred while updating the thumbnail.")

@app.on_message(filters.channel & filters.video & filters.chat(config.SOURCE_CHANNEL_ID))
async def auto_upload(client, message):
    # Log receipt of the message
    logger.info(f"Received video message in source channel {config.SOURCE_CHANNEL_ID}")

    # Notify the bot owner or channel that the process has started
    bot_owner_id = config.OWNER_ID  # Use the owner ID from the config
    await client.send_message(bot_owner_id, "Process started: Downloading and processing the video...")

    # Extract video details
    anime_name, episode_number, quality = extract_info_from_filename(message.video.file_name)

    if anime_name and episode_number and quality:
        logger.info(f"Processing video: {anime_name} - {episode_number} - {quality}")

        # Create new file name
        new_filename = f"{anime_name} - {episode_number} - {quality}.mp4"

        # Download the video asynchronously
        video_path = await message.download(file_name=new_filename)

        # Send the video with the new filename, custom caption, and thumbnail
        await client.send_video(
            chat_id=config.TARGET_CHANNEL_ID,
            video=video_path,
            caption=config.CUSTOM_CAPTION.format(anime_name=anime_name, episode_number=episode_number, quality=quality),
            thumb=config.THUMBNAIL_PATH
        )

        # Delete the local file after upload to save space
        os.remove(video_path)
        logger.info("Video uploaded successfully to the target channel.")

        # Notify the bot owner that the process is complete
        await client.send_message(bot_owner_id, "Process completed: Video uploaded successfully.")
    else:
        logger.warning("Filename format is not recognized. Skipping upload.")
        await client.send_message(bot_owner_id, "Process failed: Filename format not recognized.")

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    # Handle incoming webhooks or other Flask-related routes here
    data = request.json
    return {"status": "received", "data": data}

if __name__ == "__main__":
    app.run()
