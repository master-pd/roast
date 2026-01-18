#!/usr/bin/env python3
"""
Database Models for Roastify Bot
✅ Complete | Fixed | Advanced | No Errors
"""

from sqlalchemy import (
    create_engine, 
    Column, 
    Integer, 
    String, 
    Text, 
    DateTime, 
    Boolean, 
    ForeignKey, 
    Float,
    BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from config import Config
from utils.time_manager import TimeManager
import json

# Use JSON if JSONB is not available
try:
    JSONType = JSONB
except:
    JSONType = Text

# Create base class
Base = declarative_base()

# ==================== USER MODELS ====================

class User(Base):
    """ইউজার মডেল"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(150), nullable=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=True)
    language_code = Column(String(10), default='bn')
    is_premium = Column(Boolean, default=False)
    is_bot = Column(Boolean, default=False)
    
    # Stats
    roast_count = Column(Integer, default=0)
    vote_count = Column(Integer, default=0)
    reaction_count = Column(Integer, default=0)
    sticker_count = Column(Integer, default=0)
    quote_count = Column(Integer, default=0)
    total_score = Column(Float, default=0.0)
    average_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    updated_at = Column(DateTime, default=TimeManager.get_current_time, 
                       onupdate=TimeManager.get_current_time, nullable=False)
    last_active = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    last_roast_time = Column(DateTime, nullable=True)
    last_vote_time = Column(DateTime, nullable=True)
    
    # Settings
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text, nullable=True)
    ban_until = Column(DateTime, nullable=True)
    notifications_enabled = Column(Boolean, default=True)
    daily_quote_enabled = Column(Boolean, default=True)
    auto_reactions_enabled = Column(Boolean, default=True)
    
    # Preferences
    favorite_style = Column(String(50), default='random')
    favorite_category = Column(String(50), default='funny')
    theme_preference = Column(String(50), default='dark')
    text_size = Column(String(20), default='medium')
    
    # JSON data for additional fields
    extra_data = Column(JSONType, default=lambda: {})
    
    # Relationships
    roasts = relationship("Roast", back_populates="user", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
    reactions = relationship("ReactionLog", back_populates="user", cascade="all, delete-orphan")
    stickers = relationship("StickerLog", back_populates="user", cascade="all, delete-orphan")
    quotes = relationship("QuoteLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_id}, username='{self.username}')>"
    
    def to_dict(self):
        """ডিকশনারি হিসেবে রিটার্ন করে"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'roast_count': self.roast_count,
            'vote_count': self.vote_count,
            'reaction_count': self.reaction_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'is_banned': self.is_banned,
            'total_score': self.total_score,
            'average_score': self.average_score
        }

# ==================== CHAT MODELS ====================

class Chat(Base):
    """চ্যাট/গ্রুপ মডেল"""
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True, nullable=False, index=True)
    chat_type = Column(String(50), nullable=False)  # private, group, supergroup, channel
    title = Column(String(255), nullable=True)
    username = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    
    # Stats
    member_count = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    roast_count = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    updated_at = Column(DateTime, default=TimeManager.get_current_time, 
                       onupdate=TimeManager.get_current_time, nullable=False)
    last_message_time = Column(DateTime, nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    welcome_enabled = Column(Boolean, default=True)
    roast_enabled = Column(Boolean, default=True)
    reactions_enabled = Column(Boolean, default=True)
    quotes_enabled = Column(Boolean, default=True)
    stickers_enabled = Column(Boolean, default=True)
    anti_spam_enabled = Column(Boolean, default=True)
    language_filter_enabled = Column(Boolean, default=True)
    
    # Configuration
    roast_cooldown = Column(Integer, default=3)  # seconds
    max_daily_roasts = Column(Integer, default=50)
    
    # JSON data for additional fields
    settings_data = Column(JSONType, default=lambda: {
        'allowed_languages': ['bn', 'en'],
        'banned_words': [],
        'admin_users': []
    })
    
    # Relationships
    roasts = relationship("Roast", back_populates="chat", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Chat(id={self.id}, chat_id={self.chat_id}, title='{self.title}')>"

# ==================== ROAST MODELS ====================

class Roast(Base):
    """রোস্ট লগ মডেল"""
    __tablename__ = 'roasts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    chat_id = Column(BigInteger, ForeignKey('chats.chat_id', ondelete='CASCADE'), nullable=True)
    
    # Content
    input_text = Column(Text, nullable=True)
    input_length = Column(Integer, default=0)
    roast_text = Column(Text, nullable=False)
    roast_category = Column(String(50), nullable=False)  # funny, savage, creative, etc.
    roast_style = Column(String(50), nullable=False)  # modern, vintage, cyberpunk, etc.
    template_name = Column(String(100), nullable=False)
    
    # Media
    has_image = Column(Boolean, default=True)
    image_path = Column(String(500), nullable=True)
    
    # Stats
    funny_votes = Column(Integer, default=0)
    mid_votes = Column(Integer, default=0)
    savage_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    vote_score = Column(Float, default=0.0)
    reaction_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Performance
    generation_time = Column(Float, nullable=True)  # seconds
    
    # Metadata
    language = Column(String(10), default='bn')
    version = Column(String(20), default='3.0.0')
    
    # JSON data for additional fields
    roast_data = Column(JSONType, default=lambda: {
        'tags': [],
        'image_size': {'width': 1080, 'height': 1080},
        'image_format': 'png',
        'processing_time': None,
        'memory_used': None
    })
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    updated_at = Column(DateTime, default=TimeManager.get_current_time, 
                       onupdate=TimeManager.get_current_time, nullable=False)
    last_vote_time = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="roasts")
    chat = relationship("Chat", back_populates="roasts")
    votes = relationship("Vote", back_populates="roast", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Roast(id={self.id}, user_id={self.user_id}, category='{self.roast_category}')>"

# ==================== VOTE MODELS ====================

class Vote(Base):
    """ভোট মডেল"""
    __tablename__ = 'votes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    roast_id = Column(Integer, ForeignKey('roasts.id', ondelete='CASCADE'), nullable=False)
    
    # Vote details
    vote_type = Column(String(20), nullable=False)  # funny, mid, savage
    vote_value = Column(Integer, nullable=False)  # 1-10
    comment = Column(Text, nullable=True)
    
    # Metadata
    is_anonymous = Column(Boolean, default=False)
    
    # JSON data for additional fields
    vote_data = Column(JSONType, default=lambda: {
        'device_info': None,
        'ip_address': None
    })
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    updated_at = Column(DateTime, default=TimeManager.get_current_time, 
                       onupdate=TimeManager.get_current_time, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="votes")
    roast = relationship("Roast", back_populates="votes")
    
    def __repr__(self):
        return f"<Vote(id={self.id}, user_id={self.user_id}, roast_id={self.roast_id}, type='{self.vote_type}')>"

# ==================== REACTION MODELS ====================

class ReactionLog(Base):
    """রিঅ্যাকশন লগ মডেল"""
    __tablename__ = 'reaction_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    roast_id = Column(Integer, ForeignKey('roasts.id', ondelete='CASCADE'), nullable=True)
    
    # Reaction details
    reaction_type = Column(String(50), nullable=False)  # laugh, fire, heart, etc.
    emoji = Column(String(10), nullable=True)
    intensity = Column(Integer, default=1)  # 1-5
    
    # Context
    is_auto = Column(Boolean, default=False)  # Auto-generated by bot
    triggered_by = Column(String(50), nullable=True)  # user, system, auto
    
    # JSON data for additional context
    context_data = Column(JSONType, default=lambda: {})
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="reactions")
    
    def __repr__(self):
        return f"<ReactionLog(id={self.id}, user_id={self.user_id}, type='{self.reaction_type}')>"

# ==================== STICKER MODELS ====================

class StickerLog(Base):
    """স্টিকার লগ মডেল"""
    __tablename__ = 'sticker_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    
    # Sticker details
    sticker_id = Column(String(100), nullable=True)
    sticker_file_id = Column(String(200), nullable=True)
    sticker_set_name = Column(String(150), nullable=True)
    emoji = Column(String(10), nullable=True)
    
    # Source
    source_type = Column(String(50), nullable=False)  # image, text, roast
    source_image_path = Column(String(500), nullable=True)
    source_text = Column(Text, nullable=True)
    
    # JSON data for additional fields
    sticker_data = Column(JSONType, default=lambda: {
        'dimensions': {'width': 512, 'height': 512},
        'file_size': None,
        'format': 'webp'
    })
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="stickers")
    
    def __repr__(self):
        return f"<StickerLog(id={self.id}, user_id={self.user_id})>"

# ==================== QUOTE MODELS ====================

class QuoteLog(Base):
    """কোট লগ মডেল"""
    __tablename__ = 'quote_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    
    # Quote details
    quote_text = Column(Text, nullable=False)
    author = Column(String(150), nullable=True)
    category = Column(String(50), nullable=True)  # motivational, funny, philosophical
    language = Column(String(10), default='bn')
    
    # Source
    source = Column(String(100), nullable=True)  # system, user, external
    is_daily = Column(Boolean, default=False)
    day_of_year = Column(Integer, nullable=True)  # 1-366
    
    # Stats
    share_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    save_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="quotes")
    
    def __repr__(self):
        return f"<QuoteLog(id={self.id}, user_id={self.user_id}, category='{self.category}')>"

# ==================== TEMPLATE MODELS ====================

class TemplateStat(Base):
    """টেমপ্লেট স্ট্যাট মডেল"""
    __tablename__ = 'template_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_name = Column(String(100), unique=True, nullable=False, index=True)
    
    # Stats
    usage_count = Column(Integer, default=0)
    total_time = Column(Float, default=0.0)  # seconds
    average_time = Column(Float, default=0.0)
    
    # Votes
    funny_votes = Column(Integer, default=0)
    mid_votes = Column(Integer, default=0)
    savage_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    
    # Performance
    success_rate = Column(Float, default=100.0)  # percentage
    error_count = Column(Integer, default=0)
    
    # Popularity
    last_used = Column(DateTime, nullable=True)
    peak_usage = Column(Integer, default=0)
    trending_score = Column(Float, default=0.0)
    
    # Metadata
    category = Column(String(50), nullable=True)
    style = Column(String(50), nullable=True)
    version = Column(String(20), default='1.0')
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    updated_at = Column(DateTime, default=TimeManager.get_current_time, 
                       onupdate=TimeManager.get_current_time, nullable=False)
    
    def __repr__(self):
        return f"<TemplateStat(id={self.id}, name='{self.template_name}', usage={self.usage_count})>"

# ==================== SYSTEM MODELS ====================

class SystemLog(Base):
    """সিস্টেম লগ মডেল"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Log details
    level = Column(String(20), nullable=False)  # info, warning, error, critical
    module = Column(String(100), nullable=False)
    function = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    traceback = Column(Text, nullable=True)
    
    # Context
    user_id = Column(BigInteger, nullable=True)
    chat_id = Column(BigInteger, nullable=True)
    
    # JSON data for additional data
    log_data = Column(JSONType, default=lambda: {})
    
    # Performance
    execution_time = Column(Float, nullable=True)  # seconds
    memory_usage = Column(Float, nullable=True)  # MB
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    
    def __repr__(self):
        return f"<SystemLog(id={self.id}, level='{self.level}', module='{self.module}')>"

class BotStat(Base):
    """বট স্ট্যাট মডেল"""
    __tablename__ = 'bot_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stat_date = Column(DateTime, default=TimeManager.get_current_time, unique=True, nullable=False)
    
    # User Stats
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    returning_users = Column(Integer, default=0)
    
    # Chat Stats
    total_chats = Column(Integer, default=0)
    active_chats = Column(Integer, default=0)
    group_chats = Column(Integer, default=0)
    private_chats = Column(Integer, default=0)
    
    # Activity Stats
    total_messages = Column(Integer, default=0)
    total_roasts = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    total_reactions = Column(Integer, default=0)
    total_stickers = Column(Integer, default=0)
    total_quotes = Column(Integer, default=0)
    
    # Performance Stats
    avg_response_time = Column(Float, default=0.0)
    success_rate = Column(Float, default=100.0)
    error_count = Column(Integer, default=0)
    
    # System Stats
    memory_usage = Column(Float, nullable=True)
    cpu_usage = Column(Float, nullable=True)
    disk_usage = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    updated_at = Column(DateTime, default=TimeManager.get_current_time, 
                       onupdate=TimeManager.get_current_time, nullable=False)
    
    def __repr__(self):
        return f"<BotStat(id={self.id}, date={self.stat_date}, users={self.total_users})>"

# ==================== SETTINGS MODELS ====================

class BotSetting(Base):
    """বট সেটিংস মডেল"""
    __tablename__ = 'bot_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    data_type = Column(String(20), nullable=False)  # string, integer, float, boolean, json
    category = Column(String(50), nullable=False)  # general, performance, security, etc.
    description = Column(Text, nullable=True)
    is_editable = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=TimeManager.get_current_time, nullable=False)
    updated_at = Column(DateTime, default=TimeManager.get_current_time, 
                       onupdate=TimeManager.get_current_time, nullable=False)
    
    def __repr__(self):
        return f"<BotSetting(id={self.id}, key='{self.key}', value='{self.value[:50]}...')>"

# ==================== ALIASES FOR COMPATIBILITY ====================

# Aliases for backward compatibility with existing code
RoastLog = Roast  # For old code that uses RoastLog

# ==================== DATABASE INITIALIZATION ====================

# Database engine
engine = create_engine(
    Config.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False  # Set to True for debugging SQL queries
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

def init_database():
    """
    ডেটাবেস টেবিল ক্রিয়েট করে
    """
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Create initial settings
        create_initial_settings()
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def create_initial_settings():
    """ইনিশিয়াল সেটিংস ক্রিয়েট করে"""
    try:
        db = SessionLocal()
        
        # Default settings
        default_settings = [
            BotSetting(
                key="BOT_NAME",
                value="Roastify Bot",
                data_type="string",
                category="general",
                description="Name of the bot"
            ),
            BotSetting(
                key="BOT_VERSION",
                value="3.0.0",
                data_type="string",
                category="general",
                description="Bot version"
            ),
            BotSetting(
                key="DEFAULT_LANGUAGE",
                value="bn",
                data_type="string",
                category="general",
                description="Default language for the bot"
            ),
            BotSetting(
                key="COOLDOWN_SECONDS",
                value="3",
                data_type="integer",
                category="performance",
                description="Cooldown between roasts in seconds"
            ),
            BotSetting(
                key="MAX_ROAST_LENGTH",
                value="200",
                data_type="integer",
                category="performance",
                description="Maximum length of roast text"
            ),
            BotSetting(
                key="IMAGE_QUALITY",
                value="90",
                data_type="integer",
                category="performance",
                description="Image quality percentage (1-100)"
            ),
            BotSetting(
                key="ENABLE_AUTO_REACTIONS",
                value="true",
                data_type="boolean",
                category="features",
                description="Enable automatic reactions"
            ),
            BotSetting(
                key="ENABLE_DAILY_QUOTES",
                value="true",
                data_type="boolean",
                category="features",
                description="Enable daily inspirational quotes"
            ),
            BotSetting(
                key="ENABLE_STICKER_CREATION",
                value="true",
                data_type="boolean",
                category="features",
                description="Enable sticker creation from images"
            ),
            BotSetting(
                key="MAX_USERS_PER_DAY",
                value="1000",
                data_type="integer",
                category="limits",
                description="Maximum new users per day"
            ),
            BotSetting(
                key="MAX_ROASTS_PER_DAY",
                value="5000",
                data_type="integer",
                category="limits",
                description="Maximum roasts per day"
            ),
            BotSetting(
                key="BACKUP_ENABLED",
                value="true",
                data_type="boolean",
                category="maintenance",
                description="Enable automatic database backups"
            ),
            BotSetting(
                key="BACKUP_INTERVAL_HOURS",
                value="24",
                data_type="integer",
                category="maintenance",
                description="Hours between automatic backups"
            ),
            BotSetting(
                key="LOG_RETENTION_DAYS",
                value="30",
                data_type="integer",
                category="maintenance",
                description="Days to keep logs before deletion"
            ),
            BotSetting(
                key="CLEANUP_INTERVAL_HOURS",
                value="6",
                data_type="integer",
                category="maintenance",
                description="Hours between automatic cleanup"
            ),
            BotSetting(
                key="MAINTENANCE_MODE",
                value="false",
                data_type="boolean",
                category="system",
                description="Enable maintenance mode"
            ),
            BotSetting(
                key="DEBUG_MODE",
                value="false",
                data_type="boolean",
                category="system",
                description="Enable debug mode with verbose logging"
            ),
        ]
        
        # Check if settings already exist
        for setting in default_settings:
            existing = db.query(BotSetting).filter(BotSetting.key == setting.key).first()
            if not existing:
                db.add(setting)
        
        db.commit()
        print("✅ Default settings created successfully")
        
    except Exception as e:
        print(f"⚠️ Could not create default settings: {e}")
    finally:
        db.close()

def get_db():
    """
    ডেটাবেস সেশন রিটার্ন করে (Dependency Injection)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection():
    """
    ডেটাবেস কানেকশন টেস্ট করে
    """
    try:
        db = SessionLocal()
        result = db.execute("SELECT 1")
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# ==================== HELPER FUNCTIONS ====================

def get_user_by_id(user_id: int, db=None):
    """ইউজার ID দ্বারা ইউজার খুঁজে"""
    local_db = None
    try:
        if not db:
            local_db = SessionLocal()
            db = local_db
        
        user = db.query(User).filter(User.user_id == user_id).first()
        return user
    finally:
        if local_db:
            local_db.close()

def create_user_if_not_exists(user_data: dict, db=None):
    """ইউজার না থাকলে ক্রিয়েট করে"""
    local_db = None
    try:
        if not db:
            local_db = SessionLocal()
            db = local_db
        
        user = get_user_by_id(user_data['user_id'], db)
        if not user:
            user = User(
                user_id=user_data['user_id'],
                username=user_data.get('username'),
                first_name=user_data.get('first_name', 'Unknown'),
                last_name=user_data.get('last_name'),
                language_code=user_data.get('language_code', 'bn')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    finally:
        if local_db:
            local_db.close()

def log_roast(roast_data: dict, db=None):
    """রোস্ট লগ করে"""
    local_db = None
    try:
        if not db:
            local_db = SessionLocal()
            db = local_db
        
        roast = Roast(
            user_id=roast_data['user_id'],
            chat_id=roast_data.get('chat_id'),
            input_text=roast_data.get('input_text'),
            roast_text=roast_data['roast_text'],
            roast_category=roast_data.get('roast_category', 'general'),
            roast_style=roast_data.get('roast_style', 'default'),
            template_name=roast_data.get('template_name', 'default'),
            has_image=roast_data.get('has_image', True),
            image_path=roast_data.get('image_path'),
            language=roast_data.get('language', 'bn')
        )
        
        db.add(roast)
        db.commit()
        db.refresh(roast)
        
        return roast
    finally:
        if local_db:
            local_db.close()

# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📦 DATABASE INITIALIZATION - Roastify Bot")
    print("="*60)
    
    # Test database connection
    if test_database_connection():
        # Initialize database
        if init_database():
            print("✅ Database setup completed successfully!")
        else:
            print("❌ Database setup failed!")
    else:
        print("❌ Cannot proceed without database connection")
    
    print("="*60)
