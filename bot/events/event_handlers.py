"""
Event Handlers Module
"""
import discord
from discord.ext import commands

# Import welcome settings storage
from config.welcome_settings import get_guild_settings
from config.settings import WELCOME_IMAGE_URL

class EventHandlers:
    def __init__(self, bot):
        self.bot = bot
    
    async def setup_events(self):
        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user} has landed on Discord!')
            try:
                synced = await self.bot.tree.sync()
                print(f"Synced {len(synced)} command(s)")
            except Exception as e:
                print(f"Failed to sync commands: {e}")

        @self.bot.event
        async def on_member_join(member):
            """Welcome new members with a customizable embed"""
            guild_id = str(member.guild.id)
            
            # Get server-specific settings
            guild_settings = get_guild_settings(guild_id)
            
            # Find welcome channel - use custom setting if available, otherwise auto-detect
            welcome_channel = None
            if 'welcome_channel_id' in guild_settings:
                welcome_channel = member.guild.get_channel(guild_settings['welcome_channel_id'])
                if welcome_channel and not welcome_channel.permissions_for(member.guild.me).send_messages:
                    welcome_channel = None  # Can't send messages in configured channel
            
            # If no custom channel or it's invalid, use auto-detection
            if not welcome_channel:
                # Priority order: welcome > general > first available text channel
                for channel in member.guild.text_channels:
                    if channel.name.lower() in ['welcome', 'welcomes']:
                        welcome_channel = channel
                        break
                    elif channel.name.lower() in ['general', 'main', 'chat']:
                        welcome_channel = channel
                        break
                
                # If no specific channel found, use the first text channel the bot can send to
                if not welcome_channel:
                    for channel in member.guild.text_channels:

                        if channel.permissions_for(member.guild.me).send_messages:
                            welcome_channel = channel
                            break
            
            if not welcome_channel:
                return  # No suitable channel found
            
            # Create welcome embed using custom or default settings
            if 'custom_embed' in guild_settings:
                # Use custom embed settings
                custom = guild_settings['custom_embed']
                welcome_embed = discord.Embed(
                    title=self.process_welcome_placeholders(custom.get('title', f"🎉 Welcome to {member.guild.name}!"), member),
                    description=self.process_welcome_placeholders(custom.get('description', f"Welcome to our community!"), member),
                    color=custom.get('color', 0x00ff9f)
                )
                
                # Add custom fields if they exist
                for field in custom.get('fields', []):
                    welcome_embed.add_field(
                        name=self.process_welcome_placeholders(field['name'], member),
                        value=self.process_welcome_placeholders(field['value'], member),
                        inline=field.get('inline', True)
                    )
            else:
                # Use default enhanced welcome embed
                welcome_embed = discord.Embed(
                    title=f"🎊 Welcome to {member.guild.name}! 🎊",
                    description=f"✨ **Hey there, amazing soul!** ✨\n\n🌈 We're absolutely **thrilled** to have you join our incredible community! 💫\n\n🚀 Get ready for an **epic adventure** filled with fun, friendship, and fantastic memories! 🎯",
                    color=0x7289da  # Discord blurple color
                )
            
            # Only add default fields if not using custom embed
            if 'custom_embed' not in guild_settings:
                # Add member info with enhanced styling  
                from datetime import datetime
                join_time = member.joined_at if member.joined_at else datetime.utcnow()
                account_age = (join_time.replace(tzinfo=None) - member.created_at.replace(tzinfo=None)).days
                welcome_embed.add_field(
                    name="👤 About You ✨",
                    value=f"🏷️ **Name:** {member.display_name}",
                    inline=True
                )
                
                # Add enhanced server stats
                welcome_embed.add_field(
                    name="📊 Community Stats 🏆",
                    value=f"👥 **Total Members:** {member.guild.member_count:,}\n🏅 **You're Member:** #{member.guild.member_count}",
                    inline=True
                )
                
                # Add welcome message with emojis
                welcome_embed.add_field(
                    name="🎯 What's Next? 🌟",
                    value="📋 Check out our server rules and guidelines\n💬 Introduce yourself to our amazing community\n🔍 Explore all the awesome channels we have\n🎮 Jump into conversations and activities\n🤝 Make new friends and have a blast!\n💎 Most importantly, **enjoy your stay!**",
                    inline=False
                )
            
            # Set avatar, footer, and timestamp only if not using custom embed with these settings
            if 'custom_embed' not in guild_settings:
                # Set member avatar as thumbnail
                if member.avatar:
                    welcome_embed.set_thumbnail(url=member.avatar.url)
                else:
                    welcome_embed.set_thumbnail(url=member.default_avatar.url)
                
                # Add welcome image as main image if available, otherwise use server banner
                if WELCOME_IMAGE_URL:
                    welcome_embed.set_image(url=WELCOME_IMAGE_URL)
                elif member.guild.banner:
                    welcome_embed.set_image(url=member.guild.banner.url)
                
                # Enhanced footer with timestamp
                current_time = discord.utils.utcnow()
                if member.guild.icon:
                    welcome_embed.set_footer(
                        text=f"🎊 Joined {member.guild.name} • {current_time.strftime('%B %d, %Y at %I:%M %p')} 🎊",
                        icon_url=member.guild.icon.url
                    )
                else:
                    welcome_embed.set_footer(text=f"🎊 Joined {member.guild.name} • {current_time.strftime('%B %d, %Y at %I:%M %p')} 🎊")
                
                # Set timestamp
                welcome_embed.timestamp = current_time
            else:
                # For custom embeds, apply custom settings
                custom = guild_settings['custom_embed']
                if custom.get('thumbnail'):
                    welcome_embed.set_thumbnail(url=self.process_welcome_placeholders(custom['thumbnail'], member))
                elif custom.get('thumbnail') is None:  # Default to user avatar if not explicitly disabled
                    if member.avatar:
                        welcome_embed.set_thumbnail(url=member.avatar.url)
                    else:
                        welcome_embed.set_thumbnail(url=member.default_avatar.url)
                
                if custom.get('image'):
                    welcome_embed.set_image(url=self.process_welcome_placeholders(custom['image'], member))
                elif WELCOME_IMAGE_URL:
                    welcome_embed.set_image(url=WELCOME_IMAGE_URL)
                
                if custom.get('footer'):
                    welcome_embed.set_footer(text=self.process_welcome_placeholders(custom['footer'], member))
                
                if custom.get('timestamp', True):  # Default to True if not specified
                    welcome_embed.timestamp = discord.utils.utcnow()
            
            try:
                # Send the welcome message with user ping outside embed
                welcome_msg = await welcome_channel.send(content=f"👋 {member.mention}", embed=welcome_embed)
                
                # Add welcome reactions
                welcome_reactions = ["🎊", "✨", "💫", "🌟", "🚀", "💎"]
                for reaction in welcome_reactions:
                    try:
                        await welcome_msg.add_reaction(reaction)
                    except:
                        pass  # Ignore reaction errors
                        
            except discord.Forbidden:
                print(f"Failed to send welcome message in {welcome_channel.name} - no permission")
            except Exception as e:
                print(f"Error sending welcome message: {e}")

        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                return
            print(f"An error occurred: {error}")

        @self.bot.event
        async def on_application_command_error(interaction, error):
            if not interaction.response.is_done():
                await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
            print(f"Slash command error: {error}")
    
    def process_welcome_placeholders(self, text, member):
        """Process welcome message placeholders"""
        if not text:
            return text
        
        # User placeholders
        text = text.replace("{user_name}", member.display_name)
        text = text.replace("{user_mention}", member.mention)
        text = text.replace("{user_avatar}", member.avatar.url if member.avatar else member.default_avatar.url)
        text = text.replace("{user_id}", str(member.id))
        
        # Server placeholders
        if member.guild:
            text = text.replace("{server_name}", member.guild.name)
            text = text.replace("{server_icon}", member.guild.icon.url if member.guild.icon else "")
            text = text.replace("{server_member_count}", str(member.guild.member_count))
            text = text.replace("{server_id}", str(member.guild.id))
        
        # Date placeholders
        from datetime import datetime
        now = datetime.now()
        text = text.replace("{date}", now.strftime("%B %d, %Y"))
        text = text.replace("{time}", now.strftime("%I:%M %p"))
        
        return text