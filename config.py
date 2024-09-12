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

FILE_STORE_BOT_ID = "@Occoccicfx_bot"
THUMBNAIL_PATH = 'path_to_thumbnail'  # Initially can be None

# Custom Caption Template
CUSTOM_CAPTION = os.getenv("CUSTOM_CAPTION", "Anime: {anime_name}\nEpisode {episode_number} Added ✅\nQuality: {quality}✅\nClick to download your preferred quality ✅")
