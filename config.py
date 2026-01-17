import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Token
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # Admin IDs
    OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "987654321,1122334455").split(",")))
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///roastify.db")
    
    # Bot Settings
    BOT_USERNAME = os.getenv("BOT_USERNAME", "RoastifyBot")
    MIN_INPUT_LENGTH = int(os.getenv("MIN_INPUT_LENGTH", "4"))
    
    # Image Settings
    IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "1080"))
    IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "1080"))
    DEFAULT_FONT = os.getenv("DEFAULT_FONT", "arial.ttf")
    
    # Paths
    ASSETS_PATH = os.getenv("ASSETS_PATH", "assets")
    FONTS_PATH = os.path.join(ASSETS_PATH, "fonts")
    BACKGROUNDS_PATH = os.path.join(ASSETS_PATH, "backgrounds")
    TEMPLATES_PATH = os.path.join(ASSETS_PATH, "templates")
    
    # Time Settings
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Dhaka")
    
    # Safety
    DISALLOWED_WORDS = os.getenv("DISALLOWED_WORDS", "").split(",")
    
    # Vote System
    VOTE_WINDOW = int(os.getenv("VOTE_WINDOW", "300"))
    
    # Reaction System
    MAX_REACTIONS_PER_HOUR = int(os.getenv("MAX_REACTIONS_PER_HOUR", "20"))
    REACTION_COOLDOWN = int(os.getenv("REACTION_COOLDOWN", "15"))
    
    # Welcome Messages (comma separated)
    WELCOME_MESSAGES = os.getenv("WELCOME_MESSAGES", "স্বাগতম!,বট চালু হয়েছে!,রোস্টের জন্য প্রস্তুত!").split(",")
    
    @classmethod
    def validate(cls):
        """Validate essential configurations"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required in environment variables")
        if not cls.BOT_USERNAME:
            raise ValueError("BOT_USERNAME is required")