from datetime import datetime, timedelta
import pytz
from config import Config

class TimeManager:
    _timezone = pytz.timezone(Config.TIMEZONE)
    
    @classmethod
    def get_current_time(cls) -> datetime:
        """বর্তমান সময় রিটার্ন করে"""
        return datetime.now(cls._timezone)
    
    @classmethod
    def get_current_hour(cls) -> int:
        """বর্তমান ঘণ্টা রিটার্ন করে"""
        return cls.get_current_time().hour
    
    @classmethod
    def is_day_time(cls) -> bool:
        """দিনের সময় কিনা চেক করে"""
        hour = cls.get_current_hour()
        return 6 <= hour < 19
    
    @classmethod
    def format_time(cls, dt: datetime = None) -> str:
        """টাইম ফরম্যাট করে"""
        if dt is None:
            dt = cls.get_current_time()
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def is_within_cooldown(cls, last_time: datetime, cooldown_seconds: int) -> bool:
        """কুলডাউন সময়ের মধ্যে কিনা চেক করে"""
        if not last_time:
            return False
        
        now = cls.get_current_time()
        time_diff = (now - last_time).total_seconds()
        return time_diff < cooldown_seconds
    
    @classmethod
    def get_time_remaining(cls, last_time: datetime, cooldown_seconds: int) -> int:
        """কত সময় বাকি আছে রিটার্ন করে"""
        if not last_time:
            return 0
        
        now = cls.get_current_time()
        time_diff = (now - last_time).total_seconds()
        remaining = max(0, cooldown_seconds - int(time_diff))
        return remaining