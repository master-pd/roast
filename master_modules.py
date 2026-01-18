#!/usr/bin/env python3
"""
📦 Master Module List for Roastify Bot
এখানে শুধু মডিউল নামগুলো লিখলেই অটোমেটিক লোড হবে
"""

# ==================== MODULE REGISTRY ====================
# ✅ এখানে শুধু মডিউল নাম যোগ করুন
# Format: "module_name": {"class": "ClassName", "instance_name": "variable_name"}

MODULE_REGISTRY = {
    # Core modules
    "logger": {
        "class": "Logger",
        "instance_name": "logger"
    },
    "time_manager": {
        "class": "TimeManager", 
        "instance_name": "time_manager"
    },
    "helpers": {
        "class": "Helpers",
        "instance_name": "helpers"
    },
    "text_processor": {
        "class": "TextProcessor",
        "instance_name": "text_processor"
    },
    
    # Roast Engine
    "roaster": {
        "class": "RoastEngine",
        "instance_name": "roast_engine"
    },
    "safety_check": {
        "class": "SafetyChecker",
        "instance_name": "safety_checker"
    },
    
    # Image Engine
    "image_generator": {
        "class": "ImageGenerator",
        "instance_name": "image_generator",
        "factory": "get_image_generator"  # যদি factory function থাকে
    },
    
    # Feature Systems
    "welcome_system": {
        "class": "WelcomeSystem",
        "instance_name": "welcome_system"
    },
    "vote_system": {
        "class": "VoteSystem",
        "instance_name": "vote_system"
    },
    "mention_system": {
        "class": "MentionSystem",
        "instance_name": "mention_system"
    },
    "reaction_system": {
        "class": "ReactionSystem",
        "instance_name": "reaction_system"
    },
    "admin_protection": {
        "class": "AdminProtection",
        "instance_name": "admin_protection"
    },
    "sticker_maker": {
        "class": "StickerMaker",
        "instance_name": "sticker_maker"
    },
    "quote_of_day": {
        "class": "QuoteOfDay",
        "instance_name": "quote_of_day",
        "params": ["bot"]  # যদি constructor এ প্যারামিটার লাগে
    }
}

# ==================== MODULE CATEGORIES ====================
MODULE_CATEGORIES = {
    "core": ["logger", "time_manager", "helpers", "text_processor"],
    "roast": ["roaster", "safety_check"],
    "image": ["image_generator"],
    "features": ["welcome_system", "vote_system", "mention_system", 
                 "reaction_system", "admin_protection", "sticker_maker", 
                 "quote_of_day"]
}

# ==================== MODULE DEPENDENCIES ====================
MODULE_DEPENDENCIES = {
    "roaster": ["logger", "safety_check"],
    "image_generator": ["logger"],
    "welcome_system": ["logger"],
    "vote_system": ["logger"],
    "quote_of_day": ["logger"]
}
