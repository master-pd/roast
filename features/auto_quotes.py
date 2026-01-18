"""
Advanced Auto Quotes System - Professional Production Ready
Version: 3.0.0
Author: RoastifyBot Team
Features:
- Intelligent quote scheduling
- Channel-specific configurations
- User engagement tracking
- Adaptive quote selection
- Rate limiting & cooldowns
- Analytics & reporting
- Error recovery
"""

import asyncio
import random
import json
import os
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Set, Tuple, Union
from enum import Enum
import aiofiles
from dataclasses import dataclass, asdict
from collections import defaultdict
import pytz

# ==================== DATA CLASSES ====================

@dataclass
class ChannelConfig:
    """Channel configuration for auto quotes"""
    channel_id: str
    enabled: bool = True
    schedule_times: List[str] = None  # List of "HH:MM" times
    quote_language: str = "bn"
    categories: List[str] = None
    mention_role: str = None
    cooldown_minutes: int = 30
    last_sent: Optional[datetime] = None
    total_sent: int = 0
    active_users: Set[str] = None
    
    def __post_init__(self):
        if self.schedule_times is None:
            self.schedule_times = ["09:00", "12:00", "15:00", "18:00", "21:00"]
        if self.categories is None:
            self.categories = ["motivational", "inspirational", "life"]
        if self.active_users is None:
            self.active_users = set()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['active_users'] = list(self.active_users)
        data['last_sent'] = self.last_sent.isoformat() if self.last_sent else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChannelConfig':
        """Create from dictionary"""
        data = data.copy()
        if 'active_users' in data:
            data['active_users'] = set(data['active_users'])
        if data.get('last_sent'):
            data['last_sent'] = datetime.fromisoformat(data['last_sent'])
        return cls(**data)


@dataclass
class AutoQuoteStats:
    """Statistics for auto quotes"""
    total_quotes_sent: int = 0
    total_channels_active: int = 0
    quotes_by_hour: Dict[int, int] = None
    quotes_by_category: Dict[str, int] = None
    most_active_channels: List[Tuple[str, int]] = None
    engagement_rate: float = 0.0  # Reactions per quote
    
    def __post_init__(self):
        if self.quotes_by_hour is None:
            self.quotes_by_hour = defaultdict(int)
        if self.quotes_by_category is None:
            self.quotes_by_category = defaultdict(int)
        if self.most_active_channels is None:
            self.most_active_channels = []


class QuotePriority(Enum):
    """Priority levels for quote selection"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4  # For special occasions


class EngagementLevel(Enum):
    """User engagement levels"""
    LOW = "low"        # < 1 reaction
    MEDIUM = "medium"  # 1-3 reactions
    HIGH = "high"      # > 3 reactions


# ==================== MAIN AUTO QUOTES CLASS ====================

class AutoQuotes:
    """
    Advanced Automatic Quote Delivery System
    
    Features:
    1. Smart Scheduling - Adaptive time slots
    2. Engagement Tracking - User interaction analytics
    3. Channel Management - Per-channel configurations
    4. Rate Limiting - Prevent spam
    5. Error Recovery - Auto-retry failed sends
    6. Analytics Dashboard - Performance metrics
    7. Seasonal Quotes - Holiday/event specific quotes
    8. A/B Testing - Test different quote formats
    """
    
    def __init__(self, bot, quote_system=None):
        """
        Initialize Auto Quotes System
        
        Args:
            bot: Main bot instance
            quote_system: QuoteOfDay system instance
        """
        self.bot = bot
        self.logger = bot.logger
        self.config = getattr(bot, 'config', {})
        self.quote_system = quote_system
        
        # Paths
        self.data_dir = "data/auto_quotes"
        self.config_file = os.path.join(self.data_dir, "channels.json")
        self.stats_file = os.path.join(self.data_dir, "stats.json")
        self.log_file = os.path.join(self.data_dir, "activity.log")
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Data storage
        self.channel_configs: Dict[str, ChannelConfig] = {}
        self.stats = AutoQuoteStats()
        self.scheduler_tasks = []
        self.is_running = False
        self.cooldown_cache = {}  # channel_id -> last_sent_time
        self.engagement_data = defaultdict(list)  # channel_id -> list of reaction counts
        
        # Settings
        self.timezone = pytz.timezone('Asia/Dhaka')
        self.max_quotes_per_hour = 2
        self.min_engagement_threshold = 0.1  # 10% reactions
        self.enable_adaptive_scheduling = True
        
        # Special occasions
        self.special_dates = {
            "01-01": {"name": "New Year", "priority": QuotePriority.URGENT},
            "02-21": {"name": "International Mother Language Day", "priority": QuotePriority.HIGH},
            "03-26": {"name": "Independence Day", "priority": QuotePriority.HIGH},
            "05-01": {"name": "May Day", "priority": QuotePriority.MEDIUM},
            "08-15": {"name": "National Mourning Day", "priority": QuotePriority.HIGH},
            "12-16": {"name": "Victory Day", "priority": QuotePriority.HIGH},
            "12-25": {"name": "Christmas", "priority": QuotePriority.MEDIUM}
        }
        
        # Load data
        self.load_data()
        
        self.logger.info("✅ AutoQuotes initialized")
    
    # ==================== DATA MANAGEMENT ====================
    
    def load_data(self):
        """Load configuration and stats"""
        try:
            # Load channel configurations
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.channel_configs = {
                        cid: ChannelConfig.from_dict(cdata) 
                        for cid, cdata in data.items()
                    }
            
            # Load statistics
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stats = AutoQuoteStats(**data)
                    
        except Exception as e:
            self.logger.error(f"❌ Error loading auto quotes data: {e}")
            self.channel_configs = {}
            self.stats = AutoQuoteStats()
    
    async def save_data(self):
        """Save configuration and stats"""
        try:
            # Save channel configurations
            config_dict = {
                cid: config.to_dict() 
                for cid, config in self.channel_configs.items()
            }
            
            async with aiofiles.open(self.config_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(config_dict, ensure_ascii=False, indent=2))
            
            # Save statistics
            stats_dict = asdict(self.stats)
            async with aiofiles.open(self.stats_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(stats_dict, ensure_ascii=False, indent=2))
            
            # Log activity
            await self.log_activity("SYSTEM", "Data saved successfully")
                
        except Exception as e:
            self.logger.error(f"❌ Error saving auto quotes data: {e}")
            await self.log_activity("ERROR", f"Save failed: {str(e)}")
    
    async def log_activity(self, channel_id: str, message: str):
        """Log activity to file"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{channel_id}] {message}\n"
            
            async with aiofiles.open(self.log_file, 'a', encoding='utf-8') as f:
                await f.write(log_entry)
                
        except Exception as e:
            self.logger.error(f"❌ Error logging activity: {e}")
    
    # ==================== CHANNEL MANAGEMENT ====================
    
    def add_channel(self, channel_id: str, **kwargs) -> bool:
        """
        Add channel to auto quotes system
        
        Args:
            channel_id: Discord channel ID
            **kwargs: Configuration options
        
        Returns:
            Success status
        """
        try:
            if channel_id in self.channel_configs:
                return False  # Already exists
            
            config = ChannelConfig(channel_id=channel_id, **kwargs)
            self.channel_configs[channel_id] = config
            
            # Update stats
            self.stats.total_channels_active = len([
                c for c in self.channel_configs.values() 
                if c.enabled
            ])
            
            # Save in background
            asyncio.create_task(self.save_data())
            asyncio.create_task(self.log_activity(channel_id, "Channel added to auto quotes"))
            
            self.logger.info(f"➕ Added channel {channel_id} to auto quotes")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error adding channel: {e}")
            return False
    
    def remove_channel(self, channel_id: str) -> bool:
        """Remove channel from auto quotes"""
        if channel_id in self.channel_configs:
            del self.channel_configs[channel_id]
            
            # Update stats
            self.stats.total_channels_active = len([
                c for c in self.channel_configs.values() 
                if c.enabled
            ])
            
            asyncio.create_task(self.save_data())
            asyncio.create_task(self.log_activity(channel_id, "Channel removed from auto quotes"))
            
            self.logger.info(f"➖ Removed channel {channel_id} from auto quotes")
            return True
        
        return False
    
    def update_channel_config(self, channel_id: str, **kwargs) -> bool:
        """Update channel configuration"""
        if channel_id not in self.channel_configs:
            return False
        
        config = self.channel_configs[channel_id]
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        asyncio.create_task(self.save_data())
        asyncio.create_task(self.log_activity(channel_id, f"Config updated: {kwargs}"))
        
        return True
    
    def get_channel_config(self, channel_id: str) -> Optional[ChannelConfig]:
        """Get channel configuration"""
        return self.channel_configs.get(channel_id)
    
    def get_active_channels(self) -> List[ChannelConfig]:
        """Get all active channels"""
        return [
            config for config in self.channel_configs.values()
            if config.enabled
        ]
    
    # ==================== SCHEDULING SYSTEM ====================
    
    async def start(self):
        """Start auto quotes scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start scheduler tasks
        self.scheduler_tasks = [
            asyncio.create_task(self._main_scheduler()),
            asyncio.create_task(self._engagement_analyzer()),
            asyncio.create_task(self._stats_updater()),
            asyncio.create_task(self._adaptive_schedule_adjuster())
        ]
        
        self.logger.info("🚀 AutoQuotes scheduler started")
        await self.log_activity("SYSTEM", "Scheduler started")
    
    async def stop(self):
        """Stop auto quotes system"""
        self.is_running = False
        
        # Cancel all tasks
        for task in self.scheduler_tasks:
            task.cancel()
        
        self.scheduler_tasks.clear()
        
        self.logger.info("⏹️ AutoQuotes scheduler stopped")
        await self.log_activity("SYSTEM", "Scheduler stopped")
    
    async def _main_scheduler(self):
        """Main scheduling loop"""
        while self.is_running:
            try:
                now = datetime.now(self.timezone)
                current_time = now.strftime("%H:%M")
                
                # Check each active channel
                for config in self.get_active_channels():
                    # Check cooldown
                    if self._is_in_cooldown(config.channel_id):
                        continue
                    
                    # Check if it's time to send
                    if current_time in config.schedule_times:
                        # Send quote
                        await self.send_auto_quote(config.channel_id)
                        
                        # Update last sent time
                        config.last_sent = now
                        self.cooldown_cache[config.channel_id] = now
                        
                        # Wait to avoid multiple triggers
                        await asyncio.sleep(1)
                
                # Sleep until next minute
                await asyncio.sleep(60 - now.second)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Scheduler error: {e}")
                await self.log_activity("ERROR", f"Scheduler error: {str(e)}")
                await asyncio.sleep(60)
    
    def _is_in_cooldown(self, channel_id: str) -> bool:
        """Check if channel is in cooldown period"""
        if channel_id not in self.cooldown_cache:
            return False
        
        config = self.get_channel_config(channel_id)
        if not config:
            return False
        
        last_sent = self.cooldown_cache[channel_id]
        cooldown_end = last_sent + timedelta(minutes=config.cooldown_minutes)
        
        return datetime.now(self.timezone) < cooldown_end
    
    async def send_auto_quote(self, channel_id: str, force: bool = False) -> bool:
        """
        Send automatic quote to channel
        
        Args:
            channel_id: Target channel ID
            force: Send even if cooldown active
        
        Returns:
            Success status
        """
        try:
            config = self.get_channel_config(channel_id)
            if not config or (not force and not config.enabled):
                return False
            
            # Get channel object
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                self.logger.error(f"❌ Channel not found: {channel_id}")
                return False
            
            # Check rate limiting
            if not force and self._is_rate_limited(channel_id):
                await self.log_activity(channel_id, "Rate limited, skipping")
                return False
            
            # Get appropriate quote
            quote_data = await self._get_auto_quote_for_channel(config)
            if not quote_data:
                await self.log_activity(channel_id, "No suitable quote found")
                return False
            
            # Format message
            message = await self._format_auto_quote_message(quote_data, config)
            
            # Send message
            sent_message = await channel.send(message)
            
            # Update statistics
            config.total_sent += 1
            config.last_sent = datetime.now(self.timezone)
            
            self.stats.total_quotes_sent += 1
            self.stats.quotes_by_hour[datetime.now().hour] += 1
            self.stats.quotes_by_category[quote_data.get('category', 'general')] += 1
            
            # Track for engagement
            self.bot.loop.create_task(self._track_engagement(sent_message, channel_id))
            
            # Save data
            asyncio.create_task(self.save_data())
            
            # Log activity
            log_msg = f"Auto quote sent: {quote_data.get('id', 'N/A')}"
            await self.log_activity(channel_id, log_msg)
            
            self.logger.info(f"📨 Auto quote sent to {channel_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error sending auto quote: {e}")
            await self.log_activity(channel_id, f"Send failed: {str(e)}")
            return False
    
    def _is_rate_limited(self, channel_id: str) -> bool:
        """Check if channel is rate limited"""
        hour = datetime.now().hour
        
        # Count quotes sent this hour
        hour_count = sum(
            1 for config in self.channel_configs.values()
            if config.last_sent and 
            config.last_sent.hour == hour and
            config.channel_id == channel_id
        )
        
        return hour_count >= self.max_quotes_per_hour
    
    async def _get_auto_quote_for_channel(self, config: ChannelConfig) -> Dict:
        """
        Get appropriate quote for channel
        
        Args:
            config: Channel configuration
        
        Returns:
            Quote data
        """
        try:
            # Check for special occasions
            today_str = datetime.now().strftime("%m-%d")
            priority = QuotePriority.MEDIUM
            
            if today_str in self.special_dates:
                special = self.special_dates[today_str]
                priority = special["priority"]
                
                # Try to get holiday-specific quote
                holiday_quote = await self._get_holiday_quote(today_str, config.quote_language)
                if holiday_quote:
                    return holiday_quote
            
            # Get quote based on engagement level
            engagement = self._get_channel_engagement_level(config.channel_id)
            
            if engagement == EngagementLevel.HIGH:
                # Send popular quotes for high engagement channels
                if self.quote_system:
                    # Get most popular quotes
                    popular_quotes = sorted(
                        self.quote_system.quotes.values(),
                        key=lambda x: x.popularity,
                        reverse=True
                    )[:20]
                    
                    if popular_quotes:
                        quote = random.choice(popular_quotes)
                        return {
                            'id': quote.id,
                            'text': quote.text,
                            'author': quote.author,
                            'category': quote.category,
                            'language': quote.language,
                            'tags': quote.tags
                        }
            
            # Default: random quote from preferred categories
            if self.quote_system:
                # Filter by language and categories
                filtered_quotes = [
                    quote for quote in self.quote_system.quotes.values()
                    if quote.language == config.quote_language and
                    quote.category in config.categories
                ]
                
                if filtered_quotes:
                    quote = random.choice(filtered_quotes)
                    return {
                        'id': quote.id,
                        'text': quote.text,
                        'author': quote.author,
                        'category': quote.category,
                        'language': quote.language,
                        'tags': quote.tags
                    }
            
            # Fallback: use quote system's daily quote
            if self.quote_system:
                return self.quote_system.get_daily_quote(
                    language=config.quote_language,
                    category=random.choice(config.categories) if config.categories else None
                )
            
            # Ultimate fallback
            return {
                'id': 'fallback',
                'text': "জীবনে হাসতে থাকো, প্রতিদিন নতুন কিছু শেখো!",
                'author': "RoastifyBot",
                'category': "motivational",
                'language': config.quote_language,
                'tags': ["জীবন", "হাসি", "শিক্ষা"]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting auto quote: {e}")
            return None
    
    async def _get_holiday_quote(self, date_str: str, language: str) -> Optional[Dict]:
        """Get holiday-specific quote"""
        holiday_quotes = {
            "01-01": {
                "bn": "নতুন বছর, নতুন আশা, নতুন স্বপ্ন। সফল হোক আপনার প্রতিটি পরিকল্পনা!",
                "en": "New year, new hopes, new dreams. May all your plans succeed!"
            },
            "02-21": {
                "bn": "মায়ের ভাষার মর্যাদা রক্ষায় যারা জীবন দিয়েছেন, তাদের প্রতি বিনম্র শ্রদ্ধা।",
                "en": "Salute to those who sacrificed their lives for the dignity of mother language."
            },
            "03-26": {
                "bn": "স্বাধীনতা সবার জন্মগত অধিকার। মহান স্বাধীনতা দিবসে সবার জন্য শুভকামনা।",
                "en": "Freedom is everyone's birthright. Happy Independence Day to all."
            }
        }
        
        if date_str in holiday_quotes:
            text = holiday_quotes[date_str].get(language, holiday_quotes[date_str]["bn"])
            return {
                'id': f'holiday_{date_str}',
                'text': text,
                'author': "RoastifyBot",
                'category': "special",
                'language': language,
                'tags': ["holiday", "special"]
            }
        
        return None
    
    async def _format_auto_quote_message(self, quote_data: Dict, config: ChannelConfig) -> str:
        """Format quote message for sending"""
        # Add mention if configured
        mention = f"<@&{config.mention_role}> " if config.mention_role else ""
        
        # Add emoji based on category
        category_emojis = {
            "motivational": "💪",
            "inspirational": "✨",
            "life": "🌱",
            "funny": "😂",
            "love": "❤️",
            "wisdom": "🧠",
            "success": "🏆",
            "friendship": "🤝",
            "special": "🎉"
        }
        
        emoji = category_emojis.get(quote_data['category'], "💬")
        
        # Format based on language
        if quote_data['language'] == "bn":
            message = f"{emoji} **আজকের বিশেষ উক্তি** {emoji}\n\n"
            message += f"\"{quote_data['text']}\"\n\n"
            message += f"— *{quote_data['author']}*\n\n"
            message += f"🏷️ `{quote_data['category']}` | 📚 ID: `{quote_data.get('id', 'N/A')}`\n"
            message += f"❤️ `/fav {quote_data.get('id', '')}` দিয়ে প্রিয় তালিকায় রাখুন\n"
            message += "🔔 `/autosettings` দিয়ে নোটিফিকেশন কাস্টমাইজ করুন"
        else:
            message = f"{emoji} **Special Quote of the Day** {emoji}\n\n"
            message += f"\"{quote_data['text']}\"\n\n"
            message += f"— *{quote_data['author']}*\n\n"
            message += f"🏷️ `{quote_data['category']}` | 📚 ID: `{quote_data.get('id', 'N/A')}`\n"
            message += f"❤️ Use `/fav {quote_data.get('id', '')}` to add to favorites\n"
            message += "🔔 Use `/autosettings` to customize notifications"
        
        return f"{mention}{message}"
    
    # ==================== ENGAGEMENT TRACKING ====================
    
    async def _track_engagement(self, message, channel_id: str):
        """Track reactions to measure engagement"""
        try:
            # Wait for reactions (5 minutes)
            await asyncio.sleep(300)
            
            # Refresh message to get latest reactions
            try:
                message = await message.channel.fetch_message(message.id)
            except:
                return
            
            # Count reactions
            reaction_count = sum(reaction.count for reaction in message.reactions)
            
            # Store engagement data
            self.engagement_data[channel_id].append(reaction_count)
            
            # Keep only last 50 entries
            if len(self.engagement_data[channel_id]) > 50:
                self.engagement_data[channel_id] = self.engagement_data[channel_id][-50:]
            
            # Update config's active users
            config = self.get_channel_config(channel_id)
            if config and reaction_count > 0:
                # This is a simplified version - in reality you'd track specific users
                config.active_users.add(f"engaged_{datetime.now().timestamp()}")
            
            await self.log_activity(channel_id, f"Engagement tracked: {reaction_count} reactions")
            
        except Exception as e:
            self.logger.error(f"❌ Error tracking engagement: {e}")
    
    def _get_channel_engagement_level(self, channel_id: str) -> EngagementLevel:
        """Get engagement level for channel"""
        if channel_id not in self.engagement_data or not self.engagement_data[channel_id]:
            return EngagementLevel.MEDIUM
        
        recent_engagements = self.engagement_data[channel_id][-10:]  # Last 10 quotes
        if not recent_engagements:
            return EngagementLevel.MEDIUM
        
        avg_engagement = sum(recent_engagements) / len(recent_engagements)
        
        if avg_engagement < 1:
            return EngagementLevel.LOW
        elif avg_engagement <= 3:
            return EngagementLevel.MEDIUM
        else:
            return EngagementLevel.HIGH
    
    async def _engagement_analyzer(self):
        """Periodically analyze engagement data"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                for channel_id in list(self.engagement_data.keys()):
                    if not self.engagement_data[channel_id]:
                        continue
                    
                    avg_engagement = sum(self.engagement_data[channel_id]) / len(self.engagement_data[channel_id])
                    
                    # Update engagement rate in stats
                    if self.stats.total_quotes_sent > 0:
                        total_reactions = sum(sum(engagements) for engagements in self.engagement_data.values())
                        self.stats.engagement_rate = total_reactions / self.stats.total_quotes_sent
                    
                    # Log low engagement channels
                    if avg_engagement < self.min_engagement_threshold:
                        config = self.get_channel_config(channel_id)
                        if config:
                            await self.log_activity(
                                channel_id, 
                                f"Low engagement detected: {avg_engagement:.2f}"
                            )
                
                await self.save_data()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Engagement analyzer error: {e}")
                await asyncio.sleep(300)
    
    # ==================== ADAPTIVE SCHEDULING ====================
    
    async def _adaptive_schedule_adjuster(self):
        """Adjust schedules based on engagement"""
        if not self.enable_adaptive_scheduling:
            return
        
        while self.is_running:
            try:
                await asyncio.sleep(86400)  # Run once per day
                
                for config in self.get_active_channels():
                    engagement_level = self._get_channel_engagement_level(config.channel_id)
                    
                    # Adjust schedule based on engagement
                    if engagement_level == EngagementLevel.HIGH:
                        # High engagement: add more times
                        if len(config.schedule_times) < 8:
                            new_time = self._get_optimal_time(config)
                            if new_time and new_time not in config.schedule_times:
                                config.schedule_times.append(new_time)
                                await self.log_activity(
                                    config.channel_id,
                                    f"Added new schedule time: {new_time} (high engagement)"
                                )
                    
                    elif engagement_level == EngagementLevel.LOW:
                        # Low engagement: reduce frequency
                        if len(config.schedule_times) > 2:
                            removed = config.schedule_times.pop()
                            await self.log_activity(
                                config.channel_id,
                                f"Removed schedule time: {removed} (low engagement)"
                            )
                
                await self.save_data()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Adaptive scheduler error: {e}")
    
    def _get_optimal_time(self, config: ChannelConfig) -> Optional[str]:
        """Get optimal time for scheduling based on engagement patterns"""
        try:
            # Analyze best times based on engagement
            if not self.engagement_data.get(config.channel_id):
                return None
            
            # Simple algorithm: find hours with highest engagement
            hour_engagement = defaultdict(int)
            
            # In production, you would analyze actual engagement times
            # This is a simplified version
            
            # Default to adding evening time if not present
            existing_times = [int(t.split(':')[0]) for t in config.schedule_times]
            
            for hour in [20, 21, 22]:  # Evening hours
                if hour not in existing_times:
                    return f"{hour:02d}:00"
            
            return None
            
        except Exception:
            return None
    
    # ==================== STATISTICS & REPORTING ====================
    
    async def _stats_updater(self):
        """Update statistics periodically"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Update most active channels
                active_channels = []
                for config in self.channel_configs.values():
                    if config.enabled and config.total_sent > 0:
                        active_channels.append((config.channel_id, config.total_sent))
                
                active_channels.sort(key=lambda x: x[1], reverse=True)
                self.stats.most_active_channels = active_channels[:10]
                
                # Update total active channels
                self.stats.total_channels_active = len(self.get_active_channels())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Stats updater error: {e}")
    
    def get_system_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        return {
            'total_quotes_sent': self.stats.total_quotes_sent,
            'total_channels_active': self.stats.total_channels_active,
            'quotes_by_hour': dict(self.stats.quotes_by_hour),
            'quotes_by_category': dict(self.stats.quotes_by_category),
            'engagement_rate': self.stats.engagement_rate,
            'most_active_channels': self.stats.most_active_channels,
            'total_config_channels': len(self.channel_configs)
        }
    
    def get_channel_stats(self, channel_id: str) -> Optional[Dict]:
        """Get statistics for specific channel"""
        config = self.get_channel_config(channel_id)
        if not config:
            return None
        
        engagement_level = self._get_channel_engagement_level(channel_id)
        
        return {
            'channel_id': channel_id,
            'enabled': config.enabled,
            'schedule_times': config.schedule_times,
            'total_sent': config.total_sent,
            'last_sent': config.last_sent.isoformat() if config.last_sent else None,
            'active_users': len(config.active_users),
            'engagement_level': engagement_level.value,
            'cooldown_minutes': config.cooldown_minutes,
            'quote_language': config.quote_language,
            'categories': config.categories
        }
    
    async def generate_daily_report(self) -> str:
        """Generate daily report"""
        stats = self.get_system_stats()
        
        report = "**📊 Auto Quotes Daily Report**\n\n"
        report += f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n"
        report += f"📨 Total Quotes Sent: {stats['total_quotes_sent']}\n"
        report += f"🔔 Active Channels: {stats['total_channels_active']}\n"
        report += f"❤️ Engagement Rate: {stats['engagement_rate']:.2f} reactions/quote\n\n"
        
        report += "**🏆 Top 5 Active Channels:**\n"
        for i, (channel_id, count) in enumerate(stats['most_active_channels'][:5], 1):
            report += f"{i}. <#{channel_id}>: {count} quotes\n"
        
        report += "\n**⏰ Quotes by Hour:**\n"
        for hour in sorted(stats['quotes_by_hour'].keys()):
            if stats['quotes_by_hour'][hour] > 0:
                report += f"{hour:02d}:00 - {stats['quotes_by_hour'][hour]} quotes\n"
        
        return report
    
    # ==================== BOT COMMAND HANDLERS ====================
    
    async def handle_auto_settings_command(self, ctx):
        """Handle /autosettings command"""
        try:
            channel_id = str(ctx.channel.id)
            config = self.get_channel_config(channel_id)
            
            if not config:
                # Create default config
                self.add_channel(channel_id)
                config = self.get_channel_config(channel_id)
            
            # Format settings message
            settings_msg = "**🔧 Auto Quotes Settings**\n\n"
            settings_msg += f"📌 **Channel:** <#{channel_id}>\n"
            settings_msg += f"✅ **Status:** {'Enabled' if config.enabled else 'Disabled'}\n"
            settings_msg += f"⏰ **Schedule Times:** {', '.join(config.schedule_times)}\n"
            settings_msg += f"🌐 **Language:** {config.quote_language}\n"
            settings_msg += f"🏷️ **Categories:** {', '.join(config.categories)}\n"
            settings_msg += f"⏱️ **Cooldown:** {config.cooldown_minutes} minutes\n"
            settings_msg += f"📊 **Quotes Sent:** {config.total_sent}\n"
            settings_msg += f"👥 **Active Users:** {len(config.active_users)}\n\n"
            
            settings_msg += "**Commands:**\n"
            settings_msg += "`/autoon` - Enable auto quotes\n"
            settings_msg += "`/autooff` - Disable auto quotes\n"
            settings_msg += "`/settime HH:MM` - Add schedule time\n"
            settings_msg += "`/setlang bn/en` - Set quote language\n"
            settings_msg += "`/setcooldown MINUTES` - Set cooldown\n"
            
            await ctx.send(settings_msg)
            
        except Exception as e:
            self.logger.error(f"❌ Auto settings command error: {e}")
            await ctx.send("Settings load করতে সমস্যা হয়েছে।")
    
    async def handle_auto_on_command(self, ctx):
        """Handle /autoon command"""
        try:
            channel_id = str(ctx.channel.id)
            
            if channel_id not in self.channel_configs:
                self.add_channel(channel_id)
            
            self.update_channel_config(channel_id, enabled=True)
            
            await ctx.send("✅ Auto quotes enabled for this channel!")
            await self.log_activity(channel_id, "Auto quotes enabled via command")
            
        except Exception as e:
            self.logger.error(f"❌ Auto on command error: {e}")
            await ctx.send("Enable করতে সমস্যা হয়েছে।")
    
    async def handle_auto_off_command(self, ctx):
        """Handle /autooff command"""
        try:
            channel_id = str(ctx.channel.id)
            
            if channel_id in self.channel_configs:
                self.update_channel_config(channel_id, enabled=False)
                await ctx.send("⏹️ Auto quotes disabled for this channel.")
                await self.log_activity(channel_id, "Auto quotes disabled via command")
            else:
                await ctx.send("❌ Auto quotes not configured for this channel.")
            
        except Exception as e:
            self.logger.error(f"❌ Auto off command error: {e}")
            await ctx.send("Disable করতে সমস্যা হয়েছে।")
    
    async def handle_set_time_command(self, ctx, time_str: str):
        """Handle /settime command"""
        try:
            # Validate time format
            try:
                hour, minute = map(int, time_str.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
            except:
                await ctx.send("❌ Invalid time format. Use HH:MM (e.g., 09:30)")
                return
            
            channel_id = str(ctx.channel.id)
            config = self.get_channel_config(channel_id)
            
            if not config:
                await ctx.send("❌ Auto quotes not configured. Use `/autoon` first.")
                return
            
            if time_str in config.schedule_times:
                await ctx.send("ℹ️ This time is already in schedule.")
                return
            
            config.schedule_times.append(time_str)
            config.schedule_times.sort()
            
            await self.save_data()
            await ctx.send(f"✅ Added schedule time: {time_str}")
            await self.log_activity(channel_id, f"Added schedule time: {time_str}")
            
        except Exception as e:
            self.logger.error(f"❌ Set time command error: {e}")
            await ctx.send("Time সেট করতে সমস্যা হয়েছে।")
    
    async def handle_set_lang_command(self, ctx, language: str):
        """Handle /setlang command"""
        try:
            valid_langs = ["bn", "en", "hi"]
            
            if language not in valid_langs:
                await ctx.send(f"❌ Invalid language. Available: {', '.join(valid_langs)}")
                return
            
            channel_id = str(ctx.channel.id)
            config = self.get_channel_config(channel_id)
            
            if not config:
                await ctx.send("❌ Auto quotes not configured. Use `/autoon` first.")
                return
            
            self.update_channel_config(channel_id, quote_language=language)
            
            lang_names = {"bn": "বাংলা", "en": "English", "hi": "Hindi"}
            await ctx.send(f"✅ Quote language set to: {lang_names[language]}")
            await self.log_activity(channel_id, f"Language set to: {language}")
            
        except Exception as e:
            self.logger.error(f"❌ Set lang command error: {e}")
            await ctx.send("Language সেট করতে সমস্যা হয়েছে।")
    
    async def handle_force_quote_command(self, ctx):
        """Handle /forcequote command (admin)"""
        try:
            channel_id = str(ctx.channel.id)
            
            success = await self.send_auto_quote(channel_id, force=True)
            
            if success:
                await ctx.send("✅ Manual quote sent!")
            else:
                await ctx.send("❌ Failed to send quote. Check logs.")
            
        except Exception as e:
            self.logger.error(f"❌ Force quote command error: {e}")
            await ctx.send("Quote send করতে সমস্যা হয়েছে।")
    
    async def handle_auto_stats_command(self, ctx):
        """Handle /autostats command"""
        try:
            channel_id = str(ctx.channel.id)
            stats = self.get_channel_stats(channel_id)
            
            if not stats:
                await ctx.send("❌ No stats available. Enable auto quotes first.")
                return
            
            # Format stats
            stats_msg = "**📊 Auto Quotes Statistics**\n\n"
            stats_msg += f"📌 **Channel:** <#{channel_id}>\n"
            stats_msg += f"📨 **Total Sent:** {stats['total_sent']}\n"
            stats_msg += f"⏰ **Last Sent:** {stats['last_sent'] or 'Never'}\n"
            stats_msg += f"👥 **Active Users:** {stats['active_users']}\n"
            stats_msg += f"📈 **Engagement Level:** {stats['engagement_level'].upper()}\n"
            stats_msg += f"⏱️ **Cooldown:** {stats['cooldown_minutes']} minutes\n\n"
            
            # Add system stats if admin
            if ctx.author.guild_permissions.administrator:
                system_stats = self.get_system_stats()
                stats_msg += "**📈 System Stats:**\n"
                stats_msg += f"Total Quotes Sent: {system_stats['total_quotes_sent']}\n"
                stats_msg += f"Active Channels: {system_stats['total_channels_active']}\n"
                stats_msg += f"Engagement Rate: {system_stats['engagement_rate']:.2f}\n"
            
            await ctx.send(stats_msg)
            
        except Exception as e:
            self.logger.error(f"❌ Auto stats command error: {e}")
            await ctx.send("Statistics load করতে সমস্যা হয়েছে।")
    
    # ==================== ADMIN FUNCTIONS ====================
    
    async def handle_admin_report_command(self, ctx):
        """Handle /autoreport command (admin only)"""
        try:
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ Admin permission required.")
                return
            
            report = await self.generate_daily_report()
            await ctx.send(report)
            
        except Exception as e:
            self.logger.error(f"❌ Admin report error: {e}")
            await ctx.send("Report generate করতে সমস্যা হয়েছে।")
    
    async def handle_reset_channel_command(self, ctx, channel_mention: str = None):
        """Handle /resetauto command (admin)"""
        try:
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ Admin permission required.")
                return
            
            if channel_mention:
                # Extract channel ID from mention
                channel_id = channel_mention.strip('<>#')
            else:
                channel_id = str(ctx.channel.id)
            
            if channel_id in self.channel_configs:
                self.remove_channel(channel_id)
                await ctx.send(f"✅ Reset auto quotes for channel: <#{channel_id}>")
            else:
                await ctx.send(f"❌ Channel not found in auto quotes: <#{channel_id}>")
            
        except Exception as e:
            self.logger.error(f"❌ Reset channel error: {e}")
            await ctx.send("Reset করতে সমস্যা হয়েছে।")


# ==================== FACTORY FUNCTION ====================

def setup(bot):
    """Setup function for bot integration"""
    auto_quotes = AutoQuotes(bot)
    return auto_quotes
# AutoQuoteSystem কে AutoQuotes এর alias হিসেবে রাখুন
AutoQuoteSystem = AutoQuotes
