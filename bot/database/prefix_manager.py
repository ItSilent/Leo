import json
import os
from typing import Dict, Optional

class PrefixManager:
    def __init__(self):
        self.data_dir = "bot/data"
        self.prefix_file = os.path.join(self.data_dir, "guild_prefixes.json")
        self.default_prefix = "!"
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize prefix file
        self._init_file()
        
        # Cache for loaded prefixes
        self._prefix_cache = {}
        self._load_prefixes()
    
    def _init_file(self):
        """Initialize the prefix storage file"""
        if not os.path.exists(self.prefix_file):
            with open(self.prefix_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def _load_prefixes(self):
        """Load all prefixes into cache"""
        try:
            with open(self.prefix_file, 'r') as f:
                self._prefix_cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._prefix_cache = {}
    
    def _save_prefixes(self):
        """Save prefixes to file"""
        with open(self.prefix_file, 'w') as f:
            json.dump(self._prefix_cache, f, indent=2)
    
    def get_prefix(self, guild_id: Optional[int]) -> str:
        """
        Get the prefix for a guild
        Returns default prefix if guild_id is None (DMs) or not found
        """
        if guild_id is None:
            return self.default_prefix
        
        guild_str = str(guild_id)
        return self._prefix_cache.get(guild_str, self.default_prefix)
    
    def set_prefix(self, guild_id: int, prefix: str) -> bool:
        """
        Set a custom prefix for a guild
        Returns True if successful, False if invalid
        """
        # Validate prefix
        if not self._validate_prefix(prefix):
            return False
        
        guild_str = str(guild_id)
        self._prefix_cache[guild_str] = prefix
        self._save_prefixes()
        return True
    
    def reset_prefix(self, guild_id: int) -> str:
        """
        Reset guild prefix to default
        Returns the default prefix
        """
        guild_str = str(guild_id)
        if guild_str in self._prefix_cache:
            del self._prefix_cache[guild_str]
            self._save_prefixes()
        return self.default_prefix
    
    def get_all_prefixes(self) -> Dict[str, str]:
        """Get all guild prefixes"""
        return self._prefix_cache.copy()
    
    def _validate_prefix(self, prefix: str) -> bool:
        """
        Validate that a prefix is acceptable
        Rules:
        - Must be 1-5 characters long
        - Cannot contain spaces or newlines
        - Cannot be only whitespace
        - Cannot contain @ or # (mentions/channels)
        - Cannot start with / (slash commands)
        """
        if not prefix or len(prefix) > 5 or len(prefix.strip()) == 0:
            return False
        
        if any(char in prefix for char in [' ', '\n', '\t', '@', '#']):
            return False
        
        if prefix.startswith('/'):
            return False
        
        return True

# Global instance
prefix_manager = PrefixManager()