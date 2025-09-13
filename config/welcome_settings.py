"""
Welcome Settings Storage Module
Centralized storage for server-specific welcome configurations
"""

# Server-specific welcome settings storage
# Format: {guild_id: {welcome_channel_id: int, custom_embed: dict}}
server_welcome_settings = {}

def get_guild_settings(guild_id: str) -> dict:
    """Get welcome settings for a specific guild"""
    return server_welcome_settings.get(guild_id, {})

def set_guild_settings(guild_id: str, settings: dict) -> None:
    """Set welcome settings for a specific guild"""
    if guild_id not in server_welcome_settings:
        server_welcome_settings[guild_id] = {}
    server_welcome_settings[guild_id].update(settings)

def clear_guild_settings(guild_id: str) -> None:
    """Clear all welcome settings for a specific guild"""
    if guild_id in server_welcome_settings:
        del server_welcome_settings[guild_id]