import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config import Config
from .logger import logger

class Helpers:
    @staticmethod
    def sanitize_text(text: str) -> str:
        """সব ধরনের অপ্রয়োজনীয় ক্যারেক্টার রিমুভ করে"""
        if not text:
            return ""
        
        # Remove links
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Bengali and basic punctuation
        text = re.sub(r'[^\u0980-\u09FF\w\s!?.,]', '', text)
        
        return text.strip()
    
    @staticmethod
    def is_valid_input(text: str) -> bool:
        """ইনপুট ভ্যালিডেশন চেক"""
        if not text or len(text) < Config.MIN_INPUT_LENGTH:
            return False
        
        # Only emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
        
        if emoji_pattern.fullmatch(text):
            return False
        
        # Only numbers
        if text.replace(' ', '').isdigit():
            return False
        
        return True
    
    @staticmethod
    def get_time_based_theme() -> Dict[str, Any]:
        """সময়ভিত্তিক থিম রিটার্ন করে"""
        from utils.time_manager import TimeManager
        current_hour = TimeManager.get_current_hour()
        
        if 6 <= current_hour < 19:
            return {
                "theme": "day",
                "bg_color": (255, 255, 255, 230),
                "text_color": (0, 0, 0),
                "accent_color": (41, 128, 185)
            }
        else:
            return {
                "theme": "night",
                "bg_color": (30, 30, 40, 230),
                "text_color": (255, 255, 255),
                "accent_color": (155, 89, 182)
            }
    
    @staticmethod
    def select_random_welcome() -> str:
        """র‍্যান্ডম ওয়েলকাম মেসেজ সিলেক্ট করে"""
        return random.choice(Config.WELCOME_MESSAGES)
    
    @staticmethod
    def create_user_key(user_id: int, chat_id: int = None) -> str:
        """ইউনিক ইউজার কিং তৈরী করে"""
        if chat_id:
            return f"{user_id}:{chat_id}"
        return str(user_id)
    
    @staticmethod
    def split_text_for_image(text: str, max_chars_per_line: int = 30) -> List[str]:
        """ইমেজের জন্য টেক্সট লাইনে ভাগ করে"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars_per_line:
                current_line += (" " + word if current_line else word)
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [text]