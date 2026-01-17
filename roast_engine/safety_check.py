import re
from typing import List, Set
from config import Config
from utils.logger import logger

class SafetyChecker:
    def __init__(self):
        self.disallowed_words = set(Config.DISALLOWED_WORDS or [])
        self._load_bad_words()
    
    def _load_bad_words(self):
        """অনাকাঙ্ক্ষিত শব্দ লোড করে"""
        # Add common bad words (Bengali)
        bengali_bad_words = {
            "গালি", "অশ্লীল", "খারাপ", "মন্দ", "অপমান", 
            "রুষ্ট", "বিরক্ত", "হুমকি", "গালাগালি"
        }
        self.disallowed_words.update(bengali_bad_words)
    
    def sanitize_input(self, text: str) -> str:
        """ইনপুট টেক্সট স্যানিটাইজ করে"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '[লিংক]', text)
        
        # Remove phone numbers
        text = re.sub(r'\+?\d[\d\s\-]{7,}\d', '[ফোন]', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', '[ইমেইল]', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def is_safe_content(self, text: str) -> bool:
        """কন্টেন্ট সেফ কিনা চেক করে"""
        # Check minimum length
        if len(text) < Config.MIN_INPUT_LENGTH:
            return False
        
        # Check for disallowed words
        text_lower = text.lower()
        for word in self.disallowed_words:
            if word and word in text_lower:
                logger.warning(f"Disallowed word detected: {word}")
                return False
        
        # Check for only numbers
        if text.replace(' ', '').isdigit():
            return False
        
        # Check for only emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
                           "]+", flags=re.UNICODE)
        
        if emoji_pattern.fullmatch(text):
            return False
        
        # Check for only special characters
        if re.match(r'^[^\w\u0980-\u09FF]+$', text):
            return False
        
        return True
    
    def is_owner_or_admin(self, user_id: int) -> bool:
        """ইউজার ওনার অ্যাডমিন কিনা চেক করে"""
        return user_id == Config.OWNER_ID or user_id in Config.ADMIN_IDS
    
    def check_for_trigger_words(self, text: str, triggers: List[str] = None) -> bool:
        """ট্রিগার ওয়ার্ড চেক করে"""
        if triggers is None:
            triggers = ["গালি", "অপমান", "রোজ", "বিরক্ত করা", "হুমকি"]
        
        text_lower = text.lower()
        for trigger in triggers:
            if trigger in text_lower:
                return True
        
        return False
    
    def is_protected_user_message(self, user_id: int, text: str) -> bool:
        """প্রটেক্টেড ইউজার মেসেজ কিনা চেক করে"""
        if not self.is_owner_or_admin(user_id):
            return False
        
        return self.check_for_trigger_words(text)