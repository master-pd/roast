"""
Vote System for Roastify Bot
Fully Fixed
"""

import random
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import Config
from utils.logger import logger
from utils.time_manager import TimeManager
from database.storage import StorageManager

class VoteSystem:
    """ভোট সিস্টেম ক্লাস - সম্পূর্ণ ফিক্সড"""
    
    def __init__(self):
        self.vote_options = {
            "funny": "🔥 Funny",
            "mid": "😐 Mid", 
            "savage": "💀 Savage"
        }
        
        # Track active votes
        self.active_votes = {}  # message_id -> vote_data
    
    def create_vote_keyboard(self, message_id: int) -> InlineKeyboardMarkup:
        """ভোট কিবোর্ড তৈরি করে"""
        keyboard = []
        
        for vote_type, vote_text in self.vote_options.items():
            callback_data = f"vote_{message_id}_{vote_type}"
            keyboard.append(
                [InlineKeyboardButton(vote_text, callback_data=callback_data)]
            )
        
        return InlineKeyboardMarkup(keyboard)
    
    async def add_vote_to_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                 message_id: int, chat_id: int):
        """মেসেজে ভোট অপশন অ্যাড করে"""
        try:
            keyboard = self.create_vote_keyboard(message_id)
            
            # Store vote info
            self.active_votes[message_id] = {
                "chat_id": chat_id,
                "user_id": update.effective_user.id if update.effective_user else 0,
                "timestamp": TimeManager.get_current_time(),
                "votes": {"funny": 0, "mid": 0, "savage": 0},
                "voters": set()
            }
            
            # Send vote message
            vote_message = await context.bot.send_message(
                chat_id=chat_id,
                text="কেমন লাগলো রোস্টটা? ভোট দাও!",
                reply_to_message_id=message_id,
                reply_markup=keyboard
            )
            
            # Schedule removal of vote options
            self._schedule_vote_removal(context, message_id, vote_message.message_id, chat_id)
            
            logger.info(f"Added vote to message {message_id} in chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Error adding vote: {e}")
    
    async def handle_vote_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ভোট ক্যালব্যাক হ্যান্ডল করে - ফিক্সড"""
        query = update.callback_query
        
        if not query or not query.data:
            return
        
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if not data.startswith("vote_"):
            return
        
        # Parse callback data
        try:
            _, message_id_str, vote_type = data.split("_")
            message_id = int(message_id_str)
        except:
            return
        
        # Check if vote is still active
        if message_id not in self.active_votes:
            try:
                await query.edit_message_text(text="ভোটের সময় শেষ! ⏰")
            except:
                pass
            return
        
        vote_data = self.active_votes[message_id]
        
        # Check vote window
        if hasattr(Config, 'VOTE_WINDOW') and Config.VOTE_WINDOW > 0:
            time_passed = (TimeManager.get_current_time() - vote_data["timestamp"]).total_seconds()
            if time_passed > Config.VOTE_WINDOW:
                try:
                    await query.edit_message_text(text="ভোটের সময় শেষ! ⏰")
                except:
                    pass
                del self.active_votes[message_id]
                return
        
        # Check if user already voted
        if user_id in vote_data["voters"]:
            await query.answer("তুমি ইতিমধ্যে ভোট দিয়েছ! ❌", show_alert=True)
            return
        
        # Check self-vote
        if hasattr(Config, 'SELF_VOTE_ALLOWED') and not Config.SELF_VOTE_ALLOWED:
            if user_id == vote_data.get("user_id", 0):
                await query.answer("নিজের পোস্টে ভোট দিতে পারবে না! 🙅", show_alert=True)
                return
        
        # Register vote
        vote_data["votes"][vote_type] = vote_data["votes"].get(vote_type, 0) + 1
        vote_data["voters"].add(user_id)
        
        # Save to database if available
        try:
            StorageManager.add_vote(user_id, message_id, vote_type, vote_data["chat_id"])
        except:
            pass
        
        # Update vote counts in message
        vote_text = self._format_vote_results(vote_data["votes"])
        
        try:
            await query.edit_message_text(
                text=f"ভোটের ফলাফল:\n{vote_text}",
                reply_markup=query.message.reply_markup
            )
        except:
            pass
        
        logger.info(f"User {user_id} voted {vote_type} on message {message_id}")
    
    def _format_vote_results(self, votes: Dict[str, int]) -> str:
        """ভোট রেজাল্ট ফরম্যাট করে"""
        total = sum(votes.values())
        if total == 0:
            return "এখনো কোনো ভোট পড়েনি! ⏳"
        
        results = []
        vote_texts = {
            "funny": "🔥 মজার",
            "mid": "😐 মাঝারি", 
            "savage": "💀 স্যাভেজ"
        }
        
        for vote_type, count in votes.items():
            percentage = (count / total) * 100 if total > 0 else 0
            text = vote_texts.get(vote_type, vote_type)
            results.append(f"{text}: {count} ({percentage:.1f}%)")
        
        return "\n".join(results)
    
    def _schedule_vote_removal(self, context: ContextTypes.DEFAULT_TYPE, 
                              original_message_id: int, vote_message_id: int, chat_id: int):
        """ভোট অপশন রিমুভ করার সময় নির্ধারণ করে"""
        async def remove_vote_options(context: ContextTypes.DEFAULT_TYPE):
            try:
                # Remove vote message
                await context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=vote_message_id
                )
                
                # Remove from active votes
                if original_message_id in self.active_votes:
                    del self.active_votes[original_message_id]
                
                logger.info(f"Removed vote options for message {original_message_id}")
                
            except Exception as e:
                logger.error(f"Error removing vote options: {e}")
        
        # Schedule removal after vote window
        vote_window = getattr(Config, 'VOTE_WINDOW', 300)
        context.job_queue.run_once(
            remove_vote_options,
            when=vote_window,
            name=f"remove_vote_{original_message_id}"
        )
