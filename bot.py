from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
import os
import re
import config

# Initialize the bot client
app = Client(
    "anime_upload_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# Function to extract details from the file name
def extract_anime_details(file_name):
    pattern = r"(?P<name>.+?)\s+-\s+Episode\s+(?P<episode>\d+)\s+\[(?P<quality>\d+p)\]"
    match = re.search(pattern, file_name)
    if match:
        return match.group('name'), match.group('episode'), match.group('quality')
    else:
        return None, None, None

# Function to rename the video
def rename_video(file_name):
    anime_name, episode_number, quality = extract_anime_details(file_name)
    if anime_name and episode_number and quality:
        new_name = f"{anime_name} - Episode {episode_number} [{quality}].mp4"
    else:
        new_name = f"Renamed_Anime_Episode.mp4"  # Fallback name if pattern doesn't match
    return new_name

@app.on_message(filters.chat(config.SOURCE_CHANNEL_ID) & filters.video)
async def forward_and_upload(client, message):
    # Download the video
    download_path = await message.download()

    # Extract the file name from the downloaded path
    file_name = os.path.basename(download_path)

    # Rename the video
    new_name = rename_video(file_name)
    new_path = os.path.join(os.path.dirname(download_path), new_name)
    os.rename(download_path, new_path)

    # Upload the video to the target channel with a custom caption and thumbnail
    await client.send_video(
        chat_id=config.TARGET_CHANNEL_ID,
        video=new_path,
        caption=config.CUSTOM_CAPTION,
        thumb=config.THUMBNAIL_PATH,
        supports_streaming=True
    )

    # Delete the local file after uploading
    os.remove(new_path)

if __name__ == "__main__":
    app.run()
