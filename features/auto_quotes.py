import random
from datetime import datetime
from typing import Dict, List
from telegram.ext import ContextTypes
from config import Config
from utils.logger import logger
from utils.time_manager import TimeManager
from database.storage import StorageManager
from image_engine.image_generator import ImageGenerator

class AutoQuoteSystem:
    def __init__(self):
        self.image_generator = ImageGenerator()
        self.quotes = self._load_quotes()
        self.last_posted = {}  # chat_id -> last_post_time
    
    def _load_quotes(self) -> Dict[str, List[Dict]]:
        """কোটস লোড করে"""
        return {
            "roast_quotes": [
                {
                    "text": "তোমার আইডিয়াগুলো তো কনফিউজনের নতুন লেভেল! 😅",
                    "author": "রোস্টিফাই বট",
                    "category": "funny"
                },
                {
                    "text": "কথা বলতে পারা আর কথা বলা - দুটো আলাদা জিনিস! 😏",
                    "author": "রোস্টিফাই বট",
                    "category": "sarcastic"
                },
                {
                    "text": "তোমার লজিক দেখে আইনস্টাইনও কাঁদতেন! 😂",
                    "author": "রোস্টিফাই বট", 
                    "category": "funny"
                },
                {
                    "text": "আত্মবিশ্বাস ভালো, কিন্তু reality checkও দরকার! 💀",
                    "author": "রোস্টিফাই বট",
                    "category": "savage"
                }
            ],
            "motivational": [
                {
                    "text": "ব্যর্থতা সাফল্যের প্রথম ধাপ! 💪",
                    "author": "অজানা",
                    "category": "motivation"
                },
                {
                    "text": "চেষ্টা করলে কোনদিন না কোনদিন সফল হবেই! 🚀",
                    "author": "অজানা",
                    "category": "motivation"
                }
            ],
            "funny": [
                {
                    "text": "জীবনটা শর্ট, রোস্ট লং! 😈",
                    "author": "রোস্টিফাই বট",
                    "category": "funny"
                },
                {
                    "text": "আমি রোস্ট করি, তুমি হাসো - ফেয়ার ডিল! 😄",
                    "author": "রোস্টিফাই বট",
                    "category": "funny"
                }
            ]
        }
    
    async def post_daily_quote(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int = None):
        """ডেইলি কোট পোস্ট করে"""
        try:
            # Select quote category based on time
            if TimeManager.is_day_time():
                category = "motivational"
            else:
                category = "roast_quotes"
            
            # Get random quote
            if category in self.quotes and self.quotes[category]:
                quote = random.choice(self.quotes[category])
            else:
                # Fallback to any quote
                all_quotes = []
                for cat_quotes in self.quotes.values():
                    all_quotes.extend(cat_quotes)
                quote = random.choice(all_quotes) if all_quotes else self._get_fallback_quote()
            
            # Create quote image
            image = self._create_quote_image(quote)
            image_path = self.image_generator.save_image(
                image, 
                f"quote_{datetime.now().strftime('%Y%m%d')}.png"
            )
            
            caption = f"📜 ডেইলি কোট\n\n{quote['text']}\n\n- {quote['author']}"
            
            with open(image_path, 'rb') as photo:
                if chat_id:
                    # Post to specific chat
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=caption
                    )
                    self.last_posted[chat_id] = TimeManager.get_current_time()
                    logger.info(f"Posted daily quote to chat {chat_id}")
                else:
                    # Post to all active chats (would need chat list from database)
                    logger.info("No specific chat provided for daily quote")
            
            return True
            
        except Exception as e:
            logger.error(f"Error posting daily quote: {e}")
            return False
    
    def _create_quote_image(self, quote: Dict) -> Image.Image:
        """কোট ইমেজ তৈরি করে"""
        # Use image generator with special quote template
        primary_text = quote["text"]
        secondary_text = f"- {quote['author']}"
        
        image = self.image_generator.create_roast_image(
            primary_text=primary_text,
            secondary_text=secondary_text,
            user_id=0  # Special ID for quotes
        )
        
        return image
    
    def _get_fallback_quote(self) -> Dict:
        """ফলব্যাক কোট রিটার্ন করে"""
        return {
            "text": "রোস্টের মজা অন্যরকম! 😏",
            "author": "রোস্টিফাই বট",
            "category": "funny"
        }
    
    async def post_special_quote(self, context: ContextTypes.DEFAULT_TYPE, 
                                chat_id: int, occasion: str):
        """স্পেশাল অকেশনের কোট পোস্ট করে"""
        occasion_quotes = {
            "new_year": {
                "text": "নতুন বছর, নতুন রোস্ট! 🎊",
                "author": "রোস্টিফাই বট",
                "category": "celebration"
            },
            "pohela_boishakh": {
                "text": "শুভ নববর্ষ! রোস্টের মেজাজে! 🎉",
                "author": "রোস্টিফাই বট",
                "category": "celebration"
            },
            "halloween": {
                "text": "হ্যালোইন স্পেশাল: ভূতের মতো রোস্ট! 👻",
                "author": "রোস্টিফাই বট",
                "category": "funny"
            },
            "eid": {
                "text": "ঈদ মোবারক! আজ রোস্টে ছাড়! 😊",
                "author": "রোস্টিফাই বট",
                "category": "celebration"
            }
        }
        
        if occasion not in occasion_quotes:
            return False
        
        try:
            quote = occasion_quotes[occasion]
            image = self._create_quote_image(quote)
            image_path = self.image_generator.save_image(image)
            
            caption = f"🎉 {occasion.replace('_', ' ').title()} স্পেশাল!\n\n{quote['text']}"
            
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption
                )
            
            logger.info(f"Posted {occasion} quote to chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error posting special quote: {e}")
            return False
    
    def should_post_daily_quote(self, chat_id: int) -> bool:
        """ডেইলি কোট পোস্ট করা উচিত কিনা চেক করে"""
        if chat_id not in self.last_posted:
            return True
        
        last_post = self.last_posted[chat_id]
        time_diff = (TimeManager.get_current_time() - last_post).total_seconds()
        
        # Post once per day (86400 seconds)
        return time_diff >= 86400
    
    async def get_quote_stats(self) -> Dict:
        """কোট স্ট্যাট রিটার্ন করে"""
        total_quotes = sum(len(quotes) for quotes in self.quotes.values())
        
        return {
            "total_quotes": total_quotes,
            "categories": list(self.quotes.keys()),
            "last_posted_chats": len(self.last_posted),
            "todays_quote": None  # Would be today's quote
        }