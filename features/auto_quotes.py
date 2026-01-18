#!/usr/bin/env python3
"""
Auto Quote System for Roastify Bot
Automatic quote/meme posting system
"""

import os
import sys
import logging
import json
import random
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import apscheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

class AutoQuoteSystem:
    """Automatic quote posting system"""
    
    def __init__(self, bot=None):
        """
        Initialize AutoQuoteSystem
        
        Args:
            bot: The bot instance (RoastifyBot)
        """
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Initializing AutoQuoteSystem...")
        
        # Configuration
        self.config = self.load_config()
        
        # Scheduler for automatic posting
        self.scheduler = AsyncIOScheduler()
        
        # Quote database
        self.quotes = []
        self.memes = []
        self.facts = []
        self.jokes = []
        
        # Statistics
        self.stats = {
            'total_quotes_sent': 0,
            'last_sent_time': None,
            'active_chats': set(),
            'errors': 0
        }
        
        # Load data
        self.load_quotes()
        self.load_memes()
        self.load_facts()
        self.load_jokes()
        
        # Schedule jobs if enabled
        if self.config.get('ENABLE_AUTO_QUOTES', True):
            self.schedule_jobs()
        
        self.logger.info(f"✅ AutoQuoteSystem initialized with {len(self.quotes)} quotes, {len(self.memes)} memes")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config = {
            'QUOTE_INTERVAL': 3600,  # 1 hour
            'MEME_INTERVAL': 7200,   # 2 hours
            'FACT_INTERVAL': 10800,  # 3 hours
            'ENABLE_AUTO_QUOTES': True,
            'MAX_QUOTES_PER_DAY': 10,
            'TARGET_CHATS': [],  # Group/channel IDs
            'ADMIN_IDS': []
        }
        
        # Load from environment or config file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            config['QUOTE_INTERVAL'] = int(os.getenv('QUOTE_INTERVAL', 3600))
            config['MEME_INTERVAL'] = int(os.getenv('MEME_INTERVAL', 7200))
            config['FACT_INTERVAL'] = int(os.getenv('FACT_INTERVAL', 10800))
            config['ENABLE_AUTO_QUOTES'] = os.getenv('ENABLE_AUTO_QUOTES', 'True').lower() == 'true'
            config['MAX_QUOTES_PER_DAY'] = int(os.getenv('MAX_QUOTES_PER_DAY', 10))
            
            # Parse target chats
            target_chats = os.getenv('TARGET_CHATS', '')
            if target_chats:
                config['TARGET_CHATS'] = [int(c.strip()) for c in target_chats.split(',') if c.strip().isdigit()]
            
            # Parse admin IDs
            admin_ids = os.getenv('ADMIN_IDS', '')
            if admin_ids:
                config['ADMIN_IDS'] = [int(a.strip()) for a in admin_ids.split(',') if a.strip().isdigit()]
                
        except Exception as e:
            self.logger.warning(f"⚠️ Config loading error: {e}, using defaults")
        
        return config
    
    def load_quotes(self):
        """Load quotes from JSON file"""
        quotes_file = Path('data/quotes.json')
        backup_quotes = [
            "জীবনে দুইটি জিনিস কখনো ফিরে আসে না - সময় এবং সুযোগ।",
            "সফলতা পাওয়ার জন্য প্রথমে নিজেকে বিশ্বাস করতে হয়।",
            "ভালোবাসা দিয়ে পাওয়া যায়, ক্রয় করা যায় না।",
            "জ্ঞান হলো সেই সম্পদ যা কখনো চুরি হয় না।",
            "ধৈর্য্য হলো বিজয়ের চাবিকাঠি।",
            "স্বপ্ন দেখো, বিশ্বাস করো, অর্জন করো।",
            "ভুল থেকে শিখলেই মানুষ বড় হয়।",
            "সততা সবচেয়ে বড় সম্পদ।",
            "কঠোর পরিশ্রম কখনো বিফলে যায় না।",
            "ক্ষমা করাই হলো সবচেয়ে বড় শক্তি।"
        ]
        
        try:
            if quotes_file.exists():
                with open(quotes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quotes = data.get('quotes', backup_quotes)
            else:
                self.quotes = backup_quotes
                # Create directory and save backup
                quotes_file.parent.mkdir(parents=True, exist_ok=True)
                with open(quotes_file, 'w', encoding='utf-8') as f:
                    json.dump({'quotes': backup_quotes}, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"❌ Error loading quotes: {e}")
            self.quotes = backup_quotes
    
    def load_memes(self):
        """Load meme templates"""
        memes_file = Path('data/memes.json')
        backup_memes = [
            {"text": "When you realize Monday is tomorrow", "template": "meme1"},
            {"text": "My brain during exams", "template": "meme2"},
            {"text": "Sleep vs Assignment", "template": "meme3"},
            {"text": "Me trying to be productive", "template": "meme4"},
            {"text": "Expectation vs Reality", "template": "meme5"}
        ]
        
        try:
            if memes_file.exists():
                with open(memes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memes = data.get('memes', backup_memes)
            else:
                self.memes = backup_memes
        except Exception as e:
            self.logger.error(f"❌ Error loading memes: {e}")
            self.memes = backup_memes
    
    def load_facts(self):
        """Load interesting facts"""
        self.facts = [
            "মৌমাছিরা এক সেকেন্ডে ২০০ বার ডানা ঝাপটায়।",
            "মানুষের মস্তিষ্ক ৭৫% পানি দিয়ে তৈরি।",
            "শুক্রগ্রহে একদিন পৃথিবীর এক বছরের সমান।",
            "আকাশ আসলে বেগুনি রঙের, কিন্তু আমরা নীল দেখি।",
            "হাতিরা একমাত্র স্তন্যপায়ী যারা লাফাতে পারে না।",
            "প্রজাপতিরা পায়ের মাধ্যমে স্বাদ গ্রহণ করে।",
            "ডলফিনরা এক চোখ খোলা রেখে ঘুমায়।",
            "ওস্টরিচের চোখ তার মস্তিষ্কের চেয়ে বড়।",
            "সিংহ দিনে ২০ ঘন্টা ঘুমায়।",
            "মানুষের নাক ১ ট্রিলিয়ন গন্ধ চিনতে পারে।"
        ]
    
    def load_jokes(self):
        """Load jokes"""
        self.jokes = [
            "শিক্ষক: পরীক্ষার সময় কপি করবে কেন?\nছাত্র: স্যার, কপিরাইট তো ভাঙবো না!",
            "বাবা: তুই এত অলস কেন?\nছেলে: বাবা, জিন্স দেখে মানুষ চেনা যায় না!",
            "ডাক্তার: আপনার হার্টের অবস্থা ভালো না।\nরোগী: কষ্ট করে বলছেন কেন, মেসেজ করে দিতেন!",
            "স্বামী: তুমি রান্না শিখবে?\nস্ত্রী: না, ইউটিউবে দেখলেই হবে!",
            "বন্ধু: তোর ফোনে কতজিএবি র‍্যাম?\nবন্ধু: কতজি নয়, সবজি র‍্যাম - পেয়াজ, রসুন!",
            "কাস্টমার: এই চালে পোকা আছে!\nদোকানী: স্যার, এক্সট্রা প্রোটিন ফ্রি!",
            "শিক্ষক: জল কেন স্ফুটনাঙ্কে ফুটে?\nছাত্র: স্যার, জলের মাথা গরম হয়ে যায়!",
            "বাবা: কেন সারাক্ষণ ফোনে?\nছেলে: বাবা, ব্যাটারি লাইফ টেস্ট করছি!"
        ]
    
    def schedule_jobs(self):
        """Schedule automatic posting jobs"""
        try:
            # Schedule quote posting
            self.scheduler.add_job(
                self.post_auto_quote,
                IntervalTrigger(seconds=self.config['QUOTE_INTERVAL']),
                id='auto_quote',
                replace_existing=True
            )
            
            # Schedule meme posting
            self.scheduler.add_job(
                self.post_auto_meme,
                IntervalTrigger(seconds=self.config['MEME_INTERVAL']),
                id='auto_meme',
                replace_existing=True
            )
            
            # Schedule fact posting
            self.scheduler.add_job(
                self.post_auto_fact,
                IntervalTrigger(seconds=self.config['FACT_INTERVAL']),
                id='auto_fact',
                replace_existing=True
            )
            
            # Start scheduler
            self.scheduler.start()
            self.logger.info(f"✅ Scheduled {len(self.scheduler.get_jobs())} auto-posting jobs")
            
        except Exception as e:
            self.logger.error(f"❌ Error scheduling jobs: {e}")
    
    async def post_auto_quote(self):
        """Post automatic quote to target chats"""
        if not self.quotes or not self.config['TARGET_CHATS']:
            return
        
        quote = random.choice(self.quotes)
        author = random.choice(['- অজানা', '- প্রবাদ', '- জনপ্রিয় উক্তি'])
        
        keyboard = [
            [InlineKeyboardButton("📜 Another Quote", callback_data="auto_quote_next"),
             InlineKeyboardButton("💬 Send to Group", callback_data="auto_quote_share")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = f"""
<b>📖 আজকের উক্তি</b>

<i>"{quote}"</i>

{author}

<code>🔁 Auto Posted • {datetime.now().strftime('%H:%M')}</code>
        """
        
        success_count = 0
        for chat_id in self.config['TARGET_CHATS']:
            try:
                if self.bot and hasattr(self.bot, 'application'):
                    await self.bot.application.bot.send_message(
                        chat_id=chat_id,
                        text=message_text,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                    success_count += 1
                    await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                self.logger.error(f"❌ Error posting to {chat_id}: {e}")
                self.stats['errors'] += 1
        
        self.stats['total_quotes_sent'] += success_count
        self.stats['last_sent_time'] = datetime.now()
        
        if success_count > 0:
            self.logger.info(f"📤 Auto-quote sent to {success_count} chats")
    
    async def post_auto_meme(self):
        """Post automatic meme"""
        if not self.memes or not self.config['TARGET_CHATS']:
            return
        
        meme = random.choice(self.memes)
        message_text = f"""
<b>😂 আজকের মিম</b>

{meme['text']}

<code>🎨 Template: {meme['template']}</code>
<code>🕒 {datetime.now().strftime('%H:%M')}</code>
        """
        
        keyboard = [
            [InlineKeyboardButton("😂 Another Meme", callback_data="auto_meme_next"),
             InlineKeyboardButton("🔄 Refresh", callback_data="auto_meme_refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        for chat_id in self.config['TARGET_CHATS'][:3]:  # Limit to 3 chats
            try:
                if self.bot and hasattr(self.bot, 'application'):
                    await self.bot.application.bot.send_message(
                        chat_id=chat_id,
                        text=message_text,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
            except Exception as e:
                self.logger.error(f"❌ Error posting meme to {chat_id}: {e}")
    
    async def post_auto_fact(self):
        """Post automatic fact"""
        if not self.facts or not self.config['TARGET_CHATS']:
            return
        
        fact = random.choice(self.facts)
        message_text = f"""
<b>🔍 মজার তথ্য</b>

{fact}

<code>📚 Did You Know?</code>
<code>⏰ {datetime.now().strftime('%H:%M')}</code>
        """
        
        for chat_id in self.config['TARGET_CHATS'][:2]:  # Limit to 2 chats
            try:
                if self.bot and hasattr(self.bot, 'application'):
                    await self.bot.application.bot.send_message(
                        chat_id=chat_id,
                        text=message_text,
                        parse_mode='HTML'
                    )
            except Exception as e:
                self.logger.error(f"❌ Error posting fact to {chat_id}: {e}")
    
    async def get_random_quote(self, update: Update = None, context: ContextTypes.DEFAULT_TYPE = None):
        """Get random quote for manual request"""
        if not self.quotes:
            return "No quotes available. Please add some quotes first."
        
        quote = random.choice(self.quotes)
        return f"""
<b>📜 র‍্যান্ডম উক্তি</b>

<i>"{quote}"</i>

<code>✨ রোস্টিফাই বট</code>
        """
    
    async def get_random_joke(self):
        """Get random joke"""
        if not self.jokes:
            return "No jokes available."
        
        joke = random.choice(self.jokes)
        return f"""
<b>😂 মজার জোক</b>

{joke}

<code>😄 হাসতে হাসতে পেটে খিল ধরে!</code>
        """
    
    async def get_random_fact(self):
        """Get random fact"""
        if not self.facts:
            return "No facts available."
        
        fact = random.choice(self.facts)
        return f"""
<b>🔬 অজানা তথ্য</b>

{fact}

<code>🧠 জ্ঞান বৃদ্ধিকারী</code>
        """
    
    async def manual_quote_post(self, chat_id: int, quote_type: str = 'quote'):
        """Manually post quote to specific chat"""
        try:
            if quote_type == 'quote':
                message = await self.get_random_quote()
            elif quote_type == 'joke':
                message = await self.get_random_joke()
            elif quote_type == 'fact':
                message = await self.get_random_fact()
            else:
                message = await self.get_random_quote()
            
            if self.bot and hasattr(self.bot, 'application'):
                await self.bot.application.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='HTML'
                )
                return True
        except Exception as e:
            self.logger.error(f"❌ Manual post error: {e}")
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'total_quotes': len(self.quotes),
            'total_memes': len(self.memes),
            'total_facts': len(self.facts),
            'total_jokes': len(self.jokes),
            'quotes_sent_today': self.stats['total_quotes_sent'],
            'last_sent': self.stats['last_sent_time'],
            'active_jobs': len(self.scheduler.get_jobs()) if self.scheduler else 0,
            'errors': self.stats['errors']
        }
    
    def add_quote(self, quote: str, author: str = "Unknown") -> bool:
        """Add new quote to database"""
        try:
            self.quotes.append(quote)
            
            # Save to file
            quotes_file = Path('data/quotes.json')
            data = {'quotes': self.quotes}
            
            with open(quotes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ Quote added: {quote[:50]}...")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error adding quote: {e}")
            return False
    
    def add_meme(self, text: str, template: str) -> bool:
        """Add new meme template"""
        try:
            self.memes.append({'text': text, 'template': template})
            
            # Save to file
            memes_file = Path('data/memes.json')
            data = {'memes': self.memes}
            
            with open(memes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Error adding meme: {e}")
            return False
    
    def stop(self):
        """Stop auto quote system"""
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown()
                self.logger.info("🛑 AutoQuoteSystem stopped")
        except Exception as e:
            self.logger.error(f"❌ Error stopping system: {e}")
    
    def restart(self):
        """Restart auto quote system"""
        self.stop()
        
        # Reload data
        self.load_quotes()
        self.load_memes()
        self.load_facts()
        self.load_jokes()
        
        # Restart scheduler if enabled
        if self.config.get('ENABLE_AUTO_QUOTES', True):
            self.schedule_jobs()
        
        self.logger.info("🔄 AutoQuoteSystem restarted")

# Standalone test function
if __name__ == "__main__":
    # Test the system
    logging.basicConfig(level=logging.INFO)
    system = AutoQuoteSystem()
    
    print(f"✅ AutoQuoteSystem Test")
    print(f"📊 Quotes loaded: {len(system.quotes)}")
    print(f"📊 Memes loaded: {len(system.memes)}")
    print(f"📊 Facts loaded: {len(system.facts)}")
    print(f"📊 Jokes loaded: {len(system.jokes)}")
    
    # Show sample quote
    import asyncio
    sample = asyncio.run(system.get_random_quote())
    print(f"\n📜 Sample Quote:\n{sample}")
