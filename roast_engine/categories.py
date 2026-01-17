from typing import Dict, List, Set
from enum import Enum

class RoastCategory(str, Enum):
    SENTENCE_LOGIC = "sentence_logic"
    OVERCONFIDENCE = "overconfidence"
    COMMON_LIES = "common_lies"
    DAILY_HABITS = "daily_habits"
    SELF_CLAIMS = "self_claims"
    TARGETED = "targeted"
    NEUTRAL = "neutral"

class RoastCategoryManager:
    ALLOWED_CATEGORIES = {
        RoastCategory.SENTENCE_LOGIC,
        RoastCategory.OVERCONFIDENCE,
        RoastCategory.COMMON_LIES,
        RoastCategory.DAILY_HABITS,
        RoastCategory.SELF_CLAIMS,
        RoastCategory.TARGETED,
        RoastCategory.NEUTRAL
    }
    
    DISALLOWED_TARGETS = {
        "religion",
        "race",
        "body",
        "family",
        "gender",
        "sexuality",
        "disability",
        "politics",
        "personal_appearance",
        "financial_status"
    }
    
    @classmethod
    def validate_category(cls, category: str) -> bool:
        """ক্যাটাগরি ভ্যালিড কিনা চেক করে"""
        return category in cls.ALLOWED_CATEGORIES
    
    @classmethod
    def is_disallowed_target(cls, target: str) -> bool:
        """টার্গেট ডিসঅ্যালোয়েড কিনা চেক করে"""
        return target.lower() in cls.DISALLOWED_TARGETS
    
    @classmethod
    def get_allowed_categories_list(cls) -> List[str]:
        """অনুমোদিত ক্যাটাগরির লিস্ট রিটার্ন করে"""
        return [cat.value for cat in cls.ALLOWED_CATEGORIES]
    
    @classmethod
    def get_category_weight(cls, category: str, votes: Dict[str, int] = None) -> float:
        """ক্যাটাগরির ওয়েট ক্যালকুলেট করে (ভোটের ভিত্তিতে)"""
        base_weights = {
            RoastCategory.SENTENCE_LOGIC: 1.0,
            RoastCategory.OVERCONFIDENCE: 0.8,
            RoastCategory.COMMON_LIES: 0.7,
            RoastCategory.DAILY_HABITS: 0.6,
            RoastCategory.SELF_CLAIMS: 0.9,
            RoastCategory.TARGETED: 0.5,
            RoastCategory.NEUTRAL: 0.3
        }
        
        weight = base_weights.get(category, 0.5)
        
        # Adjust based on votes if provided
        if votes:
            funny_votes = votes.get("funny", 0)
            savage_votes = votes.get("savage", 0)
            
            if funny_votes > 5:
                weight *= 1.2
            if savage_votes > 3:
                weight *= 1.1
        
        return min(weight, 2.0)  # Cap at 2.0
    
    @classmethod
    def should_use_profile_photo(cls, text: str, category: str) -> bool:
        """প্রোফাইল ফটো ইউজ করা উচিত কিনা চেক করে"""
        short_emotional = len(text) < 10 and any(word in text.lower() for word in ["💔", "😢", "😭", "❤️"])
        attitude_claim = "আমি" in text and category == RoastCategory.SELF_CLAIMS
        self_identity = any(word in text.lower() for word in ["রাজা", "কিং", "বস", "হিরো"])
        
        return short_emotional or attitude_claim or self_identity