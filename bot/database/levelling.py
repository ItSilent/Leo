import json
import os
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import discord

class LevellingSystem:
    def __init__(self):
        self.data_dir = "bot/data"
        self.levels_file = os.path.join(self.data_dir, "levels.json")
        self.server_settings_file = os.path.join(self.data_dir, "server_settings.json")
        self.warnings_file = os.path.join(self.data_dir, "warnings.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data files if they don't exist
        self._init_files()
        
        # XP settings
        self.xp_per_message = 15
        self.xp_cooldown = 60  # seconds
        self.xp_bonus_min = 5
        self.xp_bonus_max = 25
        
        # Spam detection settings
        self.spam_message_limit = 5
        self.spam_time_window = 10  # seconds
        self.max_warnings = 3
        
        # Level calculation cache
        self._level_cache = {}
        
    def _init_files(self):
        """Initialize JSON data files"""
        files = [self.levels_file, self.server_settings_file, self.warnings_file]
        default_data = [{}, {}, {}]
        
        for file_path, default in zip(files, default_data):
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default, f, indent=2)
    
    def _load_data(self, file_path: str) -> dict:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, file_path: str, data: dict):
        """Save data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_level(self, xp: int) -> int:
        """Calculate level from XP using a curved formula"""
        if xp in self._level_cache:
            return self._level_cache[xp]
        
        # Level formula: sqrt(xp / 100) - gives nice progression
        level = int((xp / 100) ** 0.5) + 1
        self._level_cache[xp] = level
        return level
    
    def calculate_xp_for_level(self, level: int) -> int:
        """Calculate XP needed for a specific level"""
        return ((level - 1) ** 2) * 100
    
    def get_user_data(self, guild_id: int, user_id: int) -> dict:
        """Get user's level data"""
        data = self._load_data(self.levels_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        if guild_str not in data:
            data[guild_str] = {}
        
        if user_str not in data[guild_str]:
            data[guild_str][user_str] = {
                "xp": 0,
                "level": 1,
                "last_message": 0,
                "total_messages": 0
            }
            self._save_data(self.levels_file, data)
        
        return data[guild_str][user_str]
    
    def add_xp(self, guild_id: int, user_id: int, amount: Optional[int] = None) -> Tuple[bool, int, int, int]:
        """
        Add XP to user and check for level up
        Returns: (level_up_occurred, new_xp, old_level, new_level)
        """
        data = self._load_data(self.levels_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        # Get current data
        user_data = self.get_user_data(guild_id, user_id)
        current_time = datetime.now().timestamp()
        
        # Check cooldown
        if current_time - user_data["last_message"] < self.xp_cooldown:
            return False, user_data["xp"], user_data["level"], user_data["level"]
        
        # Calculate XP to add
        if amount is None:
            import random
            amount = self.xp_per_message + random.randint(self.xp_bonus_min, self.xp_bonus_max)
        
        # Update user data
        old_level = user_data["level"]
        user_data["xp"] += amount
        user_data["last_message"] = current_time
        user_data["total_messages"] += 1
        
        # Calculate new level
        new_level = self.calculate_level(user_data["xp"])
        user_data["level"] = new_level
        
        # Save data
        data[guild_str][user_str] = user_data
        self._save_data(self.levels_file, data)
        
        level_up = new_level > old_level
        return level_up, user_data["xp"], old_level, new_level
    
    def get_leaderboard(self, guild_id: int, limit: Optional[int] = 10) -> List[Tuple[int, dict]]:
        """Get server leaderboard"""
        data = self._load_data(self.levels_file)
        guild_str = str(guild_id)
        
        if guild_str not in data:
            return []
        
        # Sort by XP
        users = [(int(user_id), user_data) for user_id, user_data in data[guild_str].items()]
        users.sort(key=lambda x: x[1]["xp"], reverse=True)
        
        if limit is None:
            return users
        return users[:limit]
    
    def get_user_rank(self, guild_id: int, user_id: int) -> int:
        """Get user's rank in server"""
        leaderboard = self.get_leaderboard(guild_id, limit=None)
        for rank, (uid, _) in enumerate(leaderboard, 1):
            if uid == user_id:
                return rank
        return 0
    
    # Server Settings
    def get_server_settings(self, guild_id: int) -> dict:
        """Get server settings"""
        data = self._load_data(self.server_settings_file)
        guild_str = str(guild_id)
        
        if guild_str not in data:
            data[guild_str] = {
                "levelup_channel": None,
                "level_roles": {},  # level: role_id
                "xp_enabled": True,
                "levelup_message": "🎉 {user_mention} leveled up to **Level {level}**! 🚀",
                "spam_protection": True
            }
            self._save_data(self.server_settings_file, data)
        
        return data[guild_str]
    
    def update_server_settings(self, guild_id: int, **kwargs):
        """Update server settings"""
        data = self._load_data(self.server_settings_file)
        guild_str = str(guild_id)
        
        settings = self.get_server_settings(guild_id)
        settings.update(kwargs)
        data[guild_str] = settings
        
        self._save_data(self.server_settings_file, data)
    
    def set_level_role(self, guild_id: int, level: int, role_id: int):
        """Set role for a specific level"""
        settings = self.get_server_settings(guild_id)
        settings["level_roles"][str(level)] = role_id
        self.update_server_settings(guild_id, level_roles=settings["level_roles"])
    
    def remove_level_role(self, guild_id: int, level: int):
        """Remove role for a specific level"""
        settings = self.get_server_settings(guild_id)
        if str(level) in settings["level_roles"]:
            del settings["level_roles"][str(level)]
            self.update_server_settings(guild_id, level_roles=settings["level_roles"])
    
    def get_level_roles(self, guild_id: int) -> dict:
        """Get all level roles for server"""
        settings = self.get_server_settings(guild_id)
        return settings["level_roles"]
    
    # Spam Detection & Warnings
    def check_spam(self, guild_id: int, user_id: int) -> bool:
        """Check if user is spamming"""
        data = self._load_data(self.warnings_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        current_time = datetime.now().timestamp()
        
        if guild_str not in data:
            data[guild_str] = {}
        
        if user_str not in data[guild_str]:
            data[guild_str][user_str] = {
                "recent_messages": [],
                "warnings": 0,
                "last_warning": 0
            }
        
        user_data = data[guild_str][user_str]
        
        # Add current message timestamp
        user_data["recent_messages"].append(current_time)
        
        # Remove old messages outside time window
        cutoff_time = current_time - self.spam_time_window
        user_data["recent_messages"] = [
            msg_time for msg_time in user_data["recent_messages"] 
            if msg_time > cutoff_time
        ]
        
        # Check if spam limit exceeded
        is_spam = len(user_data["recent_messages"]) > self.spam_message_limit
        
        # Save data
        data[guild_str][user_str] = user_data
        self._save_data(self.warnings_file, data)
        
        return is_spam
    
    def add_warning(self, guild_id: int, user_id: int) -> Tuple[int, bool]:
        """
        Add warning to user
        Returns: (warning_count, should_timeout)
        """
        data = self._load_data(self.warnings_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        current_time = datetime.now().timestamp()
        
        if guild_str not in data:
            data[guild_str] = {}
        
        if user_str not in data[guild_str]:
            data[guild_str][user_str] = {
                "recent_messages": [],
                "warnings": 0,
                "last_warning": 0
            }
        
        user_data = data[guild_str][user_str]
        user_data["warnings"] += 1
        user_data["last_warning"] = current_time
        
        # Clear recent messages after warning
        user_data["recent_messages"] = []
        
        should_timeout = user_data["warnings"] >= self.max_warnings
        
        # Save data
        data[guild_str][user_str] = user_data
        self._save_data(self.warnings_file, data)
        
        return user_data["warnings"], should_timeout
    
    def get_user_warnings(self, guild_id: int, user_id: int) -> int:
        """Get user's warning count"""
        data = self._load_data(self.warnings_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        if guild_str not in data or user_str not in data[guild_str]:
            return 0
        
        return data[guild_str][user_str]["warnings"]
    
    def reset_warnings(self, guild_id: int, user_id: int):
        """Reset user's warnings"""
        data = self._load_data(self.warnings_file)
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        if guild_str in data and user_str in data[guild_str]:
            data[guild_str][user_str]["warnings"] = 0
            data[guild_str][user_str]["recent_messages"] = []
            self._save_data(self.warnings_file, data)

# Global instance
levelling_system = LevellingSystem()