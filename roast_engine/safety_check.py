"""
Safety Check System for Roastify Bot
Fixed with all required methods
"""

import re
import json
from typing import List, Set, Dict, Any, Optional
from pathlib import Path
from config import Config
from utils.logger import logger
from utils.time_manager import TimeManager

class SafetyChecker:
    """সেফটি চেকার ক্লাস - সমস্ত মেথড সহ"""
    
    def __init__(self):
        self.disallowed_words = set(Config.DISALLOWED_WORDS or [])
        self._load_bad_words()
        self._load_safety_patterns()
        
        # User safety tracking
        self.user_safety_score = {}
        self.suspicious_users = set()
        
        logger.info("SafetyChecker initialized with all methods")
    
    def _load_bad_words(self):
        """অনাকাঙ্ক্ষিত শব্দ লোড করে"""
        # Bengali inappropriate words
        bengali_bad_words = {
            "গালি", "অপমান", "অশ্লীল", "খারাপ", "মন্দ",
            "বিরক্ত", "হুমকি", "গালাগালি", "অভদ্র", "অসভ্য",
            "নষ্ট", "খারাপ", "অপবাদ", "নিন্দা"
        }
        
        # English inappropriate words
        english_bad_words = {
            "abuse", "fuck", "shit", "asshole", "bastard",
            "idiot", "stupid", "retard", "moron", "dumb",
            "hate", "kill", "die", "stupid"
        }
        
        # Add to disallowed words
        self.disallowed_words.update(bengali_bad_words)
        self.disallowed_words.update(english_bad_words)
        
        # Load from file if exists
        banned_file = Path("assets/safety/banned_words.txt")
        if banned_file.exists():
            try:
                with open(banned_file, 'r', encoding='utf-8') as f:
                    additional_words = f.read().splitlines()
                    self.disallowed_words.update(additional_words)
            except Exception as e:
                logger.error(f"Error loading banned words file: {e}")
    
    def _load_safety_patterns(self):
        """সেফটি প্যাটার্ন লোড করে"""
        self.spam_patterns = [
            (r'(http[s]?://\S+\s*){3,}', "multiple_urls"),
            (r'([\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]){10,}', "emoji_spam"),
            (r'(\S+\s+){3,}\1', "repeated_text"),
            (r'[A-Z\u0980-\u09FF]{15,}', "excessive_caps"),
            (r'@\w+\s*@\w+\s*@\w+', "multiple_mentions"),
        ]
        
        self.personal_info_patterns = [
            (r'\+?(88)?01[3-9]\d{8}', "phone_number"),
            (r'\d{4}[-\.\s]?\d{4}[-\.\s]?\d{4}', "phone_format"),
            (r'\S+@\S+\.\S+', "email_address"),
            (r'\b\d{10,17}\b', "id_number"),
        ]
    
    def sanitize_input(self, text: str) -> str:
        """ইনপুট টেক্সট স্যানিটাইজ করে"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '[লিংক]', text)
        
        # Remove phone numbers
        text = re.sub(r'\+?(88)?01[3-9]\d{8}', '[ফোন]', text)
        text = re.sub(r'\d{4}[-\.\s]?\d{4}[-\.\s]?\d{4}', '[ফোন]', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', '[ইমেইল]', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def is_safe_content(self, text: str) -> bool:
        """কন্টেন্ট সেফ কিনা চেক করে"""
        # Check minimum length
        if len(text) < Config.MIN_INPUT_LENGTH:
            return False
        
        # Check for only numbers
        if text.replace(' ', '').isdigit():
            return False
        
        # Check for only emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
                           "]+", flags=re.UNICODE)
        
        if emoji_pattern.fullmatch(text):
            return False
        
        # Check for only special characters
        if re.match(r'^[^\w\u0980-\u09FF]+$', text):
            return False
        
        return True
    
    def contains_disallowed_content(self, text: str) -> bool:
        """ডিসঅ্যালোয়েড কন্টেন্ট আছে কিনা চেক করে"""
        if not self.disallowed_words:
            return False
        
        text_lower = text.lower()
        for word in self.disallowed_words:
            if word and word.strip() and word.strip() in text_lower:
                logger.warning(f"Disallowed word detected: {word}")
                return True
        
        return False
    
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
    
    def detect_spam_patterns(self, text: str) -> List[str]:
        """স্প্যাম প্যাটার্ন ডিটেক্ট করে"""
        detected = []
        
        for pattern, pattern_name in self.spam_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.UNICODE):
                detected.append(pattern_name)
        
        return detected
    
    def detect_personal_info(self, text: str) -> List[str]:
        """পার্সোনাল ইনফো ডিটেক্ট করে"""
        detected = []
        
        for pattern, info_type in self.personal_info_patterns:
            if re.search(pattern, text):
                detected.append(info_type)
        
        return detected
    
    def filter_personal_info(self, text: str) -> str:
        """পার্সোনাল ইনফো ফিল্টার করে"""
        filtered = text
        
        for pattern, info_type in self.personal_info_patterns:
            if info_type == "phone_number":
                filtered = re.sub(pattern, '[ফোন নম্বর]', filtered)
            elif info_type == "email_address":
                filtered = re.sub(pattern, '[ইমেইল]', filtered)
            elif info_type == "id_number":
                filtered = re.sub(pattern, '[আইডি]', filtered)
        
        return filtered
    
    def analyze_message_safety(self, text: str, user_id: int) -> Dict[str, Any]:
        """মেসেজ সেফটি অ্যানালাইসিস করে"""
        analysis = {
            "is_safe": True,
            "warnings": [],
            "score": 100,
            "actions": []
        }
        
        # Check basic safety
        if not self.is_safe_content(text):
            analysis["is_safe"] = False
            analysis["warnings"].append("content_not_safe")
            analysis["score"] -= 30
        
        # Check disallowed words
        if self.contains_disallowed_content(text):
            analysis["is_safe"] = False
            analysis["warnings"].append("disallowed_content")
            analysis["score"] -= 40
            analysis["actions"].append("warn_user")
        
        # Check spam patterns
        spam_patterns = self.detect_spam_patterns(text)
        if spam_patterns:
            analysis["warnings"].extend([f"spam_{p}" for p in spam_patterns])
            analysis["score"] -= len(spam_patterns) * 10
            if len(spam_patterns) > 1:
                analysis["actions"].append("cooldown")
        
        # Check personal info
        personal_info = self.detect_personal_info(text)
        if personal_info:
            analysis["warnings"].extend([f"personal_{p}" for p in personal_info])
            analysis["score"] -= len(personal_info) * 20
            analysis["actions"].append("filter_content")
        
        # Update user safety score
        self._update_user_safety_score(user_id, analysis["score"])
        
        # Check if user is suspicious
        if analysis["score"] < 50:
            self.suspicious_users.add(user_id)
            analysis["actions"].append("monitor_user")
        
        return analysis
    
    def _update_user_safety_score(self, user_id: int, message_score: int):
        """ইউজার সেফটি স্কোর আপডেট করে"""
        if user_id not in self.user_safety_score:
            self.user_safety_score[user_id] = {
                "total_score": 0,
                "message_count": 0,
                "average_score": 100,
                "last_warning": None
            }
        
        user_data = self.user_safety_score[user_id]
        user_data["total_score"] += message_score
        user_data["message_count"] += 1
        user_data["average_score"] = user_data["total_score"] / user_data["message_count"]
        
        # Remove from suspicious if score improves
        if user_id in self.suspicious_users and user_data["average_score"] > 70:
            self.suspicious_users.remove(user_id)
    
    def get_user_safety_report(self, user_id: int) -> Dict[str, Any]:
        """ইউজার সেফটি রিপোর্ট রিটার্ন করে"""
        if user_id not in self.user_safety_score:
            return {
                "user_id": user_id,
                "has_data": False,
                "average_score": 100,
                "is_suspicious": False,
                "message_count": 0
            }
        
        user_data = self.user_safety_score[user_id]
        
        return {
            "user_id": user_id,
            "has_data": True,
            "average_score": user_data["average_score"],
            "message_count": user_data["message_count"],
            "is_suspicious": user_id in self.suspicious_users,
            "last_warning": user_data.get("last_warning"),
            "needs_monitoring": user_data["average_score"] < 60
        }
    
    def reset_user_safety_score(self, user_id: int) -> bool:
        """ইউজার সেফটি স্কোর রিসেট করে"""
        if user_id in self.user_safety_score:
            del self.user_safety_score[user_id]
        
        if user_id in self.suspicious_users:
            self.suspicious_users.remove(user_id)
        
        logger.info(f"Reset safety score for user {user_id}")
        return True
    
    def export_safety_data(self) -> Dict[str, Any]:
        """সেফটি ডাটা এক্সপোর্ট করে"""
        return {
            "total_users_tracked": len(self.user_safety_score),
            "suspicious_users": len(self.suspicious_users),
            "disallowed_words_count": len(self.disallowed_words),
            "avg_safety_score": self._calculate_average_safety_score(),
            "safety_stats": self._calculate_safety_stats()
        }
    
    def _calculate_average_safety_score(self) -> float:
        """গড় সেফটি স্কোর ক্যালকুলেট করে"""
        if not self.user_safety_score:
            return 100.0
        
        total_score = sum(data["average_score"] for data in self.user_safety_score.values())
        return total_score / len(self.user_safety_score)
    
    def _calculate_safety_stats(self) -> Dict[str, int]:
        """সেফটি স্ট্যাটস ক্যালকুলেট করে"""
        stats = {
            "excellent": 0,  # 90-100
            "good": 0,       # 70-89
            "fair": 0,       # 50-69
            "poor": 0,       # 30-49
            "critical": 0    # 0-29
        }
        
        for user_data in self.user_safety_score.values():
            score = user_data["average_score"]
            
            if score >= 90:
                stats["excellent"] += 1
            elif score >= 70:
                stats["good"] += 1
            elif score >= 50:
                stats["fair"] += 1
            elif score >= 30:
                stats["poor"] += 1
            else:
                stats["critical"] += 1
        
        return stats
    
    def cleanup_old_data(self, days: int = 30):
        """পুরানো ডাটা ক্লিনআপ করে"""
        # This would cleanup old user data in production
        # For now, just log
        logger.info(f"Safety data cleanup scheduled for {days} days")
        
        # Simple cleanup: remove users with very old data
        # In production, you would track timestamps
        
        current_time = TimeManager.get_current_time()
        logger.info(f"Safety system cleanup at {current_time}")

# Global instance
safety_checker = SafetyChecker()
