"""
Silent Bot - Main Entry Point
A comprehensive Discord bot with music, moderation, and entertainment features.
"""
import asyncio
import discord
from discord.ext import commands

# Import configuration
from config.settings import DISCORD_TOKEN, INTENTS, BOT_PREFIX, BOT_DESCRIPTION

# Import prefix manager
from bot.database.prefix_manager import prefix_manager

# Import command modules
from bot.commands.music import MusicCommands
from bot.commands.moderation import ModerationCommands
from bot.commands.actions import ActionCommands
from bot.commands.utility import UtilityCommands
from bot.commands.games import GamesCommands

# Import event handlers
from bot.events.event_handlers import EventHandlers


def get_prefix(bot, message):
    """Dynamic prefix function for per-guild custom prefixes"""
    if message.guild is None:
        # DMs use default prefix
        return commands.when_mentioned_or(BOT_PREFIX)(bot, message)
    
    # Get custom prefix for this guild
    custom_prefix = prefix_manager.get_prefix(message.guild.id)
    return commands.when_mentioned_or(custom_prefix)(bot, message)

class SilentMusicBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,  # Use dynamic prefix function
            description=BOT_DESCRIPTION,
            intents=INTENTS,
            help_command=None  # We have our own custom help command
        )

    async def setup_hook(self):
        """Setup hook called when the bot is starting up"""
        print("Setting up Silent Music Bot...")

        # Initialize command modules
        music_commands = MusicCommands(self)
        moderation_commands = ModerationCommands(self)
        action_commands = ActionCommands(self)
        utility_commands = UtilityCommands(self)
        games_commands = GamesCommands(self)
        event_handlers = EventHandlers(self)

        # Setup all commands
        await music_commands.setup_commands()
        await moderation_commands.setup_commands()
        await action_commands.setup_commands()
        await utility_commands.setup_commands()
        await games_commands.setup_commands()
        await event_handlers.setup_events()

        print("All modules loaded successfully!")
        
        # Load levelling system using the async cog method
        try:
            await self.load_extension('bot.commands.levelling')
            await self.load_extension('bot.commands.levelling_admin')
            await self.load_extension('bot.events.levelling_handler')
            print("✅ Levelling system loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to load levelling system: {e}")
        
        # Load economy system
        try:
            await self.load_extension('bot.commands.economy')
            await self.load_extension('bot.commands.shop')
            await self.load_extension('bot.commands.economy_admin')
            print("✅ Economy system loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to load economy system: {e}")
        
        # Load prefix management system
        try:
            await self.load_extension('bot.commands.prefix_admin')
            print("✅ Prefix management system loaded successfully!")
        except Exception as e:
            print(f"❌ Failed to load prefix management system: {e}")

        # Sync commands to Discord for immediate availability
        try:
            # Sync globally first (takes up to 1 hour to propagate)
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} command(s) globally")
            
            # Force sync to current guilds for immediate availability
            guild_synced = 0
            for guild in self.guilds:
                try:
                    await self.tree.sync(guild=guild)
                    guild_synced += 1
                except Exception as e:
                    print(f"⚠️ Failed to sync to guild {guild.name}: {e}")
            
            if guild_synced > 0:
                print(f"✅ Force synced commands to {guild_synced} guild(s) for immediate availability")
            
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                print(f"⚠️ Rate limited! Waiting before retry...")
                await asyncio.sleep(60)  # Wait 60 seconds
            else:
                print(f"❌ Failed to sync commands: {e}")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")


async def main():
    """Main function to run the bot"""
    if not DISCORD_TOKEN:
        print("❌ Error: DISCORD_TOKEN environment variable is not set!")
        print(
            "Please set your Discord bot token in the environment variables.")
        return

    bot = SilentMusicBot()

    try:
        print("Starting Discord Bot...")
        print("Make sure to set your DISCORD_TOKEN environment variable!")
        await bot.start(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ Failed to log in. Please check your Discord token.")
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Program interrupted by user.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
