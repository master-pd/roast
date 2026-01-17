from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config
from utils.time_manager import TimeManager

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=TimeManager.get_current_time)
    updated_at = Column(DateTime, default=TimeManager.get_current_time, onupdate=TimeManager.get_current_time)
    
    # Stats
    roast_count = Column(Integer, default=0)
    vote_count = Column(Integer, default=0)
    reaction_count = Column(Integer, default=0)
    last_roast_time = Column(DateTime)
    last_reaction_time = Column(DateTime)

class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    chat_type = Column(String(50))  # private, group, supergroup
    title = Column(String(255))
    created_at = Column(DateTime, default=TimeManager.get_current_time)
    
    # Settings
    welcome_enabled = Column(Boolean, default=True)
    roast_enabled = Column(Boolean, default=True)
    reactions_enabled = Column(Boolean, default=True)

class RoastLog(Base):
    __tablename__ = 'roast_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer)
    input_text = Column(Text)
    roast_type = Column(String(50))
    template_used = Column(String(100))
    created_at = Column(DateTime, default=TimeManager.get_current_time)

class Vote(Base):
    __tablename__ = 'votes'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer)
    message_id = Column(Integer)
    vote_type = Column(String(20))  # funny, mid, savage
    created_at = Column(DateTime, default=TimeManager.get_current_time)

class ReactionLog(Base):
    __tablename__ = 'reaction_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer)
    reaction_type = Column(String(20))
    created_at = Column(DateTime, default=TimeManager.get_current_time)

class TemplateStat(Base):
    __tablename__ = 'template_stats'
    
    id = Column(Integer, primary_key=True)
    template_name = Column(String(100), unique=True)
    usage_count = Column(Integer, default=0)
    funny_votes = Column(Integer, default=0)
    mid_votes = Column(Integer, default=0)
    savage_votes = Column(Integer, default=0)
    last_used = Column(DateTime)

# Database Engine
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_database():
    """ডেটাবেস টেবিল ক্রিয়েট করে"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """ডেটাবেস সেশন রিটার্ন করে"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()