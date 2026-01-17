"""
Advanced Welcome System for Roastify Bot
Multi-language, Image-based, Smart Responses
"""

import random
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from telegram import Update, Chat, ChatMember, ChatMemberUpdated
from telegram.ext import ContextTypes
from config import Config
from utils.logger import logger, log_info, log_error
from utils.time_manager import TimeManager
from utils.helpers import Helpers
from utils.text_processor import TextProcessor
from database.storage import StorageManager
from database.models import User, Chat as ChatModel
from image_engine.image_generator import image_generator
from roast_engine.roaster import RoastEngine

class AdvancedWelcomeSystem:
    """এডভান্সড ওয়েলকাম সিস্টেম - সম্পূর্ণ প্রোফেশনাল"""
    
    def __init__(self):
        self.roast_engine = RoastEngine()
        self.text_processor = TextProcessor()
        
        # Welcome message libraries
        self.welcome_libraries = self._load_welcome_libraries()
        
        # User tracking for personalized welcomes
        self.user_welcome_history = {}  # user_id -> welcome_count
        self.group_welcome_stats = {}   # chat_id -> welcome_count
        
        # Cooldown tracking
        self.welcome_cooldowns = {}     # (chat_id, user_id) -> last_welcome_time
        
        # Welcome templates with images
        self.welcome_templates = self._load_welcome_templates()
        
        logger.info("✅ AdvancedWelcomeSystem initialized")
    
    def _load_welcome_libraries(self) -> Dict[str, List[str]]:
        """ওয়েলকাম লাইব্রেরি লোড করে"""
        return {
            "bengali": [
                "স্বাগতম {}! আশা করি এখানে ভালো সময় কাটাবেন! 😊",
                "{} এসেছেন! গ্রুপে আনন্দময় থাকুন! 🎉",
                "অভ্যর্থনা {}! গ্রুপে আপনার আগমন সাদরে গ্রহণ করা হলো! 🤗",
                "হ্যালো {}! আশা করি এখানে অনেক মজা পাবেন! 😄",
                "{} কে গ্রুপে স্বাগতম! চলুন একসাথে মজা করি! 🥳",
                "গ্রুপে {} এর আগমন হোক আনন্দের! 🎊",
                "স্বাগতম মহান {}! আশা করি এখানে ভালো লাগবে! 👑",
                "{} এসেছেন! এবার গ্রুপে রঙিন হয়ে উঠবে! 🌈",
                "অভিনন্দন {}! গ্রুপের নতুন সদস্য হয়ে উঠলেন! 🏆",
                "হ্যালো ও হ্যালো {}! গ্রুপে আপনার জন্য শুভকামনা! 🙏"
            ],
            "english": [
                "Welcome {}! Hope you have a great time here! 😊",
                "{} has joined! Enjoy your stay in the group! 🎉",
                "Greetings {}! Your arrival is warmly welcomed! 🤗",
                "Hello {}! Hope you have lots of fun here! 😄",
                "Welcome {} to the group! Let's have fun together! 🥳",
                "May {}'s arrival bring joy to the group! 🎊",
                "Welcome the great {}! Hope you like it here! 👑",
                "{} has arrived! Now the group will become colorful! 🌈",
                "Congratulations {}! You've become a new member! 🏆",
                "Hello and hello {}! Best wishes for you in the group! 🙏"
            ],
            "funny": [
                "ওহো! {} এসেছেন! এবার গ্রুপে রোস্টিং শুরু হবে! 😈",
                "{} কে দেখে আমার রোস্টিং মেশিন চালু হলো! 🔥",
                "স্বাগতম {}! রোস্টের জন্য প্রস্তুত থাকুন! 💀",
                "{} এসেছেন! এবার গ্রুপে মজা বাড়বে! 🤣",
                "হ্যালো {}! আমি রোস্টিফাই, তোমার অপেক্ষায় ছিলাম! 😏",
                "{} এর আগমন! আমার বট ব্রেন কাজ শুরু করলো! 🧠",
                "স্বাগতম {}! তোমার জন্য বিশেষ রোস্ট প্রস্তুত! 🍳",
                "{} এসেছেন! এবার গ্রুপের তাপমাত্রা বাড়বে! 🌡️",
                "অভ্যর্থনা {}! রোস্টের আসর শুরু হোক! 🎭",
                "{} কে গ্রুপে স্বাগতম! মজা হবে ডবল! 🎪"
            ],
            "formal": [
                "গ্রুপে {} এর যোগদানে আমরা আনন্দিত। স্বাগতম জানাই। 🤝",
                "{} কে গ্রুপের সদস্য হিসেবে পেয়ে আমরা গর্বিত। 🏛️",
                "অভিনন্দন {}। গ্রুপের নিয়মাবলী মেনে চলবেন। 📜",
                "{} এর আগমন গ্রুপের জন্য গৌরবের। সম্মানিত অতিথি। 👔",
                "গ্রুপে {} কে স্বাগতম। সম্মান ও শৃঙ্খলা বজায় রাখুন। ⚖️"
            ],
            "custom": [
                "🎊 **বিশেষ স্বাগতম {}!** 🎊\nআপনার জন্য বিশেষ অফার প্রস্তুত!",
                "🌟 **স্টার মেম্বার {} আসছেন!** 🌟\nগ্রুপ আলোকিত হলো!",
                "👑 **রাজকীয় অভ্যর্থনা {}!** 👑\nআপনার আগমন সম্মানিত!",
                "🚀 **{} এর মহাশূন্য আগমন!** 🚀\nগ্রুপে নতুন দিগন্ত!",
                "🎪 **সার্কাস শুরু! {} এসেছেন!** 🎪\nমজা হবে দ্বিগুণ!"
            ]
        }
    
    def _load_welcome_templates(self) -> List[Dict]:
        """ওয়েলকাম টেমপ্লেট লোড করে"""
        return [
            {
                "id": "welcome_1",
                "name": "Classic Welcome",
                "primary_color": (41, 128, 185),
                "secondary_color": (52, 152, 219),
                "border_color": (189, 195, 199),
                "theme": "classic"
            },
            {
                "id": "welcome_2", 
                "name": "Funny Welcome",
                "primary_color": (155, 89, 182),
                "secondary_color": (142, 68, 173),
                "border_color": (210, 180, 222),
                "theme": "funny"
            },
            {
                "id": "welcome_3",
                "name": "Royal Welcome",
                "primary_color": (241, 196, 15),
                "secondary_color": (243, 156, 18),
                "border_color": (245, 176, 65),
                "theme": "royal"
            },
            {
                "id": "welcome_4",
                "name": "Night Welcome",
                "primary_color": (52, 73, 94),
                "secondary_color": (44, 62, 80),
                "border_color": (127, 140, 141),
                "theme": "night"
            },
            {
                "id": "welcome_5",
                "name": "Party Welcome",
                "primary_color": (231, 76, 60),
                "secondary_color": (192, 57, 43),
                "border_color": (245, 183, 177),
                "theme": "party"
            }
        ]
    
    async def handle_bot_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """বট স্টার্ট হলে ওয়েলকাম মেসেজ"""
        try:
            user = update.effective_user
            chat = update.effective_chat
            
            # Store user in database
            StorageManager.get_or_create_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            # Select welcome type based on time
            welcome_type = self._select_welcome_type("bot_start", user.id)
            
            # Get welcome message
            welcome_msg = self._get_welcome_message(welcome_type, user.first_name, user.id)
            
            # Create welcome image
            image = await self._create_welcome_image(
                user_name=user.first_name,
                welcome_text=welcome_msg,
                welcome_type=welcome_type,
                user_id=user.id
            )
            
            if image:
                # Save and send image
                image_path = image_generator.save_image(image)
                
                caption = (
                    f"🤖 *রোস্টিফাই বট - Professional Edition*\n\n"
                    f"{welcome_msg}\n\n"
                    f"📱 *কীভাবে ব্যবহার করবেন:*\n"
                    f"• শুধু মেসেজ লিখুন, রোস্ট ইমেজ পাবেন\n"
                    f"• গ্রুপে মেনশন করুন রোস্টের জন্য\n"
                    f"• ভোট দিয়ে রেটিং দিন\n\n"
                    f"🔧 *কমান্ডস:* `/help` দেখুন\n"
                    f"👑 *ওনার:* {Config.OWNER_ID}\n"
                    f"🤖 *বট:* @{Config.BOT_USERNAME}"
                )
                
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=chat.id,
                        photo=photo,
                        caption=caption,
                        parse_mode="Markdown"
                    )
            else:
                # Fallback to text
                text_response = (
                    f"🤖 *রোস্টিফাই বট - Professional Edition*\n\n"
                    f"{welcome_msg}\n\n"
                    f"আমি রোস্টিফাই বট। শুধু মেসেজ লিখুন, "
                    f"রোস্ট ইমেজ পাবেন!\n\n"
                    f"বট: @{Config.BOT_USERNAME}\n"
                    f"সাহায্য: /help"
                )
                
                await update.message.reply_text(text_response, parse_mode="Markdown")
            
            # Update statistics
            self._update_welcome_stats(user.id, chat.id, "bot_start")
            
            log_info(f"Bot start welcome sent to user {user.id}")
            
        except Exception as e:
            log_error(f"Error in handle_bot_start: {e}")
            await self._send_fallback_welcome(update, context)
    
    async def handle_bot_added_to_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """বট গ্রুপে অ্যাড হলে"""
        try:
            chat = update.effective_chat
            
            if not chat:
                return
            
            # Store chat in database
            StorageManager.get_or_create_chat(
                chat_id=chat.id,
                chat_type=chat.type,
                title=chat.title
            )
            
            # Select welcome type for group
            welcome_type = "group_welcome"
            
            # Get group welcome message
            group_name = chat.title or "এই গ্রুপ"
            welcome_msg = self._get_group_welcome_message(group_name)
            
            # Create group welcome image
            image = await self._create_group_welcome_image(
                group_name=group_name,
                welcome_text=welcome_msg,
                chat_id=chat.id
            )
            
            caption = (
                f"🤖 *রোস্টিফাই বট গ্রুপে যুক্ত হয়েছে!*\n\n"
                f"{welcome_msg}\n\n"
                f"📋 *গ্রুপে ব্যবহার:*\n"
                f"• যেকোনো মেসেজ লিখুন → রোস্ট ইমেজ\n"
                f"• @মেনশন করুন রোস্টের জন্য\n"
                f"• ভোট দিয়ে রেটিং দিন\n\n"
                f"⚙️ *সেটিংস:*\n"
                f"• মিনিমাম টেক্সট: {Config.MIN_INPUT_LENGTH} অক্ষর\n"
                f"• ভোট সময়: {Config.VOTE_WINDOW} সেকেন্ড\n"
                f"• ইমেজ সাইজ: {Config.IMAGE_WIDTH}x{Config.IMAGE_HEIGHT}\n\n"
                f"🤖 বট: @{Config.BOT_USERNAME}\n"
                f"❓ সাহায্য: /help গ্রুপে"
            )
            
            if image:
                image_path = image_generator.save_image(image)
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=chat.id,
                        photo=photo,
                        caption=caption,
                        parse_mode="Markdown"
                    )
            else:
                await update.message.reply_text(caption, parse_mode="Markdown")
            
            # Add welcome reactions
            await self._add_welcome_reactions(context, chat.id)
            
            log_info(f"Bot added to group {chat.id} ({chat.title})")
            
        except Exception as e:
            log_error(f"Error in handle_bot_added_to_group: {e}")
            fallback_msg = (
                "🤖 রোস্টিফাই বট গ্রুপে যুক্ত হয়েছে!\n\n"
                "শুধু মেসেজ লিখুন, রোস্ট ইমেজ পাবেন!\n\n"
                f"বট: @{Config.BOT_USERNAME}\n"
                "সাহায্য: /help"
            )
            await update.message.reply_text(fallback_msg)
    
    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """নতুন মেম্বার জয়েন করলে"""
        try:
            chat = update.effective_chat
            
            if not chat:
                return
            
            new_members = update.message.new_chat_members
            
            # Check if bot itself was added
            for member in new_members:
                if member.id == context.bot.id:
                    await self.handle_bot_added_to_group(update, context)
                    return
            
            # Welcome each new member
            for member in new_members:
                if member.is_bot:
                    continue  # Skip other bots
                
                # Check cooldown
                if not self._check_welcome_cooldown(member.id, chat.id):
                    continue
                
                # Store user in database
                StorageManager.get_or_create_user(
                    user_id=member.id,
                    username=member.username,
                    first_name=member.first_name,
                    last_name=member.last_name
                )
                
                # Check if returning member
                is_returning = await self._is_returning_member(member.id, chat.id)
                
                # Select welcome type
                if is_returning:
                    welcome_type = "returning_member"
                else:
                    welcome_type = "new_member"
                
                # Get personalized welcome message
                welcome_msg = self._get_personalized_welcome(
                    member_name=member.first_name,
                    member_id=member.id,
                    chat_name=chat.title,
                    welcome_type=welcome_type
                )
                
                # Create welcome image
                image = await self._create_member_welcome_image(
                    member_name=member.first_name,
                    welcome_text=welcome_msg,
                    member_id=member.id,
                    chat_id=chat.id,
                    is_returning=is_returning
                )
                
                if image:
                    image_path = image_generator.save_image(image)
                    with open(image_path, 'rb') as photo:
                        sent_message = await context.bot.send_photo(
                            chat_id=chat.id,
                            photo=photo,
                            caption=welcome_msg
                        )
                else:
                    sent_message = await update.message.reply_text(welcome_msg)
                
                # Add reactions to welcome message
                await self._add_member_welcome_reactions(context, sent_message, is_returning)
                
                # Update statistics
                self._update_welcome_stats(member.id, chat.id, welcome_type)
                
                # Update cooldown
                self._update_welcome_cooldown(member.id, chat.id)
                
                log_info(f"Welcomed member {member.id} in chat {chat.id}")
                
                # Small delay between welcomes
                await asyncio.sleep(1)
            
        except Exception as e:
            log_error(f"Error in handle_new_chat_members: {e}")
    
    def _select_welcome_type(self, context: str, user_id: int) -> str:
        """ওয়েলকাম টাইপ সিলেক্ট করে"""
        # Get user's welcome history
        welcome_count = self.user_welcome_history.get(user_id, 0)
        
        if context == "bot_start":
            if welcome_count == 0:
                return "bengali"
            elif welcome_count % 3 == 0:
                return "custom"
            else:
                return random.choice(["bengali", "english", "funny"])
        
        elif context == "new_member":
            hour = TimeManager.get_current_hour()
            
            if 6 <= hour < 12:
                return "bengali"
            elif 12 <= hour < 18:
                return "english"
            elif 18 <= hour < 24:
                return "funny"
            else:
                return "formal"
        
        else:
            return random.choice(list(self.welcome_libraries.keys()))
    
    def _get_welcome_message(self, welcome_type: str, user_name: str, user_id: int) -> str:
        """ওয়েলকাম মেসেজ তৈরি করে"""
        library = self.welcome_libraries.get(welcome_type, self.welcome_libraries["bengali"])
        
        # Select template based on user ID for variety
        template_index = user_id % len(library)
        template = library[template_index]
        
        return template.format(user_name)
    
    def _get_group_welcome_message(self, group_name: str) -> str:
        """গ্রুপ ওয়েলকাম মেসেজ তৈরি করে"""
        templates = [
            f"🎊 **{group_name} গ্রুপে রোস্টিফাই যুক্ত হয়েছে!**\nএখন থেকে যেকোনো মেসেজের জন্য রোস্ট ইমেজ পাবেন!",
            f"🤖 **রোস্টিফাই {group_name} গ্রুপে হাজির!**\nমেসেজ লিখুন, রোস্ট পাবেন, মজা করুন!",
            f"🔥 **{group_name} গ্রুপে রোস্টিং শুরু!**\nআমি রোস্টিফাই, তোমার অপেক্ষায়!",
            f"🎪 **মজার আসর শুরু!**\n{group_name} গ্রুপে রোস্টিফাই একটিভ!",
            f"👑 **রাজকীয় অভ্যর্থনা!**\n{group_name} গ্রুপে রোস্টিফাই উপস্থিত!"
        ]
        
        return random.choice(templates)
    
    def _get_personalized_welcome(self, member_name: str, member_id: int, 
                                 chat_name: str, welcome_type: str) -> str:
        """পার্সোনালাইজড ওয়েলকাম মেসেজ তৈরি করে"""
        hour = TimeManager.get_current_hour()
        
        if welcome_type == "returning_member":
            templates = [
                f"👋 ফিরে আসার জন্য ধন্যবাদ {member_name}! আবারও স্বাগতম! 🎉",
                f"😊 {member_name} আবার গ্রুপে ফিরেছে! মিস করেছিলাম! 🤗",
                f"🎊 ওহো! {member_name} ফিরেছে! এবার মজা বাড়বে! 🥳",
                f"🤝 আবারও স্বাগতম {member_name}! গ্রুপে আপনার প্রত্যাবর্তনে আনন্দিত! 🌟",
                f"🔥 {member_name} ফিরেছে! রোস্টের জন্য প্রস্তুত? 😈"
            ]
        else:
            # Time-based welcome messages
            if 5 <= hour < 12:
                templates = [
                    f"🌅 সুপ্রভাত {member_name}! {chat_name} গ্রুপে স্বাগতম!",
                    f"☀️ সকালবেলা স্বাগতম {member_name}! গ্রুপে আনন্দে থাকুন!",
                    f"🌞 শুভ সকাল {member_name}! গ্রুপে আপনার আগমন মঙ্গলময় হোক!"
                ]
            elif 12 <= hour < 17:
                templates = [
                    f"🌤️ শুভ অপরাহ্ন {member_name}! {chat_name} গ্রুপে স্বাগতম!",
                    f"😊 দুপুরবেলা স্বাগতম {member_name}! গ্রুপে ভালো সময় কাটান!",
                    f"🎪 হ্যালো {member_name}! গ্রুপে মজার সময়ের শুরু!"
                ]
            elif 17 <= hour < 21:
                templates = [
                    f"🌆 শুভ সন্ধ্যা {member_name}! {chat_name} গ্রুপে স্বাগতম!",
                    f"🌟 সন্ধ্যাবেলা অভ্যর্থনা {member_name}! গ্রুপ আলোকিত হলো!",
                    f"🎊 ইভনিং {member_name}! গ্রুপে আপনার জন্য বিশেষ স্বাগতম!"
                ]
            else:
                templates = [
                    f"🌙 শুভ রাত্রি {member_name}! {chat_name} গ্রুপে স্বাগতম!",
                    f"🌠 রাতের তারা হয়ে আসছেন {member_name}! স্বাগতম!",
                    f"🌜 গভীর রাতে স্বাগতম {member_name}! গ্রুপে শান্তি বজায় রাখুন!"
                ]
        
        # Add member-specific touch
        member_specific = member_id % 10
        if member_specific < 3:
            return random.choice(templates) + "\n\n🎁 আপনার জন্য একটি বিশেষ রোস্ট প্রস্তুত!"
        elif member_specific < 6:
            return random.choice(templates) + "\n\n⭐ আপনি আমাদের বিশেষ সদস্য!"
        else:
            return random.choice(templates) + "\n\n😊 আশা করি এখানে ভালো সময় কাটাবেন!"
    
    async def _create_welcome_image(self, user_name: str, welcome_text: str, 
                                   welcome_type: str, user_id: int) -> Optional:
        """ওয়েলকাম ইমেজ তৈরি করে"""
        try:
            # Select template
            template = self._select_welcome_template(welcome_type, user_id)
            
            # Prepare text
            primary_text = f"স্বাগতম {user_name}!"
            secondary_text = welcome_text.split('\n')[0]  # First line only
            
            # Create image
            image = image_generator.create_roast_image(
                primary_text=primary_text,
                secondary_text=secondary_text,
                user_id=user_id,
                roast_type="welcome"
            )
            
            return image
            
        except Exception as e:
            log_error(f"Error creating welcome image: {e}")
            return None
    
    async def _create_group_welcome_image(self, group_name: str, welcome_text: str, 
                                         chat_id: int) -> Optional:
        """গ্রুপ ওয়েলকাম ইমেজ তৈরি করে"""
        try:
            primary_text = f"{group_name} গ্রুপ"
            secondary_text = welcome_text.split('\n')[0]
            
            image = image_generator.create_roast_image(
                primary_text=primary_text,
                secondary_text=secondary_text,
                user_id=chat_id,  # Using chat_id as user_id for uniqueness
                roast_type="group_welcome"
            )
            
            return image
            
        except Exception as e:
            log_error(f"Error creating group welcome image: {e}")
            return None
    
    async def _create_member_welcome_image(self, member_name: str, welcome_text: str,
                                          member_id: int, chat_id: int, 
                                          is_returning: bool) -> Optional:
        """মেম্বার ওয়েলকাম ইমেজ তৈরি করে"""
        try:
            if is_returning:
                primary_text = f"ফিরে আসুন {member_name}!"
                roast_type = "returning"
            else:
                primary_text = f"স্বাগতম {member_name}!"
                roast_type = "welcome"
            
            secondary_text = welcome_text.split('\n')[0]
            
            image = image_generator.create_roast_image(
                primary_text=primary_text,
                secondary_text=secondary_text,
                user_id=member_id,
                roast_type=roast_type
            )
            
            return image
            
        except Exception as e:
            log_error(f"Error creating member welcome image: {e}")
            return None
    
    def _select_welcome_template(self, welcome_type: str, user_id: int) -> Dict:
        """ওয়েলকাম টেমপ্লেট সিলেক্ট করে"""
        # Filter templates by theme
        if welcome_type == "funny":
            templates = [t for t in self.welcome_templates if t["theme"] in ["funny", "party"]]
        elif welcome_type == "formal":
            templates = [t for t in self.welcome_templates if t["theme"] in ["classic", "night"]]
        elif welcome_type == "custom":
            templates = [t for t in self.welcome_templates if t["theme"] == "royal"]
        else:
            templates = self.welcome_templates
        
        # Select based on user ID for variety
        if templates:
            return templates[user_id % len(templates)]
        
        # Default template
        return self.welcome_templates[0]
    
    async def _add_welcome_reactions(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
        """ওয়েলকাম মেসেজে রিএকশন যোগ করে"""
        try:
            reactions = ["🤖", "🎉", "🔥", "😊", "👋", "🌟", "🎊", "🤝", "🥳", "👑"]
            selected = random.sample(reactions, min(4, len(reactions)))
            
            # This would require message_id, for now just log
            logger.info(f"Would add reactions {selected} to welcome message in chat {chat_id}")
            
        except Exception as e:
            log_error(f"Error adding welcome reactions: {e}")
    
    async def _add_member_welcome_reactions(self, context: ContextTypes.DEFAULT_TYPE, 
                                           message, is_returning: bool):
        """মেম্বার ওয়েলকামে রিএকশন যোগ করে"""
        try:
            if is_returning:
                reactions = ["👋", "😊", "🤗", "🌟", "🎉"]
            else:
                reactions = ["👋", "🎉", "🥳", "🌟", "🎊", "🤝", "😄", "👏"]
            
            selected = random.sample(reactions, min(3, len(reactions)))
            
            for emoji in selected:
                try:
                    await context.bot.set_message_reaction(
                        chat_id=message.chat_id,
                        message_id=message.message_id,
                        reaction=[{"type": "emoji", "emoji": emoji}]
                    )
                    await asyncio.sleep(0.3)
                except Exception as e:
                    logger.warning(f"Could not add reaction {emoji}: {e}")
                    
        except Exception as e:
            log_error(f"Error adding member welcome reactions: {e}")
    
    async def _is_returning_member(self, user_id: int, chat_id: int) -> bool:
        """মেম্বার রিটার্নিং কিনা চেক করে"""
        # This would check database for previous membership
        # For now, simple implementation
        return False
    
    def _check_welcome_cooldown(self, user_id: int, chat_id: int) -> bool:
        """ওয়েলকাম কুলডাউন চেক করে"""
        key = (chat_id, user_id)
        
        if key in self.welcome_cooldowns:
            last_welcome = self.welcome_cooldowns[key]
            time_diff = (TimeManager.get_current_time() - last_welcome).total_seconds()
            
            # 5 minutes cooldown for same user in same chat
            return time_diff >= 300
        
        return True
    
    def _update_welcome_cooldown(self, user_id: int, chat_id: int):
        """ওয়েলকাম কুলডাউন আপডেট করে"""
        key = (chat_id, user_id)
        self.welcome_cooldowns[key] = TimeManager.get_current_time()
    
    def _update_welcome_stats(self, user_id: int, chat_id: int, welcome_type: str):
        """ওয়েলকাম স্ট্যাটস আপডেট করে"""
        # Update user welcome count
        self.user_welcome_history[user_id] = self.user_welcome_history.get(user_id, 0) + 1
        
        # Update group stats
        if chat_id not in self.group_welcome_stats:
            self.group_welcome_stats[chat_id] = {"total": 0, "types": {}}
        
        self.group_welcome_stats[chat_id]["total"] += 1
        self.group_welcome_stats[chat_id]["types"][welcome_type] = \
            self.group_welcome_stats[chat_id]["types"].get(welcome_type, 0) + 1
    
    async def _send_fallback_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ফলব্যাক ওয়েলকাম পাঠায়"""
        try:
            fallback_messages = [
                "🤖 রোস্টিফাই বটে স্বাগতম! আমি রোস্ট তৈরি করি।",
                "👋 হ্যালো! আমি রোস্টিফাই, রোস্টের জন্য প্রস্তুত?",
                "🎉 স্বাগতম! মেসেজ লিখুন, রোস্ট ইমেজ পাবেন!",
                "😊 হাই! আমি রোস্টিফাই বট, সাহায্য চাইলে /help লিখুন।"
            ]
            
            await update.message.reply_text(random.choice(fallback_messages))
            
        except Exception as e:
            log_error(f"Error in fallback welcome: {e}")
    
    async def send_custom_welcome(self, chat_id: int, user_name: str, 
                                 welcome_type: str = "custom", 
                                 custom_message: str = None) -> bool:
        """কাস্টম ওয়েলকাম মেসেজ পাঠায়"""
        try:
            if custom_message:
                welcome_msg = custom_message
            else:
                welcome_msg = self._get_welcome_message(welcome_type, user_name, hash(user_name))
            
            # Create image
            image = await self._create_welcome_image(
                user_name=user_name,
                welcome_text=welcome_msg,
                welcome_type=welcome_type,
                user_id=hash(user_name)
            )
            
            if image:
                image_path = image_generator.save_image(image)
                with open(image_path, 'rb') as photo:
                    await self.application.bot.send_photo(
                        chat_id=chat_id,
                        photo=photo,
                        caption=welcome_msg
                    )
            else:
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=welcome_msg
                )
            
            return True
            
        except Exception as e:
            log_error(f"Error sending custom welcome: {e}")
            return False
    
    def get_welcome_stats(self, chat_id: int = None) -> Dict:
        """ওয়েলকাম স্ট্যাটস রিটার্ন করে"""
        if chat_id:
            return self.group_welcome_stats.get(chat_id, {"total": 0, "types": {}})
        
        total_users = len(self.user_welcome_history)
        total_welcomes = sum(self.user_welcome_history.values())
        
        return {
            "total_users": total_users,
            "total_welcomes": total_welcomes,
            "avg_welcomes_per_user": total_welcomes / max(total_users, 1),
            "active_chats": len(self.group_welcome_stats),
            "cooldown_active": len(self.welcome_cooldowns)
        }
    
    def cleanup_old_data(self, days: int = 7):
        """পুরানো ডাটা ক্লিনআপ করে"""
        try:
            cutoff_time = TimeManager.get_current_time() - timedelta(days=days)
            
            # Clean old cooldowns
            to_remove = []
            for key, last_time in self.welcome_cooldowns.items():
                if last_time < cutoff_time:
                    to_remove.append(key)
            
            for key in to_remove:
                del self.welcome_cooldowns[key]
            
            logger.info(f"Cleaned up {len(to_remove)} old welcome cooldowns")
            
        except Exception as e:
            log_error(f"Error cleaning welcome data: {e}")

# Global instance
welcome_system = AdvancedWelcomeSystem()
