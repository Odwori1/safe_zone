from datetime import datetime, timezone
from typing import Optional, Dict
import pytz
from fastapi import Request

class TimezoneHandler:
    """
    Global timezone handling utilities for Safe Zone
    Auto-detects timezone from request headers for global mental health platform
    """
    
    @staticmethod
    def get_utc_now() -> datetime:
        """Get current time in UTC with timezone awareness"""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def ensure_utc(dt: datetime) -> datetime:
        """Ensure datetime is in UTC timezone"""
        if dt.tzinfo is None:
            # Assume naive datetime is in UTC (database storage)
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    
    @staticmethod
    def detect_timezone_from_request(request: Request) -> str:
        """
        Auto-detect timezone from request headers
        Priority: 1. Timezone header 2. Offset header 3. Default UTC
        """
        # Check for explicit timezone header
        timezone_header = request.headers.get("X-Timezone")
        if timezone_header and TimezoneHandler.validate_timezone(timezone_header):
            return timezone_header
        
        # Check for UTC offset header (common in mobile apps/browsers)
        offset_header = request.headers.get("X-Timezone-Offset")
        if offset_header:
            try:
                offset_hours = int(offset_header)
                return TimezoneHandler._get_timezone_from_offset(offset_hours)
            except (ValueError, TypeError):
                pass
        
        # Fallback to UTC
        return "UTC"
    
    @staticmethod
    def _get_timezone_from_offset(offset_hours: int) -> str:
        """Convert UTC offset to approximate timezone"""
        # Common timezone mappings based on UTC offset
        offset_mapping = {
            -12: "Pacific/Fiji",      # Fiji
            -11: "Pacific/Samoa",     # Samoa
            -10: "US/Hawaii",         # Hawaii
            -9: "US/Alaska",          # Alaska
            -8: "US/Pacific",         # Pacific Time
            -7: "US/Mountain",        # Mountain Time
            -6: "US/Central",         # Central Time
            -5: "US/Eastern",         # Eastern Time
            -4: "America/Puerto_Rico", # Atlantic Time
            -3: "America/Sao_Paulo",  # Brazil
            -2: "America/Noronha",    # Fernando de Noronha
            -1: "Atlantic/Azores",    # Azores
            0: "UTC",                 # UTC
            1: "Europe/London",       # UK
            2: "Europe/Paris",        # Central Europe
            3: "Europe/Moscow",       # Moscow
            4: "Asia/Dubai",          # UAE
            5: "Asia/Karachi",        # Pakistan
            6: "Asia/Dhaka",          # Bangladesh
            7: "Asia/Bangkok",        # Thailand
            8: "Asia/Shanghai",       # China
            9: "Asia/Tokyo",          # Japan
            10: "Australia/Sydney",   # Eastern Australia
            11: "Pacific/Noumea",     # New Caledonia
            12: "Pacific/Auckland",   # New Zealand
        }
        
        return offset_mapping.get(offset_hours, "UTC")
    
    @staticmethod
    def to_user_timezone(dt: datetime, user_timezone: str = 'UTC') -> datetime:
        """Convert UTC datetime to user's detected timezone"""
        utc_dt = TimezoneHandler.ensure_utc(dt)
        try:
            user_tz = pytz.timezone(user_timezone)
            return utc_dt.astimezone(user_tz)
        except pytz.UnknownTimeZoneError:
            # Fallback to UTC for invalid timezones
            return utc_dt
    
    @staticmethod
    def format_for_display(dt: datetime, user_timezone: str = 'UTC') -> str:
        """
        Format datetime for display in user's timezone
        Essential for posts, messages, journal entries in mental health app
        """
        localized_dt = TimezoneHandler.to_user_timezone(dt, user_timezone)
        
        # Smart formatting based on recency (good for mental health timeline)
        now_utc = TimezoneHandler.get_utc_now()
        dt_utc = TimezoneHandler.ensure_utc(dt)
        diff = now_utc - dt_utc
        
        if diff.days == 0:
            # Today - show time only
            return localized_dt.strftime("%H:%M")
        elif diff.days == 1:
            # Yesterday
            return "Yesterday"
        elif diff.days < 7:
            # Within week - show day name
            return localized_dt.strftime("%A")
        else:
            # Older - show date
            return localized_dt.strftime("%b %d, %Y")
    
    @staticmethod
    def format_relative_time(dt: datetime, user_timezone: str = 'UTC') -> str:
        """Format as relative time (e.g., '2 hours ago') - good for activity feeds"""
        now_utc = TimezoneHandler.get_utc_now()
        dt_utc = TimezoneHandler.ensure_utc(dt)
        
        diff = now_utc - dt_utc
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    
    @staticmethod
    def validate_timezone(timezone_str: str) -> bool:
        """Validate if timezone string is valid"""
        try:
            pytz.timezone(timezone_str)
            return True
        except pytz.UnknownTimeZoneError:
            return False
    
    @staticmethod
    def get_supported_locales():
        """Return supported locales for internationalization"""
        return {
            'en-US': 'English (US)',
            'es-ES': 'Español (Spain)',
            'fr-FR': 'Français (France)',
            'de-DE': 'Deutsch (Germany)',
            'pt-BR': 'Português (Brazil)',
            'zh-CN': '中文 (China)',
            'ja-JP': '日本語 (Japan)',
            'ar-SA': 'العربية (Saudi Arabia)',
            'hi-IN': 'हिन्दी (India)'
        }

# Global instance
timezone_handler = TimezoneHandler()
