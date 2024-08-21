import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# API Configuration
API_ID = int(os.getenv("21740783"))
API_HASH = os.getenv("a5dc7fec8302615f5b441ec5e238cd46")
BOT_TOKEN = os.getenv("7116266807:AAFiuS4MxcubBiHRyzKEDnmYPCRiS0f3aGU")

# Channel IDs
TARGET_CHANNEL_ID = int(os.getenv("-1002183423252"))  # The channel where videos will be uploaded
SOURCE_CHANNEL_ID = int(os.getenv("-1002245327685"))  # The channel to monitor for new videos

# File paths and settings
THUMBNAIL_PATH = "Warrior Tamil.jpg"  # Path to your default thumbnail
CUSTOM_CAPTION = "Anime: {anime_name}\nEpisode: {episode_number}\nQuality: {quality}"
