"""
Bot Configuration Settings
"""
import os
from discord import Intents

# Bot Configuration
BOT_PREFIX = "!"
BOT_DESCRIPTION = "A comprehensive Discord bot with music, moderation, and entertainment features"

# Discord Intents
INTENTS = Intents.default()
INTENTS.message_content = True
INTENTS.voice_states = True
INTENTS.guilds = True
INTENTS.guild_messages = True
INTENTS.members = True  # Required for member join events

# Environment Variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TENOR_API_KEY = os.getenv('TENOR_API_KEY')
BOT_INVITE_LINK = os.getenv('BOT_INVITE_LINK')
SUPPORT_SERVER_LINK = os.getenv('SUPPORT_SERVER_LINK')
WELCOME_IMAGE_URL = os.getenv('WELCOME_IMAGE_URL')

# Music Configuration
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
    'executable': 'ffmpeg'
}

# Embed Colors
COLORS = {
    'music': 0xff6b6b,
    'moderation': 0x4ecdc4,
    'action': 0xffbe0b,
    'info': 0x00ff9f,
    'help': 0x00aaff,
    'utility': 0x6c5ce7,
    'error': 0xff4757,
    'success': 0x2ed573
}