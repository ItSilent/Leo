# 🎵 Silent Bot

A comprehensive Discord bot featuring music playback, moderation tools, and entertainment commands with beautiful interactive interfaces.

## ✨ Features

### 🎵 Music System
- **YouTube Integration** - Play any song from YouTube
- **Queue Management** - Multiple songs per server with queue system
- **Interactive Controls** - Pause, resume, skip buttons on music embeds
- **High-Quality Audio** - Opus encoding for best audio quality

### 🛡️ Moderation Tools
- **Member Management** - Kick, ban, and timeout commands
- **Message Cleanup** - Bulk delete messages (1-100)
- **Democratic System** - No special permissions required
- **Detailed Logging** - All moderation actions are tracked

### 🎭 Action Commands
- **8 Interactive Commands** - Hug, kiss, slap, poke, pat, cuddle, dance, wave
- **Animated GIFs** - Beautiful anime-style reaction GIFs
- **Giphy Integration** - Fresh content with reliable fallbacks
- **Colorful Embeds** - Each action has unique styling

### 🔧 Utility Features
- **Interactive Help System** - Beautiful button-based command navigation
- **Detailed Bot Information** - Live statistics and feature descriptions
- **Professional Embeds** - Clean, organized information display

## 🏗️ Project Structure

```
├── main.py                 # Main bot entry point
├── config/
│   └── settings.py         # Bot configuration and settings
├── bot/
│   ├── commands/
│   │   ├── music.py        # Music-related commands
│   │   ├── moderation.py   # Moderation commands
│   │   ├── actions.py      # Fun action commands
│   │   └── utility.py      # Info and help commands
│   ├── utils/
│   │   ├── music_bot.py    # Music bot utilities and classes
│   │   └── gif_handler.py  # GIF fetching and management
│   └── events/
│       └── event_handlers.py # Discord event handlers
├── main_old.py            # Original monolithic file (backup)
└── README.md              # This file
```

## 🚀 Commands

### Music Commands (4)
- `/play [song]` - Play a song from YouTube
- `/queue` - Show the current music queue
- `/skip` - Skip the current song
- `/stop` - Stop music and disconnect

### Moderation Commands (4)
- `/kick [member] [reason]` - Kick a member
- `/ban [member] [reason]` - Ban a member
- `/timeout [member] [duration] [reason]` - Timeout a member
- `/clear [amount]` - Delete messages in bulk

### Action Commands (8)
- `/hug [user]` - Give someone a warm hug
- `/kiss [user]` - Give someone a sweet kiss
- `/slap [user]` - Slap someone playfully
- `/poke [user]` - Poke someone to get attention
- `/pat [user]` - Give someone a gentle pat
- `/cuddle [user]` - Cuddle with someone
- `/dance [user]` - Dance with someone (optional)
- `/wave [user]` - Wave hello to someone

### Utility Commands (2)
- `/info` - Get detailed bot information
- `/help` - Interactive help system with buttons

## 🛠️ Technical Details

- **Language:** Python 3.11+
- **Framework:** discord.py 2.0+
- **Audio Engine:** FFmpeg + yt-dlp
- **Architecture:** Modular, async/await pattern
- **Hosting:** Replit Cloud Platform

## 📝 Environment Variables

Required environment variables:
- `DISCORD_TOKEN` - Your Discord bot token
- `TENOR_API_KEY` - Tenor API key (optional, has fallbacks)

## 🎯 Installation & Setup

1. Set up your Discord bot token in environment variables
2. Install dependencies (handled automatically on Replit)
3. Run `python main.py`
4. Bot will automatically sync slash commands

## 💡 Key Features

- **Modular Architecture** - Clean, organized codebase
- **Error Handling** - Comprehensive error management
- **Interactive UI** - Button-based controls and navigation
- **Professional Embeds** - Beautiful, informative displays
- **No Permission Requirements** - Democratic access to all features
- **Reliable Fallbacks** - Works even when external APIs fail

---

*Made with ❤️ by Itz_Silent*