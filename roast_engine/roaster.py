import random
from typing import Dict, List, Tuple, Optional
from config import Config
from utils.text_processor import TextProcessor
from utils.logger import logger
from roast_engine.safety_check import SafetyChecker

class RoastEngine:
    def __init__(self):
        self.roast_templates = self._load_roast_templates()
        self.safety_checker = SafetyChecker()
        
    def _load_roast_templates(self) -> Dict:
        """রোস্ট টেমপ্লেট লোড করে"""
        return {
            "sentence_logic": {
                "primary": [
                    "এই লজিক তো আগে কখনো শুনি নাই!",
                    "বুঝলাম... মানে কিছুই বুঝলাম না!",
                    "এই কথার কোনো মানে হয় নাকি?"
                ],
                "secondary": [
                    "আবার চেষ্টা করো হয়তো একদিন পারবে!",
                    "লজিকের থেকে ফ্যান্টাসি বেশি মনে হয়!",
                    "একটু সোজা করে বলো বুঝি না!"
                ]
            },
            "overconfidence": {
                "primary": [
                    "আহা কত বড় হইয়া গেছস!",
                    "এই আত্মবিশ্বাসের ঠিকানা কি?"
                ],
                "secondary": [
                    "থামো, পৃথিবীটা ঘুরছে না তোমার চারপাশে!",
                    "একটু নিচে নেমে আসো, উপরে ঠান্ডা লাগবে!"
                ]
            },
            "common_lies": {
                "primary": [
                    "এই গল্পটা আগেও শুনেছি!",
                    "সত্যি বলতে এতটাও বিশ্বাসযোগ্য না!"
                ],
                "secondary": [
                    "চলো আরেকটা গল্প বলো!",
                    "এই এপিসোড আগেই দেখেছি!"
                ]
            },
            "daily_habits": {
                "primary": [
                    "এটা তো তোমার ডেইলি রুটিন!",
                    "নতুন কিছু করলে হতো!"
                ],
                "secondary": [
                    "বদলাও, জীবন বদলে যাবে!",
                    "একঘেয়েমি দূর করো!"
                ]
            },
            "self_claims": {
                "primary": [
                    "হুম, ঠিক বলেছ! (না)",
                    "নিজেকে কত বড় ভাবস!"
                ],
                "secondary": [
                    "বাস্তবতার মুখোমুখি হও!",
                    "আয়নায় একবার দেখো!"
                ]
            }
        }
    
    def generate_roast(self, text: str, user_id: int) -> Dict[str, str]:
        """ইনপুট টেক্সট থেকে রোস্ট জেনারেট করে"""
        try:
            # Sanitize and validate
            text = self.safety_checker.sanitize_input(text)
            
            if not self.safety_checker.is_safe_content(text):
                return self._get_safe_fallback_roast()
            
            # Detect roast category
            category = self._detect_roast_category(text)
            
            # Select templates based on category
            if category in self.roast_templates:
                primary = random.choice(self.roast_templates[category]["primary"])
                secondary = random.choice(self.roast_templates[category]["secondary"])
            else:
                primary = random.choice(self.roast_templates["sentence_logic"]["primary"])
                secondary = random.choice(self.roast_templates["sentence_logic"]["secondary"])
            
            # Add emoji based on mood
            mood = TextProcessor.analyze_mood(text)
            emoji = self._select_emoji(mood)
            
            # Format final roast
            primary_with_emoji = f"{primary} {emoji}"
            
            return {
                "primary": primary_with_emoji,
                "secondary": secondary,
                "category": category,
                "emoji": emoji,
                "mood_intensity": mood["intensity"]
            }
            
        except Exception as e:
            logger.error(f"Error generating roast: {e}")
            return self._get_safe_fallback_roast()
    
    def _detect_roast_category(self, text: str) -> str:
        """রোস্ট ক্যাটাগরি ডিটেক্ট করে"""
        text_lower = text.lower()
        
        # Logic-based detection
        if any(word in text_lower for word in ["হবে", "করব", "পারব", "জানি", "বুঝি"]):
            return "overconfidence"
        
        if any(word in text_lower for word in ["মিথ্যা", "মিথ্যে", "লাই", "ভুল"]):
            return "common_lies"
        
        if any(word in text_lower for word in ["রোজ", "প্রতিদিন", "সকাল", "রাত"]):
            return "daily_habits"
        
        if any(word in text_lower for word in ["আমি", "আমার", "আমাকে"]):
            return "self_claims"
        
        return "sentence_logic"
    
    def _select_emoji(self, mood: Dict) -> str:
        """মুড ভিত্তিতে ইমোজি সিলেক্ট করে"""
        intensity = mood["intensity"]
        
        if intensity > 7:
            return "💀"
        elif intensity > 4:
            return "🔥"
        elif mood["has_emojis"]:
            return "😏"
        else:
            return "😂"
    
    def _get_safe_fallback_roast(self) -> Dict[str, str]:
        """সেফ ফলব্যাক রোস্ট রিটার্ন করে"""
        return {
            "primary": "তুমি তো মজার! 😄",
            "secondary": "চলো আবার চেষ্টা করো!",
            "category": "neutral",
            "emoji": "😄",
            "mood_intensity": 3
        }
    
    def generate_targeted_roast(self, target_name: str, sender_name: str = None) -> Dict[str, str]:
        """টার্গেটেড রোস্ট জেনারেট করে (গ্রুপে মেনশনের জন্য)"""
        templates = [
            {
                "primary": f"{target_name} এর অবস্থা কী? 😏",
                "secondary": "কিছু বলার আছে নাকি?"
            },
            {
                "primary": f"{target_name} কে ডাকাডাকি কেন? 🤔",
                "secondary": "নিজের কাজ দেখো!"
            },
            {
                "primary": f"এই যে {target_name} এসেছে! 👀",
                "secondary": "কী বলবে বলো!"
            }
        ]
        
        if sender_name:
            templates.append({
                "primary": f"{sender_name} {target_name} কে ডেকেছে! 😄",
                "secondary": "এখন কী হবে?"
            })
        
        roast = random.choice(templates)
        roast["category"] = "targeted"
        roast["emoji"] = "😄"
        
        return roast
