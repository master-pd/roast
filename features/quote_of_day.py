"""
Advanced Quote of the Day System with Database Support
Author: RoastifyBot Team
Version: 2.0.0
"""

import asyncio
import random
import json
import os
import aiofiles
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
import pytz
from dataclasses import dataclass
from collections import defaultdict

try:
    from bson import ObjectId
    HAS_MONGO = True
except ImportError:
    HAS_MONGO = False

# ==================== DATA CLASSES ====================

@dataclass
class Quote:
    """Quote data structure"""
    id: str
    text: str
    author: str
    category: str
    language: str
    tags: List[str]
    popularity: int
    used_count: int
    last_used: Optional[datetime]
    created_at: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'text': self.text,
            'author': self.author,
            'category': self.category,
            'language': self.language,
            'tags': self.tags,
            'popularity': self.popularity,
            'used_count': self.used_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Quote':
        """Create from dictionary"""
        return cls(
            id=data.get('id', str(ObjectId()) if HAS_MONGO else str(random.randint(1000, 9999))),
            text=data['text'],
            author=data.get('author', 'Unknown'),
            category=data.get('category', 'general'),
            language=data.get('language', 'bn'),
            tags=data.get('tags', []),
            popularity=data.get('popularity', 0),
            used_count=data.get('used_count', 0),
            last_used=datetime.fromisoformat(data['last_used']) if data.get('last_used') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        )


@dataclass
class UserQuoteHistory:
    """User quote history"""
    user_id: str
    quotes_seen: List[str]
    favorite_quotes: List[str]
    last_seen: Optional[datetime]
    streak_days: int
    total_quotes: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'quotes_seen': self.quotes_seen,
            'favorite_quotes': self.favorite_quotes,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'streak_days': self.streak_days,
            'total_quotes': self.total_quotes
        }


class QuoteCategory(Enum):
    """Quote categories"""
    MOTIVATIONAL = "motivational"
    FUNNY = "funny"
    LOVE = "love"
    WISDOM = "wisdom"
    LIFE = "life"
    SUCCESS = "success"
    FRIENDSHIP = "friendship"
    INSPIRATIONAL = "inspirational"
    SPIRITUAL = "spiritual"
    PHILOSOPHY = "philosophy"
    EDUCATION = "education"
    BUSINESS = "business"
    HEALTH = "health"
    TECHNOLOGY = "technology"


class QuoteLanguage(Enum):
    """Supported languages"""
    BANGLA = "bn"
    ENGLISH = "en"
    HINDI = "hi"
    ARABIC = "ar"
    URDU = "ur"


# ==================== DEFAULT QUOTES DATABASE ====================

DEFAULT_QUOTES_BANGLA = [
    {
        "text": "যে নিজের উপর বিশ্বাস রাখে, পৃথিবী তার পায়ে নত হয়।",
        "author": "স্বামী বিবেকানন্দ",
        "category": "motivational",
        "language": "bn",
        "tags": ["বিশ্বাস", "সাফল্য", "আত্মবিশ্বাস"]
    },
    {
        "text": "হাসতে হাসতে জীবন কাটাও, কারণ জীবনের প্রতিটি মুহূর্তই বিশেষ।",
        "author": "অজানা",
        "category": "life",
        "language": "bn",
        "tags": ["জীবন", "হাসি", "আনন্দ"]
    },
    {
        "text": "পরিশ্রম সৌভাগ্যের প্রসূতি।",
        "author": "প্রবাদ",
        "category": "success",
        "language": "bn",
        "tags": ["পরিশ্রম", "সাফল্য", "অধ্যবসায়"]
    },
    {
        "text": "ভালোবাসা কোন কথা নয়, এটি একটি অনুভূতি যা হৃদয় দিয়ে বুঝতে হয়।",
        "author": "রবীন্দ্রনাথ ঠাকুর",
        "category": "love",
        "language": "bn",
        "tags": ["ভালোবাসা", "হৃদয়", "অনুভূতি"]
    },
    {
        "text": "জ্ঞানী ব্যক্তি সবসময় শেখে, অজ্ঞানী সবসময় শিক্ষা দেয়।",
        "author": "বাংলা প্রবাদ",
        "category": "wisdom",
        "language": "bn",
        "tags": ["জ্ঞান", "শিক্ষা", "বুদ্ধিমত্তা"]
    },
    {
        "text": "সময়ের এক ফোঁড়, অন时间的十针",
        "author": "বাংলা প্রবাদ",
        "category": "life",
        "language": "bn",
        "tags": ["সময়", "মূল্য", "জীবন"]
    },
    {
        "text": "মিতব্যয়ী ধনী, অপব্যয়ী দরিদ্র।",
        "author": "প্রবাদ",
        "category": "business",
        "language": "bn",
        "tags": ["সঞ্চয়", "অর্থ", "বুদ্ধিমত্তা"]
    },
    {
        "text": "স্বাস্থ্যই সম্পদ",
        "author": "প্রবাদ",
        "category": "health",
        "language": "bn",
        "tags": ["স্বাস্থ্য", "সম্পদ", "জীবন"]
    },
    {
        "text": "বন্ধুত্ব হৃদয়ের কথা, মুখের নয়।",
        "author": "অজানা",
        "category": "friendship",
        "language": "bn",
        "tags": ["বন্ধুত্ব", "হৃদয়", "আন্তরিকতা"]
    },
    {
        "text": "প্রতিটি ব্যর্থতা সাফল্যের দিকে একটি পদক্ষেপ।",
        "author": "টমাস এডিসন",
        "category": "inspirational",
        "language": "bn",
        "tags": ["ব্যর্থতা", "সাফল্য", "অধ্যবসায়"]
    }
]

DEFAULT_QUOTES_ENGLISH = [
    {
        "text": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs",
        "category": "motivational",
        "language": "en",
        "tags": ["work", "passion", "success"]
    },
    {
        "text": "Life is what happens to you while you're busy making other plans.",
        "author": "John Lennon",
        "category": "life",
        "language": "en",
        "tags": ["life", "plans", "reality"]
    },
    {
        "text": "The future belongs to those who believe in the beauty of their dreams.",
        "author": "Eleanor Roosevelt",
        "category": "inspirational",
        "language": "en",
        "tags": ["future", "dreams", "belief"]
    },
    {
        "text": "Be the change that you wish to see in the world.",
        "author": "Mahatma Gandhi",
        "category": "inspirational",
        "language": "en",
        "tags": ["change", "world", "action"]
    }
]

# ==================== MAIN QUOTE CLASS ====================

class QuoteOfDay:
    """
    Advanced Quote of the Day System
    Features:
    - Daily quotes with caching
    - Multi-language support
    - User preferences
    - Statistics and analytics
    - Streak tracking
    - Favorite quotes
    - Category-based filtering
    """
    
    def __init__(self, bot):
        """
        Initialize Quote of the Day System
        
        Args:
            bot: Main bot instance
        """
        self.bot = bot
        self.logger = bot.logger
        self.config = getattr(bot, 'config', {})
        
        # Paths
        self.data_dir = "data/quotes"
        self.quotes_file = os.path.join(self.data_dir, "quotes.json")
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.stats_file = os.path.join(self.data_dir, "stats.json")
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Data storage
        self.quotes: Dict[str, Quote] = {}
        self.user_data: Dict[str, UserQuoteHistory] = {}
        self.daily_cache: Dict[str, Dict] = {}  # date -> quote data
        self.stats: Dict = {}
        
        # Settings
        self.timezone = pytz.timezone('Asia/Dhaka')
        self.daily_reset_hour = 6  # 6 AM Bangladesh time
        
        # Load data
        self.load_data()
        
        # Initialize default quotes if empty
        if not self.quotes:
            self.initialize_default_quotes()
        
        self.logger.info(f"✅ QuoteOfDay initialized with {len(self.quotes)} quotes")
    
    # ==================== DATA MANAGEMENT ====================
    
    def load_data(self):
        """Load quotes and user data from files"""
        try:
            # Load quotes
            if os.path.exists(self.quotes_file):
                with open(self.quotes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quotes = {qid: Quote.from_dict(qdata) for qid, qdata in data.items()}
            
            # Load user data
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_data = {
                        uid: UserQuoteHistory(
                            user_id=uid,
                            quotes_seen=udata.get('quotes_seen', []),
                            favorite_quotes=udata.get('favorite_quotes', []),
                            last_seen=datetime.fromisoformat(udata['last_seen']) if udata.get('last_seen') else None,
                            streak_days=udata.get('streak_days', 0),
                            total_quotes=udata.get('total_quotes', 0)
                        )
                        for uid, udata in data.items()
                    }
            
            # Load stats
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
                    
        except Exception as e:
            self.logger.error(f"❌ Error loading quote data: {e}")
            self.quotes = {}
            self.user_data = {}
            self.stats = {}
    
    async def save_data(self):
        """Save quotes and user data to files"""
        try:
            # Save quotes
            quotes_dict = {qid: quote.to_dict() for qid, quote in self.quotes.items()}
            async with aiofiles.open(self.quotes_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(quotes_dict, ensure_ascii=False, indent=2))
            
            # Save user data
            users_dict = {uid: data.to_dict() for uid, data in self.user_data.items()}
            async with aiofiles.open(self.users_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(users_dict, ensure_ascii=False, indent=2))
            
            # Save stats
            async with aiofiles.open(self.stats_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(self.stats, ensure_ascii=False, indent=2))
                
        except Exception as e:
            self.logger.error(f"❌ Error saving quote data: {e}")
    
    def initialize_default_quotes(self):
        """Initialize with default quotes"""
        all_defaults = DEFAULT_QUOTES_BANGLA + DEFAULT_QUOTES_ENGLISH
        
        for idx, quote_data in enumerate(all_defaults):
            quote_id = f"default_{idx + 1:04d}"
            quote = Quote(
                id=quote_id,
                text=quote_data['text'],
                author=quote_data['author'],
                category=quote_data['category'],
                language=quote_data['language'],
                tags=quote_data.get('tags', []),
                popularity=0,
                used_count=0,
                last_used=None,
                created_at=datetime.now()
            )
            self.quotes[quote_id] = quote
        
        self.logger.info(f"📚 Loaded {len(all_defaults)} default quotes")
    
    # ==================== QUOTE OPERATIONS ====================
    
    def add_quote(self, text: str, author: str = "Unknown", 
                  category: str = "general", language: str = "bn",
                  tags: List[str] = None) -> str:
        """
        Add a new quote
        
        Args:
            text: Quote text
            author: Quote author
            category: Quote category
            language: Language code
            tags: List of tags
        
        Returns:
            Quote ID
        """
        quote_id = f"user_{len(self.quotes) + 1:06d}"
        
        quote = Quote(
            id=quote_id,
            text=text,
            author=author,
            category=category,
            language=language,
            tags=tags or [],
            popularity=0,
            used_count=0,
            last_used=None,
            created_at=datetime.now()
        )
        
        self.quotes[quote_id] = quote
        self.logger.info(f"➕ Added new quote: {quote_id}")
        
        # Auto-save in background
        asyncio.create_task(self.save_data())
        
        return quote_id
    
    def get_quote(self, quote_id: str) -> Optional[Quote]:
        """Get quote by ID"""
        return self.quotes.get(quote_id)
    
    def delete_quote(self, quote_id: str) -> bool:
        """Delete a quote"""
        if quote_id in self.quotes:
            del self.quotes[quote_id]
            self.logger.info(f"🗑️ Deleted quote: {quote_id}")
            asyncio.create_task(self.save_data())
            return True
        return False
    
    def search_quotes(self, query: str, language: str = None, 
                      category: str = None, limit: int = 10) -> List[Quote]:
        """
        Search quotes
        
        Args:
            query: Search query
            language: Filter by language
            category: Filter by category
            limit: Maximum results
        
        Returns:
            List of matching quotes
        """
        results = []
        query_lower = query.lower()
        
        for quote in self.quotes.values():
            # Apply filters
            if language and quote.language != language:
                continue
            if category and quote.category != category:
                continue
            
            # Search in text, author, and tags
            if (query_lower in quote.text.lower() or 
                query_lower in quote.author.lower() or
                any(query_lower in tag.lower() for tag in quote.tags)):
                results.append(quote)
        
        # Sort by popularity
        results.sort(key=lambda x: x.popularity, reverse=True)
        
        return results[:limit]
    
    # ==================== DAILY QUOTE SYSTEM ====================
    
    def get_today_date(self) -> str:
        """Get today's date string in Bangladesh time"""
        now = datetime.now(self.timezone)
        return now.strftime("%Y-%m-%d")
    
    def get_daily_quote(self, user_id: str = None, 
                        language: str = "bn",
                        category: str = None) -> Dict:
        """
        Get quote of the day
        
        Args:
            user_id: User ID for personalization
            language: Preferred language
            category: Preferred category
        
        Returns:
            Quote data dictionary
        """
        today = self.get_today_date()
        
        # Check cache
        cache_key = f"{today}_{language}_{category}"
        if cache_key in self.daily_cache:
            cached = self.daily_cache[cache_key]
            self._update_user_history(user_id, cached['id'])
            return cached
        
        # Filter quotes by language and category
        filtered_quotes = [
            quote for quote in self.quotes.values()
            if quote.language == language and 
            (category is None or quote.category == category)
        ]
        
        if not filtered_quotes:
            # Fallback to any language
            filtered_quotes = list(self.quotes.values())
        
        # Select quote (weighted by popularity and recency)
        selected = self._select_quote(filtered_quotes, user_id)
        
        # Update quote stats
        selected.used_count += 1
        selected.last_used = datetime.now()
        selected.popularity += 1
        
        # Update user history
        self._update_user_history(user_id, selected.id)
        
        # Prepare response
        result = {
            'id': selected.id,
            'text': selected.text,
            'author': selected.author,
            'category': selected.category,
            'language': selected.language,
            'date': today,
            'tags': selected.tags,
            'popularity': selected.popularity
        }
        
        # Cache for today
        self.daily_cache[cache_key] = result
        
        # Save data in background
        asyncio.create_task(self.save_data())
        
        self.logger.info(f"📖 Daily quote served: {selected.id} to user {user_id}")
        
        return result
    
    def _select_quote(self, quotes: List[Quote], user_id: str = None) -> Quote:
        """Select a quote using smart algorithm"""
        if not quotes:
            return Quote(
                id="default",
                text="জীবন সুন্দর, হাসতে থাকো!",
                author="RoastifyBot",
                category="general",
                language="bn",
                tags=[],
                popularity=0,
                used_count=0,
                last_used=None,
                created_at=datetime.now()
            )
        
        # Get user's seen quotes
        seen_quotes = set()
        if user_id and user_id in self.user_data:
            seen_quotes = set(self.user_data[user_id].quotes_seen)
        
        # Filter unseen quotes
        unseen_quotes = [q for q in quotes if q.id not in seen_quotes]
        
        # If all seen, use all quotes
        if not unseen_quotes:
            candidate_quotes = quotes
        else:
            candidate_quotes = unseen_quotes
        
        # Weighted selection (lower used_count = higher chance)
        weights = [1.0 / (q.used_count + 1) for q in candidate_quotes]
        
        try:
            selected = random.choices(candidate_quotes, weights=weights, k=1)[0]
        except:
            selected = random.choice(candidate_quotes)
        
        return selected
    
    def _update_user_history(self, user_id: str, quote_id: str):
        """Update user's quote history"""
        if not user_id:
            return
        
        now = datetime.now(self.timezone)
        today = now.date()
        
        if user_id not in self.user_data:
            self.user_data[user_id] = UserQuoteHistory(
                user_id=user_id,
                quotes_seen=[],
                favorite_quotes=[],
                last_seen=None,
                streak_days=0,
                total_quotes=0
            )
        
        user = self.user_data[user_id]
        
        # Update last seen
        last_seen_date = user.last_seen.date() if user.last_seen else None
        
        if last_seen_date:
            if last_seen_date == today:
                # Already seen today
                pass
            elif last_seen_date == today - timedelta(days=1):
                # Consecutive day
                user.streak_days += 1
            else:
                # Streak broken
                user.streak_days = 1
        else:
            # First time
            user.streak_days = 1
        
        user.last_seen = now
        
        # Add quote to seen list (if not already)
        if quote_id not in user.quotes_seen:
            user.quotes_seen.append(quote_id)
            user.total_quotes += 1
        
        # Trim seen list (keep last 100)
        if len(user.quotes_seen) > 100:
            user.quotes_seen = user.quotes_seen[-100:]
    
    # ==================== USER FUNCTIONS ====================
    
    def toggle_favorite(self, user_id: str, quote_id: str) -> Tuple[bool, str]:
        """
        Toggle favorite status of a quote
        
        Returns:
            (is_favorite, status_message)
        """
        if user_id not in self.user_data:
            self.user_data[user_id] = UserQuoteHistory(
                user_id=user_id,
                quotes_seen=[],
                favorite_quotes=[],
                last_seen=None,
                streak_days=0,
                total_quotes=0
            )
        
        user = self.user_data[user_id]
        
        if quote_id in user.favorite_quotes:
            # Remove from favorites
            user.favorite_quotes.remove(quote_id)
            asyncio.create_task(self.save_data())
            return False, "❤️ থেকে সরানো হয়েছে"
        else:
            # Add to favorites
            if quote_id not in user.favorite_quotes:
                user.favorite_quotes.append(quote_id)
                asyncio.create_task(self.save_data())
                return True, "❤️ তে যোগ করা হয়েছে"
        
        return False, "কিছু সমস্যা হয়েছে"
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
        if user_id not in self.user_data:
            return {
                'streak_days': 0,
                'total_quotes': 0,
                'favorites': 0,
                'level': 1
            }
        
        user = self.user_data[user_id]
        
        # Calculate level based on total quotes
        level = min((user.total_quotes // 10) + 1, 10)
        
        return {
            'streak_days': user.streak_days,
            'total_quotes': user.total_quotes,
            'favorites': len(user.favorite_quotes),
            'level': level,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None
        }
    
    def get_user_favorites(self, user_id: str, limit: int = 20) -> List[Quote]:
        """Get user's favorite quotes"""
        if user_id not in self.user_data:
            return []
        
        favorites = []
        for quote_id in self.user_data[user_id].favorite_quotes[:limit]:
            quote = self.get_quote(quote_id)
            if quote:
                favorites.append(quote)
        
        return favorites
    
    # ==================== BOT COMMAND HANDLERS ====================
    
    async def handle_daily_quote_command(self, ctx, language: str = "bn"):
        """Handle /quote command"""
        try:
            quote_data = self.get_daily_quote(
                user_id=str(ctx.author.id),
                language=language
            )
            
            user_stats = self.get_user_stats(str(ctx.author.id))
            
            # Format message
            if language == "bn":
                message = f"**📖 আজকের উক্তি ({quote_data['date']})**\n\n"
                message += f"\"{quote_data['text']}\"\n"
                message += f"— *{quote_data['author']}*\n\n"
                message += f"🏷️ বিভাগ: {quote_data['category']}\n"
                message += f"📊 জনপ্রিয়তা: {quote_data['popularity']}\n"
                message += f"🔥 আপনার স্ট্রীক: {user_stats['streak_days']} দিন\n"
                message += f"📚 মোট উক্তি: {user_stats['total_quotes']}\n"
                message += f"❤️ প্রিয়: {user_stats['favorites']}\n"
                message += f"⭐ লেভেল: {user_stats['level']}\n\n"
                message += "`/fav` দিয়ে প্রিয় তালিকায় যোগ করুন"
            else:
                message = f"**📖 Quote of the Day ({quote_data['date']})**\n\n"
                message += f"\"{quote_data['text']}\"\n"
                message += f"— *{quote_data['author']}*\n\n"
                message += f"🏷️ Category: {quote_data['category']}\n"
                message += f"📊 Popularity: {quote_data['popularity']}\n"
                message += f"🔥 Your Streak: {user_stats['streak_days']} days\n"
                message += f"📚 Total Quotes: {user_stats['total_quotes']}\n"
                message += f"❤️ Favorites: {user_stats['favorites']}\n"
                message += f"⭐ Level: {user_stats['level']}\n\n"
                message += "Use `/fav` to add to favorites"
            
            # Send message
            if hasattr(ctx, 'send'):
                await ctx.send(message)
            elif hasattr(ctx, 'reply'):
                await ctx.reply(message)
            
            self.logger.info(f"📨 Quote sent to {ctx.author.id}")
            
        except Exception as e:
            error_msg = "উক্তি লোড করতে সমস্যা হয়েছে। পরে চেষ্টা করুন।" if language == "bn" else "Error loading quote. Please try again."
            self.logger.error(f"❌ Quote command error: {e}")
            
            if hasattr(ctx, 'send'):
                await ctx.send(error_msg)
            elif hasattr(ctx, 'reply'):
                await ctx.reply(error_msg)
    
    async def handle_search_command(self, ctx, query: str, language: str = "bn"):
        """Handle /searchquote command"""
        try:
            if not query or len(query) < 2:
                error_msg = "অনুগ্রহ করে কমপক্ষে ২ অক্ষরের একটি শব্দ লিখুন।" if language == "bn" else "Please enter at least 2 characters."
                await ctx.send(error_msg)
                return
            
            results = self.search_quotes(query, language=language, limit=5)
            
            if not results:
                no_results_msg = f"\"{query}\" এর জন্য কোন উক্তি পাওয়া যায়নি।" if language == "bn" else f"No quotes found for \"{query}\"."
                await ctx.send(no_results_msg)
                return
            
            # Format results
            if language == "bn":
                message = f"**🔍 '{query}' এর জন্য ফলাফল ({len(results)})**\n\n"
            else:
                message = f"**🔍 Results for '{query}' ({len(results)})**\n\n"
            
            for i, quote in enumerate(results, 1):
                message += f"{i}. \"{quote.text[:80]}...\"\n"
                message += f"   — *{quote.author}* | 📊 {quote.popularity}\n\n"
            
            message += "`/quote <id>` দিয়ে সম্পূর্ণ উক্তি দেখুন" if language == "bn" else "Use `/quote <id>` to view full quote"
            
            await ctx.send(message[:2000])  # Discord limit
            
        except Exception as e:
            self.logger.error(f"❌ Search command error: {e}")
            error_msg = "সার্চ করতে সমস্যা হয়েছে।" if language == "bn" else "Error searching."
            await ctx.send(error_msg)
    
    async def handle_favorite_command(self, ctx, quote_id: str = None):
        """Handle /fav command"""
        try:
            user_id = str(ctx.author.id)
            language = "bn"  # Default
            
            if quote_id:
                # Toggle specific quote
                is_fav, status = self.toggle_favorite(user_id, quote_id)
                
                if is_fav:
                    msg = f"✅ উক্তি #{quote_id} প্রিয় তালিকায় যোগ করা হয়েছে!"
                else:
                    msg = f"✅ উক্তি #{quote_id} প্রিয় তালিকা থেকে সরানো হয়েছে!"
                
            else:
                # Show favorites
                favorites = self.get_user_favorites(user_id)
                
                if not favorites:
                    msg = "📭 আপনার প্রিয় তালিকায় এখনও কোন উক্তি নেই।\n`/fav <quote_id>` দিয়ে যোগ করুন।"
                else:
                    msg = f"**❤️ আপনার প্রিয় উক্তি ({len(favorites)})**\n\n"
                    
                    for i, quote in enumerate(favorites[:10], 1):
                        msg += f"{i}. \"{quote.text[:60]}...\"\n"
                        msg += f"   — *{quote.author}* | ID: `{quote.id}`\n\n"
                    
                    if len(favorites) > 10:
                        msg += f"... এবং আরও {len(favorites) - 10}টি\n"
                    
                    msg += "`/fav <id>` দিয়ে সরান"
            
            await ctx.send(msg)
            
        except Exception as e:
            self.logger.error(f"❌ Favorite command error: {e}")
            await ctx.send("প্রিয় তালিকা ম্যানেজ করতে সমস্যা হয়েছে।")
    
    async def handle_stats_command(self, ctx):
        """Handle /quotestats command"""
        try:
            user_id = str(ctx.author.id)
            stats = self.get_user_stats(user_id)
            
            # Create progress bar for level
            progress = (stats['total_quotes'] % 10) * 10
            progress_bar = "▓" * (progress // 10) + "░" * (10 - (progress // 10))
            
            message = "**📊 আপনার উক্তি পরিসংখ্যান**\n\n"
            message += f"🔥 **স্ট্রীক:** {stats['streak_days']} দিন\n"
            message += f"📚 **মোট উক্তি:** {stats['total_quotes']}\n"
            message += f"❤️ **প্রিয় উক্তি:** {stats['favorites']}\n"
            message += f"⭐ **লেভেল:** {stats['level']}\n"
            message += f"📈 **প্রোগ্রেস:** [{progress_bar}] {progress}%\n\n"
            message += f"পরবর্তী লেভেলের জন্য {10 - (stats['total_quotes'] % 10)}টি উক্তি বাকি!"
            
            await ctx.send(message)
            
        except Exception as e:
            self.logger.error(f"❌ Stats command error: {e}")
            await ctx.send("পরিসংখ্যান লোড করতে সমস্যা হয়েছে।")
    
    async def handle_add_quote_command(self, ctx, text: str, author: str = "Unknown"):
        """Handle /addquote command (admin only)"""
        try:
            # Check permissions (simplified)
            # In real bot, check actual permissions
            
            if len(text) < 10:
                await ctx.send("উক্তি কমপক্ষে ১০ অক্ষরের হতে হবে।")
                return
            
            quote_id = self.add_quote(
                text=text,
                author=author,
                language="bn"  # Default to Bangla
            )
            
            await ctx.send(f"✅ নতুন উক্তি যোগ করা হয়েছে!\nID: `{quote_id}`\n\n\"{text[:100]}...\"")
            
        except Exception as e:
            self.logger.error(f"❌ Add quote error: {e}")
            await ctx.send("উক্তি যোগ করতে সমস্যা হয়েছে।")
    
    # ==================== AUTOMATED TASKS ====================
    
    async def setup(self):
        """Setup periodic tasks"""
        # Clear daily cache at reset time
        asyncio.create_task(self._schedule_daily_reset())
        
        # Auto-save every 5 minutes
        asyncio.create_task(self._auto_save_task())
        
        self.logger.info("✅ QuoteOfDay scheduler started")
    
    async def _schedule_daily_reset(self):
        """Schedule daily cache reset"""
        while True:
            now = datetime.now(self.timezone)
            next_reset = now.replace(hour=self.daily_reset_hour, minute=0, second=0, microsecond=0)
            
            if now.hour >= self.daily_reset_hour:
                next_reset += timedelta(days=1)
            
            wait_seconds = (next_reset - now).total_seconds()
            
            self.logger.info(f"⏰ Next quote cache reset in {wait_seconds/3600:.1f} hours")
            
            await asyncio.sleep(wait_seconds)
            
            # Clear cache
            self.daily_cache.clear()
            self.logger.info("🔄 Daily quote cache cleared")
    
    async def _auto_save_task(self):
        """Auto-save data periodically"""
        while True:
            await asyncio.sleep(300)  # 5 minutes
            try:
                await self.save_data()
                self.logger.debug("💾 Quote data auto-saved")
            except Exception as e:
                self.logger.error(f"❌ Auto-save error: {e}")
    
    # ==================== STATISTICS ====================
    
    def get_system_stats(self) -> Dict:
        """Get system-wide statistics"""
        total_quotes = len(self.quotes)
        total_users = len(self.user_data)
        
        # Count by language
        by_language = defaultdict(int)
        for quote in self.quotes.values():
            by_language[quote.language] += 1
        
        # Count by category
        by_category = defaultdict(int)
        for quote in self.quotes.values():
            by_category[quote.category] += 1
        
        # Most popular quotes
        popular = sorted(self.quotes.values(), key=lambda x: x.popularity, reverse=True)[:5]
        
        return {
            'total_quotes': total_quotes,
            'total_users': total_users,
            'by_language': dict(by_language),
            'by_category': dict(by_category),
            'most_popular': [
                {'id': q.id, 'text': q.text[:50], 'popularity': q.popularity}
                for q in popular
            ]
        }
    
    # ==================== EXPORT/IMPORT ====================
    
    async def export_quotes(self, format: str = "json") -> str:
        """Export quotes to file"""
        if format == "json":
            quotes_dict = {qid: quote.to_dict() for qid, quote in self.quotes.items()}
            export_file = os.path.join(self.data_dir, f"quotes_export_{datetime.now().strftime('%Y%m%d')}.json")
            
            async with aiofiles.open(export_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(quotes_dict, ensure_ascii=False, indent=2))
            
            return export_file
        
        return None
    
    async def import_quotes(self, file_path: str) -> int:
        """Import quotes from file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            
            imported = 0
            for qid, qdata in data.items():
                if qid not in self.quotes:
                    self.quotes[qid] = Quote.from_dict(qdata)
                    imported += 1
            
            await self.save_data()
            return imported
            
        except Exception as e:
            self.logger.error(f"❌ Import error: {e}")
            return 0


# ==================== FACTORY FUNCTION ====================

def setup(bot):
    """Setup function for bot integration"""
    quote_system = QuoteOfDay(bot)
    asyncio.create_task(quote_system.setup())
    return quote_system
