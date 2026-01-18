"""
Features package for RoastifyBot
"""

from .quote_of_day import QuoteOfDay, setup as setup_quotes
from .welcome_system import WelcomeSystem
from .vote_system import VoteSystem
from .mention_system import MentionSystem
from .reaction_system import ReactionSystem
from .admin_protection import AdminProtection
from .auto_quotes import AutoQuotes

__all__ = [
    'QuoteOfDay',
    'WelcomeSystem',
    'VoteSystem',
    'MentionSystem',
    'ReactionSystem',
    'AdminProtection',
    'AutoQuotes',
    'setup_quotes'
]
