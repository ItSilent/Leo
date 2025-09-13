# Overview

This is a comprehensive Discord bot built with Python that provides music playback, server moderation, interactive entertainment, and advanced utility features. The bot uses discord.py for Discord integration and yt-dlp for YouTube audio extraction. It features a queue system to manage multiple songs per server, automatic welcome messages for new members, and a powerful interactive embed builder similar to popular bots like Mimu.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes

## Complete Economy Ecosystem Added (September 2025)
- **💰 Virtual Currency System**: Full coin-based economy with earning, spending, and wealth tracking
- **🎁 Daily Rewards**: Streak-based daily rewards with escalating bonuses (up to 500 coins/day)
- **💼 Work System**: 6 different jobs (Programmer, Designer, Streamer, Chef, Gamer, Teacher) with experience progression and skill-based pay increases
- **🎰 Casino Games**: Slots machine with jackpots and coinflip betting for entertainment
- **🛒 Shop & Inventory**: Complete shopping system with 6 item types (Custom Role Colors, VIP Status, Custom Titles, Gift Boxes, XP Boosts, Daily Streak Protection)
- **🏦 Banking System**: Separate bank storage for secure coin management
- **📊 Leaderboards**: Multiple ranking systems (richest users, top earners, streak champions)
- **🔗 Levelling Integration**: Users earn 50 coins per level up, creating synergy between systems
- **⚙️ Admin Tools**: Full administrative control with coin management and economy statistics
- **📈 Transaction Logging**: Complete audit trail for all economy activities

## Hybrid Command System Added (September 2025)
- **🔄 Dual Command Support**: Every command works as both slash commands (/balance) and prefix commands (!balance)
- **⚙️ Per-Guild Prefix Customization**: Admins can set custom prefixes (?, >, ., etc.) with `/setprefix`
- **🎯 Dynamic Prefix Resolution**: Bot automatically detects and uses the correct prefix per server
- **📋 Prefix Management Commands**: `/prefix`, `/setprefix`, `/resetprefix` for full prefix control
- **🏷️ Hybrid Help System**: Help displays both slash and prefix command syntax dynamically
- **🔧 Hybrid-Safe Response System**: Smart response handling prevents ephemeral parameter errors

## Previous Features (September 2025)  
- **Welcome Message System**: Automatic welcome messages with embeds for new server members
- **Interactive Embed Builder**: Comprehensive embed creation tool with buttons for customization
- **Enhanced User Experience**: Mimu-like interface with modal forms and interactive buttons
- **Welcome Customization Commands**: Moderation tools for customizing welcome channel and message content
- **Dynamic Placeholder System**: Support for placeholders in custom welcome messages

# System Architecture

## Bot Framework
- **Discord.py**: Core Discord API wrapper handling bot interactions, voice connections, and command processing
- **Command System**: Uses discord.py's slash commands for modern user interactions
- **Intents Configuration**: Enables message content and voice state monitoring for full bot functionality

## Economy System Architecture
- **EconomySystem Class**: Centralized virtual economy management with JSON persistence
- **Multi-Guild Support**: Separate economy data per Discord server to prevent cross-server interference
- **File-Based Storage**: JSON files for economy data, shop items, and transaction logs
- **Transaction Logging**: Complete audit trail with timestamps and reasons for all coin movements
- **Job Experience System**: Progressive skill improvement with better pay rates over time
- **Casino Games**: Slot machine with configurable payouts and coinflip betting system

## Audio Processing Pipeline
- **yt-dlp**: YouTube audio extraction library replacing the deprecated youtube-dl
- **FFmpeg**: Audio streaming and format conversion for Discord voice channels
- **Audio Options**: Configured for best audio quality with reconnection handling for stable streaming

## Queue Management System
- **MusicBot Class**: Centralized music management system handling multiple Discord servers
- **Per-Guild Queues**: Separate music queues for each Discord server to prevent cross-server interference
- **Voice Client Tracking**: Maintains voice connections and current playback state per server
- **Song State Management**: Tracks currently playing songs across different servers

## Data Storage
- **Music System**: In-memory storage for queue data, voice clients, and song states (session-based)
- **Economy System**: Persistent JSON storage for user balances, transactions, and shop data
- **Levelling System**: Persistent JSON storage for XP data and role rewards
- **Guild-Scoped Data**: All systems partition data by Discord guild ID for multi-server support
- **File Structure**: 
  - `bot/data/economy.json`: User coin balances and statistics
  - `bot/data/shop.json`: Available shop items and configurations
  - `bot/data/transactions.json`: Transaction history and audit logs

## Audio Configuration
- **Streaming Quality**: Configured for best available audio quality from YouTube
- **Connection Resilience**: FFmpeg options include reconnection logic for unstable network conditions
- **Format Restrictions**: Safe filename handling and audio-only extraction to prevent issues

# External Dependencies

## Core Libraries
- **discord.py**: Discord API integration and bot framework
- **yt-dlp**: YouTube audio extraction and metadata retrieval
- **asyncio**: Asynchronous programming support for Discord operations

## System Dependencies  
- **FFmpeg**: Required system binary for audio processing and streaming
- **Python 3.7+**: Runtime environment for the bot

## External Services
- **Discord API**: Real-time communication with Discord servers and voice channels
- **YouTube**: Audio content source through yt-dlp extraction
- **Various Audio Platforms**: yt-dlp supports multiple platforms beyond YouTube

## Environment Requirements
- **Discord Bot Token**: Required authentication for Discord API access
- **Network Access**: Stable internet connection for audio streaming and Discord communication
- **Voice Channel Permissions**: Bot requires appropriate Discord permissions for voice operations