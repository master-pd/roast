import re
from typing import Any, Dict, List, Optional
#from typing import Dict, List, Tuple
from config import Config
from utils.helpers import Helpers

class TextProcessor:
    # Topic detection keywords (Bengali)
    TOPIC_KEYWORDS = {
        "funny": ["মজা", "হাসি", "কমেডি", "জোক", "লাফ", "ঠাট্টা", "ঠিকানা"],
        "sad": ["দুঃখ", "একাকী", "কষ্ট", "অভিমান", "কান্না", "বিরহ"],
        "love": ["ভালোবাসা", "প্রেম", "আকাশ", "চাঁদ", "হৃদয়", "পাগল"],
        "motivation": ["সফলতা", "উদ্যোগ", "চেষ্টা", "লক্ষ্য", "স্বপ্ন", "কঠিন"],
        "attitude": ["আমি", "বস", "হিরো", "সেরা", "কিং", "রাজা", "মহারাজ"]
    }
    
    # Reaction emojis for each topic
    REACTION_EMOJIS = {
        "funny": ["😂", "🤣", "😹", "👏"],
        "sad": ["😢", "😭", "☹️", "🤗"],
        "love": ["❤️", "😍", "🥰", "💖"],
        "motivation": ["💪", "🔥", "🏆", "🚀"],
        "attitude": ["😎", "🤘", "😏", "👑"]
    }
    
    @classmethod
    def detect_topic(cls, text: str) -> List[str]:
        """টেক্সট থেকে টপিক ডিটেক্ট করে"""
        text_lower = text.lower()
        detected_topics = []
        
        for topic, keywords in cls.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_topics.append(topic)
                    break
        
        return detected_topics if detected_topics else ["neutral"]
    
    @classmethod
    def get_reaction_emojis(cls, topics: List[str]) -> List[str]:
        """টপিকের উপর ভিত্তি করে ইমোজি রিটার্ন করে"""
        emojis = []
        for topic in topics:
            if topic in cls.REACTION_EMOJIS:
                emojis.extend(cls.REACTION_EMOJIS[topic])
        
        # Remove duplicates and limit to 3
        unique_emojis = list(dict.fromkeys(emojis))
        return unique_emojis[:3]
    
    @classmethod
    def contains_disallowed_content(cls, text: str) -> bool:
        """ডিসঅ্যালোয়েড কন্টেন্ট চেক করে"""
        if not Config.DISALLOWED_WORDS:
            return False
        
        text_lower = text.lower()
        for word in Config.DISALLOWED_WORDS:
            if word.strip() and word.strip() in text_lower:
                return True
        
        return False
    
    @classmethod
    def extract_mentions(cls, text: str) -> List[str]:
        """টেক্সট থেকে মেনশন এক্সট্র্যাক্ট করে"""
        return re.findall(r'@(\w+)', text)
    
    @classmethod
    def analyze_mood(cls, text: str) -> Dict[str, Any]:
        """টেক্সটের মুড অ্যানালাইসিস করে"""
        # Count emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
                           "]+", flags=re.UNICODE)
        
        emojis = emoji_pattern.findall(text)
        emoji_count = len(emojis)
        
        # Count punctuation for intensity
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        # Calculate mood score
        intensity = min(10, (exclamation_count * 2) + emoji_count)
        
        return {
            "emoji_count": emoji_count,
            "exclamation_count": exclamation_count,
            "question_count": question_count,
            "intensity": intensity,
            "has_emojis": emoji_count > 0
        }
