import os
import logging
from flask import Flask, request
from pyrogram import Client, filters
import config  # Import configurations from config.py

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
flask_app = Flask(__name__)

app = Client(
    "anime_userbot",  # This should be a userbot session name
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    phone_number=config.PHONE_NUMBER  # This is needed for userbot login
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

@app.on_message(filters.command("join_channel") & filters.private)
async def join_channel(client, message):
    # Automatically join a source channel
    try:
        await client.join_chat(config.SOURCE_CHANNEL_USERNAME)  # Use the channel's username to join
        await message.reply(f"Successfully joined the channel: {config.SOURCE_CHANNEL_USERNAME}")
        logger.info(f"Bot joined the channel: {config.SOURCE_CHANNEL_USERNAME}")
    except Exception as e:
        await message.reply(f"Failed to join the channel: {e}")
        logger.error(f"Failed to join the channel: {e}")

@app.on_message(filters.channel & filters.video & filters.chat(config.SOURCE_CHANNEL_ID))
async def auto_upload(client, message):
    # Log receipt of the message
    logger.info(f"Received video message in source channel {config.SOURCE_CHANNEL_ID}")

    # Extract video details
    anime_name, episode_number, quality = extract_info_from_filename(message.video.file_name)

    if anime_name and episode_number and quality:
        logger.info(f"Processing video: {anime_name} - {episode_number} - {quality}")

        # Create new file name
        new_filename = f"{anime_name} - {episode_number} - {quality}.mp4"

        # Download the video asynchronously
        video_path = await message.download(file_name=new_filename)

        try:
            # Send the video with the new filename, custom caption, and thumbnail
            await client.send_video(
                chat_id=config.TARGET_CHANNEL_ID,
                video=video_path,
                caption=config.CUSTOM_CAPTION.format(anime_name=anime_name, episode_number=episode_number, quality=quality),
                thumb=config.THUMBNAIL_PATH
            )
            logger.info("Video uploaded successfully to the target channel.")
        except Exception as e:
            logger.error(f"Failed to upload video: {e}")
        finally:
            # Delete the local file after upload to save space
            os.remove(video_path)
    else:
        logger.warning("Filename format is not recognized. Skipping upload.")

@app.on_message(filters.photo & filters.private)
async def set_thumbnail(client, message):
    # Save the thumbnail image
    photo_path = await message.download()
    config.THUMBNAIL_PATH = photo_path
    logger.info(f"Thumbnail image saved at {photo_path}")

    # Notify the user that the thumbnail has been added successfully
    await message.reply("Thumbnail added successfully.")

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    # Handle incoming webhooks or other Flask-related routes here
    data = request.json
    return {"status": "received", "data": data}

if __name__ == "__main__":
    app.run()
