import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# API Configuration
API_ID = int(os.getenv("API_ID", "21740783"))
API_HASH = os.getenv("API_HASH", "a5dc7fec8302615f5b441ec5e238cd46")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7116266807:AAFiuS4MxcubBiHRyzKEDnmYPCRiS0f3aGU")
OWNER_ID = int(os.getenv("OWNER_ID", "6299192020"))

# Channel IDs
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "-1002183423252"))  # The channel where videos will be uploaded
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID", "-1002245327685"))  # The channel to monitor for new videos

# File paths and settings
THUMBNAIL_PATH = os.getenv("THUMBNAIL_PATH", "https://telegra.ph/file/162f06ba78445ff3fee99.jpg")  # Path to your default thumbnail
CUSTOM_CAPTION = "Anime: {anime_name}\nEpisode: {episode_number}\nQuality: {quality}"
