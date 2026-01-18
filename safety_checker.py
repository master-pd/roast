"""
COMPLETE Safety Checker Module for Roastify Bot
Full featured safety system with all required methods
"""

import re
import json
import logging
import sqlite3
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum


class SafetyLevel(Enum):
    """Safety levels"""
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"
    BLOCKED = "blocked"


class ContentType(Enum):
    """Content types"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    STICKER = "sticker"
    AUDIO = "audio"
    DOCUMENT = "document"


class SafetyChecker:
    """Complete Safety Checker with all methods"""
    
    def __init__(self, config_path: str = "config/safety_config.json"):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Initializing Complete Safety Checker...")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize databases
        self._init_databases()
        
        # Load safety data
        self.banned_words: Set[str] = set()
        self.suspicious_patterns: List[Tuple[str, str]] = []
        self.allowed_domains: Set[str] = set()
        self.banned_users: Set[int] = set()
        
        self._load_safety_data()
        
        # User tracking
        self.user_scores: Dict[int, Dict[str, Any]] = {}
        self.user_warnings: Dict[int, List[Dict]] = {}
        self.user_messages: Dict[int, List[datetime]] = {}
        
        # Admin/owner
        self.admin_ids: Set[int] = set(self.config.get("admin_ids", []))
        self.owner_id: int = self.config.get("owner_id", 0)
        
        # Statistics
        self.stats = {
            "total_checks": 0,
            "blocks": 0,
            "warnings": 0,
            "false_positives": 0
        }
        
        self.logger.info(f"✅ Safety Checker initialized with {len(self.banned_words)} banned words")
        self.logger.info(f"📊 Admin IDs: {len(self.admin_ids)}, Owner: {self.owner_id}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "banned_words_file": "data/banned_words.txt",
            "suspicious_patterns_file": "data/suspicious_patterns.json",
            "allowed_domains_file": "data/allowed_domains.txt",
            "banned_users_file": "data/banned_users.txt",
            "safety_rules": {
                "max_message_length": 1000,
                "min_message_length": 2,
                "max_emojis": 10,
                "max_caps_ratio": 0.5,
                "max_urls": 2,
                "rate_limit": 10,  # messages per minute
                "daily_warning_limit": 5,
                "warning_cooldown": 3600,  # 1 hour
            },
            "admin_ids": [],
            "owner_id": 0,
            "auto_ban_threshold": 3,
            "auto_mute_duration": 3600,  # 1 hour
            "strict_mode": False,
        }
        
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
        except Exception as e:
            self.logger.error(f"❌ Error loading config: {e}")
        
        return default_config
    
    def _init_databases(self):
        """Initialize safety databases"""
        try:
            self.safety_db = sqlite3.connect('data/safety.db', check_same_thread=False)
            self.safety_db.row_factory = sqlite3.Row
            
            # Create tables
            cursor = self.safety_db.cursor()
            
            # User safety table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_safety (
                    user_id INTEGER PRIMARY KEY,
                    safety_score INTEGER DEFAULT 100,
                    warning_count INTEGER DEFAULT 0,
                    block_count INTEGER DEFAULT 0,
                    last_warning TIMESTAMP,
                    last_activity TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Warning log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    warning_type TEXT,
                    warning_message TEXT,
                    content TEXT,
                    safety_score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_safety (user_id)
                )
            ''')
            
            # Block log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    block_type TEXT,
                    reason TEXT,
                    duration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_safety (user_id)
                )
            ''')
            
            self.safety_db.commit()
            self.logger.info("✅ Safety databases initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing databases: {e}")
            self.safety_db = None
    
    def _load_safety_data(self):
        """Load all safety data from files"""
        # Load banned words
        banned_words_file = Path(self.config["banned_words_file"])
        if banned_words_file.exists():
            try:
                with open(banned_words_file, 'r', encoding='utf-8') as f:
                    self.banned_words = set(line.strip().lower() for line in f if line.strip())
                self.logger.info(f"📚 Loaded {len(self.banned_words)} banned words")
            except Exception as e:
                self.logger.error(f"❌ Error loading banned words: {e}")
                self._load_default_banned_words()
        else:
            self._load_default_banned_words()
        
        # Load suspicious patterns
        patterns_file = Path(self.config["suspicious_patterns_file"])
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
                    self.suspicious_patterns = [
                        (pattern["regex"], pattern["name"])
                        for pattern in patterns_data.get("patterns", [])
                    ]
                self.logger.info(f"📚 Loaded {len(self.suspicious_patterns)} suspicious patterns")
            except Exception as e:
                self.logger.error(f"❌ Error loading patterns: {e}")
                self._load_default_patterns()
        else:
            self._load_default_patterns()
        
        # Load allowed domains
        domains_file = Path(self.config["allowed_domains_file"])
        if domains_file.exists():
            try:
                with open(domains_file, 'r', encoding='utf-8') as f:
                    self.allowed_domains = set(line.strip().lower() for line in f if line.strip())
                self.logger.info(f"📚 Loaded {len(self.allowed_domains)} allowed domains")
            except Exception as e:
                self.logger.error(f"❌ Error loading domains: {e}")
        
        # Load banned users
        banned_users_file = Path(self.config["banned_users_file"])
        if banned_users_file.exists():
            try:
                with open(banned_users_file, 'r', encoding='utf-8') as f:
                    self.banned_users = set(int(line.strip()) for line in f if line.strip().isdigit())
                self.logger.info(f"📚 Loaded {len(self.banned_users)} banned users")
            except Exception as e:
                self.logger.error(f"❌ Error loading banned users: {e}")
    
    def _load_default_banned_words(self):
        """Load default banned words"""
        # English inappropriate words
        english_bad = {
            "fuck", "shit", "asshole", "bastard", "bitch", "cunt", "pussy", "dick", "cock",
            "whore", "slut", "nigger", "nigga", "retard", "faggot", "dyke", "tranny",
            "idiot", "moron", "stupid", "dumbass", "motherfucker", "bullshit", "damn",
            "hell", "suck", "sucks", "sucking", "blowjob", "handjob", "masturbate",
            "porn", "porno", "xxx", "sex", "sexual", "rape", "rapist", "pedophile",
            "scam", "scamming", "fraud", "hack", "hacking", "virus", "malware",
            "kill", "killing", "murder", "suicide", "bomb", "terrorist", "attack"
        }
        
        # Bengali inappropriate words
        bengali_bad = {
            "গালি", "অপমান", "অশ্লীল", "খারাপ", "মন্দ", "হুট", "হুঙ্কার",
            "শালা", "শালী", "হরামী", "হারামি", "জাহান্নামী", "কুত্তা", "কুত্তির",
            "শুয়োর", "বেজন্মা", "হাপা", "হাবা", "পাগল", "উল্টা", "নষ্ট",
            "বদমাইশ", "গুণ্ডা", "খারাপ", "অভদ্র", "অসভ্য", "অপবাদ", "নিন্দা",
            "গালাগালি", "ঝগড়া", "মারামারি", "হানাহানি", "ধর্ষণ", "বলপ্রয়োগ"
        }
        
        # Romanized Bengali bad words
        romanized_bad = {
            "sala", "sali", "harami", "kutta", "kuttar", "kuttir", "hoga",
            "pagol", "ulta", "beshya", "randi", "khanki", "magi", "faltu"
        }
        
        self.banned_words = english_bad.union(bengali_bad).union(romanized_bad)
        self.logger.info(f"📚 Loaded {len(self.banned_words)} default banned words")
    
    def _load_default_patterns(self):
        """Load default suspicious patterns"""
        self.suspicious_patterns = [
            # URLs and links
            (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', "url_detected"),
            (r'(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?', "website_detected"),
            (r't\.me/[\w]+', "telegram_link"),
            
            # Personal information
            (r'\+?(88)?01[3-9]\d{8}', "phone_number"),
            (r'\d{4}[-\.\s]?\d{4}[-\.\s]?\d{4}', "phone_format"),
            (r'\S+@\S+\.\S+', "email_address"),
            (r'\b\d{10,17}\b', "id_number"),
            (r'\b\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4}\b', "us_phone"),
            
            # Spam patterns
            (r'([\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]){10,}', "emoji_spam"),
            (r'(\S+\s+){3,}\1', "repeated_text"),
            (r'[A-Z\u0980-\u09FF]{15,}', "excessive_caps"),
            (r'@\w+\s*@\w+\s*@\w+', "multiple_mentions"),
            (r'[\W_]{20,}', "excessive_special_chars"),
            (r'\b(?:win|won|free|gift|prize|money|cash|reward)\b.*\b(?:click|link|call|visit)\b', "spam_keywords"),
            
            # Threat patterns
            (r'\b(?:kill|murder|attack|beat|hit|hurt|harm|destroy)\b.*\b(?:you|u|your|urself)\b', "threat_detected"),
            (r'\b(?:bomb|explode|shoot|gun|knife|weapon)\b', "weapon_mention"),
            (r'\b(?:die|death|dead|suicide|hang|jump)\b', "self_harm"),
            
            # Scam patterns
            (r'\b(?:bitcoin|crypto|investment|profit|earn|money|rich)\b.*\b(?:fast|quick|easy|guaranteed)\b', "scam_alert"),
            (r'\b(?:password|login|account|bank|card|pin)\b.*\b(?:send|give|share|provide)\b', "phishing_attempt"),
            
            # Inappropriate content
            (r'\b(?:nude|naked|porn|sex|xxx|adult)\b', "adult_content"),
            (r'\b(?:drug|weed|cocaine|heroin|alcohol|drunk)\b', "drug_mention"),
            
            # Hate speech
            (r'\b(?:hate|racist|sexist|homophobic|transphobic)\b', "hate_speech"),
            (r'\b(?:muslim|hindu|christian|buddhist|jew)\b.*\b(?:bad|evil|wrong|stupid)\b', "religious_hate"),
        ]
    
    # ========== MAIN SAFETY METHODS ==========
    
    def check_message(self, text: str, user_id: Optional[int] = None, 
                     content_type: ContentType = ContentType.TEXT) -> Dict[str, Any]:
        """
        Complete message safety check
        
        Args:
            text: Message text
            user_id: User ID (optional)
            content_type: Type of content
            
        Returns:
            dict: Safety check results
        """
        self.stats["total_checks"] += 1
        
        # Initialize result
        result = {
            "is_safe": True,
            "safety_level": SafetyLevel.SAFE.value,
            "score": 100,
            "warnings": [],
            "actions": [],
            "details": {},
            "filtered_text": text,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if user is banned
        if user_id and self.is_user_banned(user_id):
            result["is_safe"] = False
            result["safety_level"] = SafetyLevel.BLOCKED.value
            result["score"] = 0
            result["warnings"].append("user_banned")
            result["actions"].append("block_message")
            result["actions"].append("notify_admin")
            return result
        
        # Check rate limiting
        if user_id and not self._check_rate_limit(user_id):
            result["warnings"].append("rate_limit_exceeded")
            result["score"] -= 30
            result["actions"].append("slow_down")
        
        # Basic text validation
        if not text or not isinstance(text, str):
            result["is_safe"] = False
            result["safety_level"] = SafetyLevel.BLOCKED.value
            result["score"] = 0
            result["warnings"].append("invalid_content")
            return result
        
        # Content type specific checks
        if content_type == ContentType.TEXT:
            text_result = self._check_text_content(text)
            result.update(text_result)
        
        # Check banned words
        banned_words_found = self._check_banned_words(text)
        if banned_words_found:
            result["warnings"].append(f"banned_words:{len(banned_words_found)}")
            result["score"] -= len(banned_words_found) * 15
            result["details"]["banned_words"] = banned_words_found
        
        # Check suspicious patterns
        patterns_found = self._check_suspicious_patterns(text)
        if patterns_found:
            result["warnings"].extend([f"pattern:{p}" for p in patterns_found])
            result["score"] -= len(patterns_found) * 10
            result["details"]["patterns"] = patterns_found
        
        # Check URLs
        urls_found = self._extract_urls(text)
        if urls_found:
            unsafe_urls = [url for url in urls_found if not self._is_url_safe(url)]
            if unsafe_urls:
                result["warnings"].append(f"unsafe_urls:{len(unsafe_urls)}")
                result["score"] -= len(unsafe_urls) * 20
                result["details"]["unsafe_urls"] = unsafe_urls
                result["filtered_text"] = self._filter_urls(text, unsafe_urls)
        
        # Determine safety level
        if result["score"] >= 80:
            result["safety_level"] = SafetyLevel.SAFE.value
        elif result["score"] >= 60:
            result["safety_level"] = SafetyLevel.WARNING.value
            result["actions"].append("warn_user")
        elif result["score"] >= 40:
            result["safety_level"] = SafetyLevel.DANGER.value
            result["actions"].extend(["warn_user", "mute_temporary"])
        else:
            result["safety_level"] = SafetyLevel.BLOCKED.value
            result["is_safe"] = False
            result["actions"].extend(["block_message", "warn_user", "report_admin"])
        
        # Update user safety score
        if user_id:
            self._update_user_safety(user_id, result["score"], result["warnings"])
            
            # Check if user needs auto-ban
            if not result["is_safe"] and self._should_auto_ban(user_id):
                result["actions"].append("auto_ban")
                result["details"]["auto_ban_reason"] = "multiple_violations"
        
        # Log warning if unsafe
        if not result["is_safe"]:
            self.stats["blocks"] += 1
            if user_id:
                self._log_warning(user_id, result)
        
        return result
    
    def _check_text_content(self, text: str) -> Dict[str, Any]:
        """Check text content for safety"""
        result = {
            "score_deductions": 0,
            "text_analysis": {}
        }
        
        # Length checks
        text_length = len(text)
        max_len = self.config["safety_rules"]["max_message_length"]
        min_len = self.config["safety_rules"]["min_message_length"]
        
        if text_length < min_len:
            result["score_deductions"] += 30
            result["text_analysis"]["too_short"] = True
        
        if text_length > max_len:
            result["score_deductions"] += 10
            result["text_analysis"]["too_long"] = True
        
        # Character analysis
        bengali_chars = len(re.findall(r'[\u0980-\u09FF]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        digit_chars = len(re.findall(r'\d', text))
        special_chars = len(re.findall(r'[^\w\u0980-\u09FF\s]', text))
        emoji_chars = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF]', text))
        
        result["text_analysis"]["char_counts"] = {
            "bengali": bengali_chars,
            "english": english_chars,
            "digits": digit_chars,
            "special": special_chars,
            "emojis": emoji_chars,
            "total": text_length
        }
        
        # Check for only numbers
        if text.replace(' ', '').isdigit():
            result["score_deductions"] += 20
            result["text_analysis"]["only_numbers"] = True
        
        # Check for only emojis
        if emoji_chars > 0 and (bengali_chars + english_chars + digit_chars) == 0:
            result["score_deductions"] += 15
            result["text_analysis"]["only_emojis"] = True
        
        # Check excessive emojis
        max_emojis = self.config["safety_rules"]["max_emojis"]
        if emoji_chars > max_emojis:
            result["score_deductions"] += (emoji_chars - max_emojis) * 2
        
        # Check caps ratio
        caps_chars = len(re.findall(r'[A-Z\u0980-\u09FF]', text))
        total_alpha = len(re.findall(r'[a-zA-Z\u0980-\u09FF]', text))
        if total_alpha > 0:
            caps_ratio = caps_chars / total_alpha
            max_caps = self.config["safety_rules"]["max_caps_ratio"]
            if caps_ratio > max_caps:
                result["score_deductions"] += 25
                result["text_analysis"]["excessive_caps"] = True
        
        # Word count
        words = text.split()
        result["text_analysis"]["word_count"] = len(words)
        
        if len(words) < 2:
            result["score_deductions"] += 5
        
        return result
    
    def _check_banned_words(self, text: str) -> List[str]:
        """Check for banned words in text"""
        found_words = []
        text_lower = text.lower()
        
        for word in self.banned_words:
            if word and word in text_lower:
                found_words.append(word)
        
        return found_words
    
    def _check_suspicious_patterns(self, text: str) -> List[str]:
        """Check for suspicious patterns"""
        found_patterns = []
        
        for pattern, pattern_name in self.suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.UNICODE):
                found_patterns.append(pattern_name)
        
        return found_patterns
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w .?=&%+-]*'
        return re.findall(url_pattern, text)
    
    def _is_url_safe(self, url: str) -> bool:
        """Check if URL is safe"""
        # Extract domain
        domain_match = re.search(r'https?://([^/]+)', url)
        if not domain_match:
            return False
        
        domain = domain_match.group(1).lower()
        
        # Check if domain is in allowed list
        for allowed_domain in self.allowed_domains:
            if domain.endswith(allowed_domain):
                return True
        
        # Check for suspicious domains
        suspicious_domains = ["bit.ly", "tinyurl", "shorte.st", "adf.ly", "bc.vc"]
        for suspicious in suspicious_domains:
            if suspicious in domain:
                return False
        
        return True
    
    def _filter_urls(self, text: str, urls_to_filter: List[str]) -> str:
        """Filter unsafe URLs from text"""
        filtered_text = text
        for url in urls_to_filter:
            filtered_text = filtered_text.replace(url, "[UNSAFE_LINK]")
        return filtered_text
    
    # ========== USER MANAGEMENT METHODS ==========
    
    def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        if user_id in self.banned_users:
            return True
        
        # Check database
        if self.safety_db:
            try:
                cursor = self.safety_db.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM blocks WHERE user_id = ? AND expires_at > ?",
                    (user_id, datetime.now())
                )
                count = cursor.fetchone()[0]
                return count > 0
            except Exception as e:
                self.logger.error(f"❌ Error checking user ban: {e}")
        
        return False
    
    def ban_user(self, user_id: int, reason: str, duration_hours: int = 24,
                banned_by: Optional[int] = None) -> bool:
        """Ban a user"""
        try:
            # Add to memory
            self.banned_users.add(user_id)
            
            # Add to file
            banned_file = Path(self.config["banned_users_file"])
            banned_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(banned_file, 'a', encoding='utf-8') as f:
                f.write(f"{user_id}\n")
            
            # Add to database
            if self.safety_db:
                cursor = self.safety_db.cursor()
                expires_at = datetime.now() + timedelta(hours=duration_hours)
                
                cursor.execute(
                    """INSERT INTO blocks 
                    (user_id, block_type, reason, duration, expires_at) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (user_id, "manual", reason, duration_hours * 3600, expires_at)
                )
                
                self.safety_db.commit()
            
            # Log action
            self.logger.warning(f"🚫 User {user_id} banned for {duration_hours}h. Reason: {reason}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error banning user: {e}")
            return False
    
    def unban_user(self, user_id: int) -> bool:
        """Unban a user"""
        try:
            # Remove from memory
            if user_id in self.banned_users:
                self.banned_users.remove(user_id)
            
            # Remove from file (recreate without user)
            banned_file = Path(self.config["banned_users_file"])
            if banned_file.exists():
                with open(banned_file, 'r', encoding='utf-8') as f:
                    users = [line.strip() for line in f if line.strip() != str(user_id)]
                
                with open(banned_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(users))
            
            # Update database
            if self.safety_db:
                cursor = self.safety_db.cursor()
                cursor.execute(
                    "UPDATE blocks SET expires_at = ? WHERE user_id = ?",
                    (datetime.now(), user_id)
                )
                self.safety_db.commit()
            
            self.logger.info(f"✅ User {user_id} unbanned")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error unbanning user: {e}")
            return False
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check rate limiting for user"""
        now = datetime.now()
        
        # Initialize user messages list
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        
        # Remove old messages (last minute)
        self.user_messages[user_id] = [
            msg_time for msg_time in self.user_messages[user_id]
            if now - msg_time < timedelta(minutes=1)
        ]
        
        # Check limit
        max_messages = self.config["safety_rules"]["rate_limit"]
        if len(self.user_messages[user_id]) >= max_messages:
            return False
        
        # Add current message
        self.user_messages[user_id].append(now)
        
        return True
    
    def _update_user_safety(self, user_id: int, score: int, warnings: List[str]):
        """Update user safety score"""
        try:
            # Update in-memory
            if user_id not in self.user_scores:
                self.user_scores[user_id] = {
                    "scores": [],
                    "warnings": 0,
                    "last_updated": datetime.now()
                }
            
            user_data = self.user_scores[user_id]
            user_data["scores"].append(score)
            user_data["warnings"] += len(warnings)
            user_data["last_updated"] = datetime.now()
            
            # Keep only last 100 scores
            if len(user_data["scores"]) > 100:
                user_data["scores"] = user_data["scores"][-100:]
            
            # Update database
            if self.safety_db:
                cursor = self.safety_db.cursor()
                
                # Check if user exists
                cursor.execute(
                    "SELECT safety_score, warning_count FROM user_safety WHERE user_id = ?",
                    (user_id,)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing
                    new_score = (existing["safety_score"] + score) // 2
                    new_warnings = existing["warning_count"] + len(warnings)
                    
                    cursor.execute(
                        """UPDATE user_safety 
                        SET safety_score = ?, warning_count = ?, last_activity = ?
                        WHERE user_id = ?""",
                        (new_score, new_warnings, datetime.now(), user_id)
                    )
                else:
                    # Insert new
                    cursor.execute(
                        """INSERT INTO user_safety 
                        (user_id, safety_score, warning_count, last_activity) 
                        VALUES (?, ?, ?, ?)""",
                        (user_id, score, len(warnings), datetime.now())
                    )
                
                self.safety_db.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Error updating user safety: {e}")
    
    def _log_warning(self, user_id: int, result: Dict[str, Any]):
        """Log warning for user"""
        try:
            warning_data = {
                "user_id": user_id,
                "warning_type": "safety_violation",
                "warning_message": f"Safety score: {result['score']}",
                "content": result.get("filtered_text", "")[:500],
                "safety_score": result["score"],
                "warnings": result["warnings"],
                "actions": result["actions"]
            }
            
            # Add to memory
            if user_id not in self.user_warnings:
                self.user_warnings[user_id] = []
            
            self.user_warnings[user_id].append(warning_data)
            
            # Keep only last 50 warnings
            if len(self.user_warnings[user_id]) > 50:
                self.user_warnings[user_id] = self.user_warnings[user_id][-50:]
            
            # Add to database
            if self.safety_db:
                cursor = self.safety_db.cursor()
                
                cursor.execute(
                    """INSERT INTO warnings 
                    (user_id, warning_type, warning_message, content, safety_score) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (user_id, warning_data["warning_type"], 
                     warning_data["warning_message"], 
                     warning_data["content"], 
                     warning_data["safety_score"])
                )
                
                # Update user's last warning time
                cursor.execute(
                    """UPDATE user_safety 
                    SET last_warning = ? 
                    WHERE user_id = ?""",
                    (datetime.now(), user_id)
                )
                
                self.safety_db.commit()
            
        except Exception as e:
            self.logger.error(f"❌ Error logging warning: {e}")
    
    def _should_auto_ban(self, user_id: int) -> bool:
        """Check if user should be auto-banned"""
        if user_id not in self.user_scores:
            return False
        
        user_data = self.user_scores[user_id]
        warning_limit = self.config["safety_rules"]["daily_warning_limit"]
        auto_ban_threshold = self.config["auto_ban_threshold"]
        
        # Count warnings in last 24 hours
        recent_warnings = 0
        if user_id in self.user_warnings:
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_warnings = sum(
                1 for warning in self.user_warnings[user_id]
                if warning.get("timestamp", datetime.min) > cutoff_time
            )
        
        return (user_data["warnings"] >= auto_ban_threshold or 
                recent_warnings >= warning_limit)
    
    # ========== ADMIN METHODS ==========
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids or user_id == self.owner_id
    
    def is_owner(self, user_id: int) -> bool:
        """Check if user is owner"""
        return user_id == self.owner_id
    
    def add_admin(self, user_id: int, added_by: int) -> bool:
        """Add admin"""
        if not self.is_owner(added_by):
            return False
        
        self.admin_ids.add(user_id)
        self.logger.info(f"👑 Admin added: {user_id} by {added_by}")
        return True
    
    def remove_admin(self, user_id: int, removed_by: int) -> bool:
        """Remove admin"""
        if not self.is_owner(removed_by):
            return False
        
        if user_id in self.admin_ids:
            self.admin_ids.remove(user_id)
            self.logger.info(f"👑 Admin removed: {user_id} by {removed_by}")
            return True
        
        return False
    
    # ========== STATISTICS AND REPORTS ==========
    
    def get_user_report(self, user_id: int) -> Dict[str, Any]:
        """Get detailed user report"""
        report = {
            "user_id": user_id,
            "is_banned": self.is_user_banned(user_id),
            "is_admin": self.is_admin(user_id),
            "is_owner": self.is_owner(user_id),
            "safety_data": {},
            "warning_history": [],
            "statistics": {}
        }
        
        # Get safety data
        if user_id in self.user_scores:
            user_data = self.user_scores[user_id]
            report["safety_data"] = {
                "current_score": user_data["scores"][-1] if user_data["scores"] else 100,
                "average_score": sum(user_data["scores"]) / len(user_data["scores"]) if user_data["scores"] else 100,
                "total_warnings": user_data["warnings"],
                "last_updated": user_data["last_updated"].isoformat() if user_data["last_updated"] else None
            }
        
        # Get warning history
        if user_id in self.user_warnings:
            report["warning_history"] = self.user_warnings[user_id][-10:]  # Last 10 warnings
        
        # Get database stats
        if self.safety_db:
            try:
                cursor = self.safety_db.cursor()
                
                # Get warning count
                cursor.execute(
                    "SELECT COUNT(*) as count FROM warnings WHERE user_id = ?",
                    (user_id,)
                )
                warning_count = cursor.fetchone()["count"]
                
                # Get block history
                cursor.execute(
                    "SELECT * FROM blocks WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
                    (user_id,)
                )
                block_history = [dict(row) for row in cursor.fetchall()]
                
                report["statistics"]["database_warnings"] = warning_count
                report["statistics"]["block_history"] = block_history
                
            except Exception as e:
                self.logger.error(f"❌ Error getting user database stats: {e}")
        
        return report
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "total_checks": self.stats["total_checks"],
            "blocks": self.stats["blocks"],
            "warnings": self.stats["warnings"],
            "false_positives": self.stats["false_positives"],
            "total_users_tracked": len(self.user_scores),
            "banned_users": len(self.banned_users),
            "admin_count": len(self.admin_ids),
            "banned_words_count": len(self.banned_words),
            "suspicious_patterns": len(self.suspicious_patterns),
            "uptime": str(datetime.now() - self._get_start_time()),
            "memory_usage": self._get_memory_usage()
        }
    
    def _get_start_time(self) -> datetime:
        """Get safety checker start time"""
        # In production, store this when initialized
        return datetime.now() - timedelta(hours=1)  # Example
    
    def _get_memory_usage(self) -> str:
        """Get memory usage"""
        try:
            import psutil
            process = psutil.Process()
            mem_mb = process.memory_info().rss / 1024 / 1024
            return f"{mem_mb:.2f} MB"
        except:
            return "N/A"
    
    # ========== CONFIGURATION METHODS ==========
    
    def add_banned_word(self, word: str, added_by: int) -> bool:
        """Add banned word"""
        if not self.is_admin(added_by):
            return False
        
        word_lower = word.lower().strip()
        if word_lower and word_lower not in self.banned_words:
            self.banned_words.add(word_lower)
            
            # Save to file
            banned_file = Path(self.config["banned_words_file"])
            banned_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(banned_file, 'a', encoding='utf-8') as f:
                f.write(f"{word_lower}\n")
            
            self.logger.info(f"📝 Banned word added by {added_by}: {word_lower}")
            return True
        
        return False
    
    def remove_banned_word(self, word: str, removed_by: int) -> bool:
        """Remove banned word"""
        if not self.is_admin(removed_by):
            return False
        
        word_lower = word.lower().strip()
        if word_lower in self.banned_words:
            self.banned_words.remove(word_lower)
            
            # Update file
            banned_file = Path(self.config["banned_words_file"])
            if banned_file.exists():
                with open(banned_file, 'r', encoding='utf-8') as f:
                    words = [line.strip() for line in f if line.strip() != word_lower]
                
                with open(banned_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(words))
            
            self.logger.info(f"📝 Banned word removed by {removed_by}: {word_lower}")
            return True
        
        return False
    
    def export_safety_data(self) -> Dict[str, Any]:
        """Export all safety data"""
        return {
            "banned_words": list(self.banned_words),
            "banned_users": list(self.banned_users),
            "admin_ids": list(self.admin_ids),
            "owner_id": self.owner_id,
            "user_scores": {
                str(user_id): data for user_id, data in self.user_scores.items()
            },
            "statistics": self.stats,
            "config": self.config
        }
    
    def import_safety_data(self, data: Dict[str, Any], imported_by: int) -> bool:
        """Import safety data"""
        if not self.is_owner(imported_by):
            return False
        
        try:
            # Import data
            if "banned_words" in data:
                self.banned_words = set(data["banned_words"])
            
            if "banned_users" in data:
                self.banned_users = set(data["banned_users"])
            
            if "admin_ids" in data:
                self.admin_ids = set(data["admin_ids"])
            
            if "owner_id" in data:
                self.owner_id = data["owner_id"]
            
            self.logger.info(f"📥 Safety data imported by {imported_by}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error importing safety data: {e}")
            return False
    
    # ========== UTILITY METHODS ==========
    
    def sanitize_text(self, text: str, aggressive: bool = False) -> str:
        """
        Sanitize text by removing sensitive information
        
        Args:
            text: Text to sanitize
            aggressive: Whether to aggressively sanitize
            
        Returns:
            str: Sanitized text
        """
        if not text:
            return ""
        
        sanitized = text
        
        # Remove URLs
        urls = self._extract_urls(sanitized)
        for url in urls:
            sanitized = sanitized.replace(url, "[LINK]")
        
        # Remove phone numbers
        sanitized = re.sub(r'\+?(88)?01[3-9]\d{8}', '[PHONE]', sanitized)
        sanitized = re.sub(r'\d{4}[-\.\s]?\d{4}[-\.\s]?\d{4}', '[PHONE]', sanitized)
        
        # Remove email addresses
        sanitized = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', sanitized)
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # Aggressive sanitization
        if aggressive:
            # Remove banned words
            for word in self.banned_words:
                sanitized = re.sub(r'\b' + re.escape(word) + r'\b', '[FILTERED]', 
                                 sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.safety_db:
                self.safety_db.close()
            
            # Save current state
            self._save_state()
            
            self.logger.info("🧹 Safety Checker cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
    
    def _save_state(self):
        """Save current state to file"""
        try:
            state_file = Path("data/safety_state.json")
            state_file.parent.mkdir(parents=True, exist_ok=True)
            
            state_data = {
                "user_scores": {
                    str(user_id): data for user_id, data in self.user_scores.items()
                },
                "user_warnings": {
                    str(user_id): warnings for user_id, warnings in self.user_warnings.items()
                },
                "banned_users": list(self.banned_users),
                "stats": self.stats,
                "saved_at": datetime.now().isoformat()
            }
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("💾 Safety state saved")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving state: {e}")
    
    # ========== TEST METHODS ==========
    
    def test_safety_check(self, test_text: str) -> Dict[str, Any]:
        """Test safety check with given text"""
        return self.check_message(test_text, user_id=999999, content_type=ContentType.TEXT)
    
    def run_self_test(self) -> Dict[str, Any]:
        """Run self-test"""
        test_cases = [
            ("Hello world", True),
            ("Fuck you", False),
            ("Visit http://example.com", True),
            ("My phone is 01712345678", False),
            ("গালি দিব না", False),
            ("This is a normal message", True),
            ("WIN FREE MONEY NOW!!! CLICK HERE!!!", False),
            ("I love programming", True),
        ]
        
        results = []
        for text, expected_safe in test_cases:
            result = self.test_safety_check(text)
            passed = result["is_safe"] == expected_safe
            results.append({
                "text": text,
                "expected_safe": expected_safe,
                "actual_safe": result["is_safe"],
                "score": result["score"],
                "passed": passed
            })
        
        passed_count = sum(1 for r in results if r["passed"])
        total_count = len(results)
        
        return {
            "test_cases": results,
            "summary": {
                "total": total_count,
                "passed": passed_count,
                "failed": total_count - passed_count,
                "success_rate": (passed_count / total_count * 100) if total_count > 0 else 0
            }
        }


# Global instance
safety_checker = SafetyChecker()

if __name__ == "__main__":
    # Test the safety checker
    logging.basicConfig(level=logging.INFO)
    
    checker = SafetyChecker()
    
    print("🔍 Testing SafetyChecker...")
    
    # Run self-test
    test_results = checker.run_self_test()
    
    print(f"\n📊 Test Results:")
    print(f"  Total tests: {test_results['summary']['total']}")
    print(f"  Passed: {test_results['summary']['passed']}")
    print(f"  Failed: {test_results['summary']['failed']}")
    print(f"  Success rate: {test_results['summary']['success_rate']:.1f}%")
    
    print("\n🔍 Individual test results:")
    for i, result in enumerate(test_results["test_cases"][:3], 1):
        status = "✅" if result["passed"] else "❌"
        print(f"  {status} Test {i}: '{result['text'][:30]}...' - "
              f"Score: {result['score']}, Safe: {result['actual_safe']}")
    
    print("\n📊 System Statistics:")
    stats = checker.get_system_stats()
    for key, value in stats.items():
        if key not in ["memory_usage", "uptime"]:
            print(f"  {key}: {value}")
    
    # Cleanup
    checker.cleanup()
