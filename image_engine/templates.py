import json
import random
from typing import Dict, List, Any, Tuple
from pathlib import Path
from config import Config
from utils.time_manager import TimeManager
from utils.logger import logger

class TemplateManager:
    def __init__(self):
        self.templates_file = Path(Config.TEMPLATES_PATH) / "templates.json"
        self.templates = self._load_templates()
        self.used_templates = {}  # Track recent usage per user
        self.template_stats = {}
        
    def _load_templates(self) -> Dict:
        """টেমপ্লেট ফাইল লোড করে"""
        try:
            if self.templates_file.exists():
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Templates file not found, creating default")
                return self._create_default_templates()
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            return self._create_default_templates()
    
    def _create_default_templates(self) -> Dict:
        """ডিফল্ট টেমপ্লেট তৈরি করে"""
        default_templates = {
            "templates": {
                "cartoon_roast": [
                    {
                        "id": "cartoon_1",
                        "name": "Cartoon Funny",
                        "background": "cartoon_bg_1.png",
                        "font": "comic.ttf",
                        "primary_color": (255, 105, 180),
                        "secondary_color": (0, 0, 0),
                        "font_size": 60,
                        "sub_font_size": 30,
                        "position": {"x": 540, "y": 400},
                        "sub_position": {"x": 540, "y": 500},
                        "effects": ["shadow", "outline"]
                    },
                    {
                        "id": "cartoon_2",
                        "name": "Cartoon Bubble",
                        "background": "cartoon_bg_2.png",
                        "font": "bubble.ttf",
                        "primary_color": (41, 128, 185),
                        "secondary_color": (255, 255, 255),
                        "font_size": 55,
                        "sub_font_size": 28,
                        "position": {"x": 540, "y": 380},
                        "sub_position": {"x": 540, "y": 480},
                        "effects": ["glow", "shadow"]
                    }
                ],
                "neon_savage": [
                    {
                        "id": "neon_1",
                        "name": "Neon Red",
                        "background": "neon_bg_1.png",
                        "font": "neon.ttf",
                        "primary_color": (255, 0, 100),
                        "secondary_color": (0, 255, 255),
                        "font_size": 65,
                        "sub_font_size": 32,
                        "position": {"x": 540, "y": 420},
                        "sub_position": {"x": 540, "y": 520},
                        "effects": ["glow", "blur"]
                    }
                ],
                "dark_sarcastic": [
                    {
                        "id": "dark_1",
                        "name": "Dark Humor",
                        "background": "dark_bg_1.png",
                        "font": "gothic.ttf",
                        "primary_color": (200, 200, 200),
                        "secondary_color": (100, 100, 100),
                        "font_size": 58,
                        "sub_font_size": 29,
                        "position": {"x": 540, "y": 410},
                        "sub_position": {"x": 540, "y": 510},
                        "effects": ["shadow", "gradient"]
                    }
                ]
            },
            "total_templates": 50,
            "unlocked_templates": ["cartoon_1", "cartoon_2", "neon_1", "dark_1"]
        }
        
        # Save default templates
        self.templates_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(default_templates, f, indent=2, ensure_ascii=False)
        
        return default_templates
    
    def get_template(self, user_id: int, roast_type: str = None) -> Dict[str, Any]:
        """ইউজারের জন্য উপযুক্ত টেমপ্লেট সিলেক্ট করে"""
        # Get available categories based on time
        if TimeManager.is_day_time():
            preferred_categories = ["cartoon_roast", "minimal_mock"]
        else:
            preferred_categories = ["neon_savage", "dark_sarcastic", "poster_style"]
        
        # Filter by roast type if provided
        if roast_type and roast_type in self.templates["templates"]:
            available_templates = self.templates["templates"][roast_type]
        else:
            # Combine templates from preferred categories
            available_templates = []
            for category in preferred_categories:
                if category in self.templates["templates"]:
                    available_templates.extend(self.templates["templates"][category])
        
        if not available_templates:
            # Fallback to any template
            for category in self.templates["templates"].values():
                available_templates.extend(category)
        
        # Filter out recently used templates for this user
        user_key = str(user_id)
        if user_key in self.used_templates:
            recent_templates = self.used_templates[user_key]
            available_templates = [t for t in available_templates if t["id"] not in recent_templates]
        
        # If no templates available, clear user's recent list
        if not available_templates and user_key in self.used_templates:
            self.used_templates[user_key] = []
            available_templates = []
            for category in self.templates["templates"].values():
                available_templates.extend(category)
        
        # Select random template
        selected_template = random.choice(available_templates) if available_templates else {}
        
        # Update recent templates for user
        if user_key not in self.used_templates:
            self.used_templates[user_key] = []
        
        self.used_templates[user_key].append(selected_template.get("id", ""))
        
        # Keep only last 5 templates
        if len(self.used_templates[user_key]) > 5:
            self.used_templates[user_key] = self.used_templates[user_key][-5:]
        
        return selected_template
    
    def unlock_template(self, template_id: str) -> bool:
        """টেমপ্লেট আনলক করে"""
        if template_id not in self.templates["unlocked_templates"]:
            self.templates["unlocked_templates"].append(template_id)
            return self._save_templates()
        return False
    
    def _save_templates(self) -> bool:
        """টেমপ্লেট ফাইল সেভ করে"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving templates: {e}")
            return False
    
    def get_template_stats(self, template_id: str) -> Dict:
        """টেমপ্লেট স্ট্যাট রিটার্ন করে"""
        return self.template_stats.get(template_id, {
            "usage_count": 0,
            "funny_votes": 0,
            "mid_votes": 0,
            "savage_votes": 0
        })
    
    def get_all_categories(self) -> List[str]:
        """সকল ক্যাটাগরি লিস্ট রিটার্ন করে"""
        return list(self.templates["templates"].keys())