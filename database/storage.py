from contextlib import contextmanager
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .models import User, Chat, RoastLog, Vote, ReactionLog, TemplateStat, get_db
from utils.time_manager import TimeManager
from utils.logger import logger

class StorageManager:
    
    @staticmethod
    @contextmanager
    def get_session():
        """ডেটাবেস সেশন কনটেক্সট ম্যানেজার"""
        db = next(get_db())
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            db.close()
    
    # User Management
    @classmethod
    def get_or_create_user(cls, user_id: int, username: str = None, 
                          first_name: str = None, last_name: str = None) -> User:
        """ইউজার খুঁজে বা ক্রিয়েট করে"""
        with cls.get_session() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                db.add(user)
                logger.info(f"New user created: {user_id}")
            else:
                # Update user info if changed
                update_needed = False
                if username and user.username != username:
                    user.username = username
                    update_needed = True
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                    update_needed = True
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                    update_needed = True
                
                if update_needed:
                    user.updated_at = TimeManager.get_current_time()
            
            return user
    
    @classmethod
    def increment_user_roast_count(cls, user_id: int):
        """ইউজারের রোস্ট কাউন্ট বাড়ায়"""
        with cls.get_session() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                user.roast_count += 1
                user.last_roast_time = TimeManager.get_current_time()
    
    # Chat Management
    @classmethod
    def get_or_create_chat(cls, chat_id: int, chat_type: str = None, title: str = None) -> Chat:
        """চ্যাট খুঁজে বা ক্রিয়েট করে"""
        with cls.get_session() as db:
            chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
            
            if not chat:
                chat = Chat(
                    chat_id=chat_id,
                    chat_type=chat_type,
                    title=title
                )
                db.add(chat)
                logger.info(f"New chat added: {chat_id}")
            
            return chat
    
    # Roast Logging
    @classmethod
    def log_roast(cls, user_id: int, input_text: str, roast_type: str, 
                  template_used: str, chat_id: int = None):
        """রোস্ট লগ সেভ করে"""
        with cls.get_session() as db:
            roast_log = RoastLog(
                user_id=user_id,
                chat_id=chat_id,
                input_text=input_text[:500],  # Limit text length
                roast_type=roast_type,
                template_used=template_used
            )
            db.add(roast_log)
    
    # Vote Management
    @classmethod
    def add_vote(cls, user_id: int, message_id: int, vote_type: str, chat_id: int = None) -> bool:
        """ভোট সেভ করে"""
        with cls.get_session() as db:
            # Check if user already voted for this message
            existing_vote = db.query(Vote).filter(
                Vote.user_id == user_id,
                Vote.message_id == message_id
            ).first()
            
            if existing_vote:
                return False
            
            vote = Vote(
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                vote_type=vote_type
            )
            db.add(vote)
            
            # Update user vote count
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                user.vote_count += 1
            
            return True
    
    # Template Statistics
    @classmethod
    def update_template_stats(cls, template_name: str, vote_type: str = None):
        """টেমপ্লেট স্ট্যাট আপডেট করে"""
        with cls.get_session() as db:
            template = db.query(TemplateStat).filter(
                TemplateStat.template_name == template_name
            ).first()
            
            if not template:
                template = TemplateStat(template_name=template_name)
                db.add(template)
            
            template.usage_count += 1
            template.last_used = TimeManager.get_current_time()
            
            if vote_type:
                if vote_type == "funny":
                    template.funny_votes += 1
                elif vote_type == "mid":
                    template.mid_votes += 1
                elif vote_type == "savage":
                    template.savage_votes += 1
    
    # Leaderboard
    @classmethod
    def get_leaderboard(cls, category: str = "most_roasted", limit: int = 10) -> List[Dict]:
        """লিডারবোর্ড ডেটা রিটার্ন করে"""
        with cls.get_session() as db:
            if category == "most_roasted":
                users = db.query(User).order_by(User.roast_count.desc()).limit(limit).all()
            elif category == "most_votes":
                users = db.query(User).order_by(User.vote_count.desc()).limit(limit).all()
            else:
                users = db.query(User).order_by(User.reaction_count.desc()).limit(limit).all()
            
            result = []
            for i, user in enumerate(users, 1):
                result.append({
                    "rank": i,
                    "user_id": user.user_id,
                    "username": user.username or f"User_{user.user_id}",
                    "first_name": user.first_name,
                    "score": getattr(user, f"{category.split('_')[1]}_count")
                })
            
            return result
    
    # Cleanup old data
    @classmethod
    def cleanup_old_data(cls, days: int = 30):
        """পুরানো ডেটা ক্লিনআপ করে"""
        cutoff_date = TimeManager.get_current_time() - timedelta(days=days)
        
        with cls.get_session() as db:
            # Delete old roast logs
            db.query(RoastLog).filter(RoastLog.created_at < cutoff_date).delete()
            
            # Delete old votes
            db.query(Vote).filter(Vote.created_at < cutoff_date).delete()
            
            # Delete old reaction logs
            db.query(ReactionLog).filter(ReactionLog.created_at < cutoff_date).delete()
            
            logger.info(f"Cleaned up data older than {days} days")