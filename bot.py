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

# Pyrogram client setup
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

async def send_to_file_store(client, video_path):
    """
    Sends the video to the file store bot and retrieves the file link.
    """
    try:
        response = await client.send_document(
            chat_id=config.FILE_STORE_BOT_ID,  # ID of the file store bot
            document=video_path
        )
        # Assuming the link is in the response message
        file_link = response.document.file_id
        return file_link
    except Exception as e:
        logger.error(f"Error sending to file store bot: {e}")
        return None

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

        try:
            # Send to file store bot and get the link
            file_link = await send_to_file_store(client, video_path)

            if not file_link:
                await client.send_message(bot_owner_id, "Process failed: Could not retrieve file link.")
                return

            # Create the caption with buttons
            caption = (f"Anime: {anime_name}\n"
                       f"Episode {episode_number} Added ✅\n"
                       f"Quality: {quality}✅\n"
                       "Enna quality venumo click pannunga File varum ✅")

            # Create buttons for different qualities using the file link
            buttons = [
                [{"text": "480p", "url": file_link if quality == "480p" else ""}],
                [{"text": "720p", "url": file_link if quality == "720p" else ""}],
                [{"text": "1080p", "url": file_link if quality == "1080p" else ""}],
            ]

            # Upload the video with the new filename, custom caption, thumbnail, and buttons
            await client.send_video(
                chat_id=config.TARGET_CHANNEL_ID,
                video=video_path,
                caption=caption,
                thumb=config.THUMBNAIL_PATH,
                reply_markup={"inline_keyboard": buttons}
            )
            logger.info("Video uploaded successfully to the target channel.")

            # Notify the bot owner that the process is complete
            await client.send_message(bot_owner_id, "Process completed: Video uploaded successfully.")
        except Exception as e:
            logger.error(f"Failed to upload video: {e}")
            await client.send_message(bot_owner_id, f"Process failed: {e}")
        finally:
            # Delete the local file after upload to save space
            os.remove(video_path)
    else:
        logger.warning("Filename format is not recognized. Skipping upload.")
        await client.send_message(bot_owner_id, "Process failed: Filename format not recognized.")

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
    # Run Flask app and Pyrogram client
    app.run()
