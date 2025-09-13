"""
Utility Commands Module (Info and Help)
"""
import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional
from config.settings import COLORS, BOT_INVITE_LINK, SUPPORT_SERVER_LINK

# Import welcome settings storage
from config.welcome_settings import get_guild_settings, set_guild_settings, clear_guild_settings

class UtilityCommands:
    def __init__(self, bot):
        self.bot = bot

    async def setup_commands(self):
        @self.bot.tree.command(name="info", description="Quick bot info and stats")
        async def info(interaction: discord.Interaction):
            embed = discord.Embed(
                title="🤖 **Leo Bot**",
                description="*Ultimate Discord experience with music, economy & more!*",
                color=0x00ff88
            )
            
            # Compact stats in one field
            embed.add_field(
                name="📊 **Quick Stats**",
                value=f"🏠 **{len(self.bot.guilds)}** servers\n"
                      f"⚡ **{round(self.bot.latency * 1000)}ms** ping\n"
                      f"⚙️ **56** commands",
                inline=True
            )
            
            # Core features in one field
            embed.add_field(
                name="✨ **Core Features**",
                value="🎵 **Music** • 💰 **Economy**\n"
                      "📈 **Levelling** • 🛡️ **Moderation**\n"
                      "🎮 **Games** • 🎨 **Customization**",
                inline=True
            )
            
            # Quick action buttons
            embed.add_field(
                name="🚀 **Get Started**",
                value="❓ Type `/help` for commands\n"
                      "⚙️ Use `/setprefix` to customize\n"
                      "💬 Join support for help",
                inline=False
            )
            
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.set_footer(text="Leo • Built with 💜", icon_url=self.bot.user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)

        # Interactive Embed Builder Command 
        @self.bot.tree.command(name="embed", description="Create custom embeds with an interactive builder")
        @discord.app_commands.describe(
            channel="Channel to send the embed to (optional, defaults to current channel)"
        )
        async def embed_command(
            interaction: discord.Interaction,
            channel: Optional[discord.TextChannel] = None
        ):
            if not interaction.guild:
                await interaction.response.send_message("❌ This command can only be used in a server!", ephemeral=True)
                return
            
            # Use current channel if no channel specified
            target_channel = channel or interaction.channel
            
            # Check permissions
            bot_member = interaction.guild.get_member(self.bot.user.id)
            if not bot_member or not target_channel.permissions_for(bot_member).send_messages:
                await interaction.response.send_message(f"❌ I don't have permission to send messages in {target_channel.mention}!", ephemeral=True)
                return
            
            # Create the embed builder
            embed_builder = EmbedBuilder(interaction.user, target_channel)
            view = EmbedBuilderView(embed_builder, self.bot)
            
            await interaction.response.send_message(embed=embed_builder.create_preview_embed(), view=view, ephemeral=True)

        # Welcome Command (Admin only)
        @self.bot.tree.command(name="welcome", description="Test or send welcome message for a user")
        @discord.app_commands.describe(user="User to welcome (optional, defaults to you)")
        async def welcome_command(interaction: discord.Interaction, user: Optional[discord.Member] = None):
            # Check if user has manage server permissions
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("❌ You need 'Manage Server' permissions to use this command!", ephemeral=True)
                return
            
            target_user = user or interaction.user
            
            # Create the same welcome embed as the automatic system
            welcome_embed = discord.Embed(
                title=f"🎉 Welcome to {interaction.guild.name}!",
                description=f"Hey {target_user.mention}! 👋\n\n**We're thrilled to have you join our amazing community!** 🌟\n\nGet ready for an awesome experience here! 🚀",
                color=COLORS['success']
            )
            
            # Add member info
            if hasattr(target_user, 'joined_at') and target_user.joined_at:
                account_age = (target_user.joined_at.replace(tzinfo=None) - target_user.created_at.replace(tzinfo=None)).days
            else:
                account_age = (datetime.utcnow() - target_user.created_at.replace(tzinfo=None)).days
                
            welcome_embed.add_field(
                name="👤 About You",
                value=f"**Name:** {target_user.display_name}\n**Account:** {target_user.created_at.strftime('%b %d, %Y')}\n**Age:** {account_age} days old",
                inline=True
            )
            
            # Add server stats
            welcome_embed.add_field(
                name="📊 Community Stats",
                value=f"**Members:** {interaction.guild.member_count:,} total\n**You're:** Member #{interaction.guild.member_count}\n**Server:** Created {interaction.guild.created_at.strftime('%b %Y')}",
                inline=True
            )
            
            # Add getting started info
            welcome_embed.add_field(
                name="🎯 What's Next?",
                value="🔸 Check out our server rules\n🔸 Introduce yourself to the community\n🔸 Explore different channels\n🔸 Have fun and make new friends!",
                inline=False
            )
            
            # Set avatar
            if target_user.avatar:
                welcome_embed.set_thumbnail(url=target_user.avatar.url)
            else:
                welcome_embed.set_thumbnail(url=target_user.default_avatar.url)
            
            # Add server banner if available
            if interaction.guild.banner:
                welcome_embed.set_image(url=interaction.guild.banner.url)
            
            # Footer
            current_time = datetime.utcnow()
            if interaction.guild.icon:
                welcome_embed.set_footer(
                    text=f"Welcome Preview • {current_time.strftime('%B %d, %Y at %I:%M %p')}",
                    icon_url=interaction.guild.icon.url
                )
            else:
                welcome_embed.set_footer(text=f"Welcome Preview • {current_time.strftime('%B %d, %Y at %I:%M %p')}")
            
            welcome_embed.timestamp = current_time
            
            await interaction.response.send_message(embed=welcome_embed)

        # Set Welcome Channel Command (Mod only)
        @self.bot.tree.command(name="setwelcomechannel", description="Set the welcome channel for new members (Mod only)")
        @discord.app_commands.describe(channel="Channel to use for welcome messages")
        async def set_welcome_channel(interaction: discord.Interaction, channel: discord.TextChannel):
            # Check permissions
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message("❌ You need 'Manage Channels' permissions to use this command!", ephemeral=True)
                return
            
            # Check if bot can send messages in the channel
            if not channel.permissions_for(interaction.guild.me).send_messages:
                await interaction.response.send_message(f"❌ I don't have permission to send messages in {channel.mention}!", ephemeral=True)
                return
            
            # Save the setting
            guild_id = str(interaction.guild.id)
            set_guild_settings(guild_id, {'welcome_channel_id': channel.id})
            
            # Confirmation
            success_embed = discord.Embed(
                title="✅ Welcome Channel Set!",
                description=f"Welcome messages will now be sent to {channel.mention}",
                color=COLORS['success']
            )
            await interaction.response.send_message(embed=success_embed)

        # Custom Welcome Message Command (Mod only)
        @self.bot.tree.command(name="customwelcome", description="Customize welcome embed message (Mod only)")
        async def custom_welcome(interaction: discord.Interaction):
            # Check permissions
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("❌ You need 'Manage Server' permissions to use this command!", ephemeral=True)
                return
            
            guild_id = str(interaction.guild.id)
            
            # Create the welcome customizer
            customizer = WelcomeCustomizer(guild_id)
            view = WelcomeCustomizerView(customizer)
            
            await interaction.response.send_message(embed=customizer.create_preview_embed(), view=view, ephemeral=True)

        # Reset Welcome Settings Command (Mod only)  
        @self.bot.tree.command(name="resetwelcome", description="Reset welcome settings to default (Mod only)")
        async def reset_welcome(interaction: discord.Interaction):
            # Check permissions
            if not interaction.user.guild_permissions.manage_guild:
                await interaction.response.send_message("❌ You need 'Manage Server' permissions to use this command!", ephemeral=True)
                return
            
            guild_id = str(interaction.guild.id)
            clear_guild_settings(guild_id)
            
            success_embed = discord.Embed(
                title="✅ Welcome Settings Reset!",
                description="Welcome messages have been reset to default settings",
                color=COLORS['success']
            )
            await interaction.response.send_message(embed=success_embed)


        # Help Command with Interactive Buttons
        @self.bot.tree.command(name="help", description="Get help with bot commands")
        async def help_command(interaction: discord.Interaction):
            view = HelpView(self.bot, interaction.guild.id if interaction.guild else None)
            embed = view.create_main_embed()
            await interaction.response.send_message(embed=embed, view=view)

class HelpView(discord.ui.View):
    def __init__(self, bot, guild_id=None):
        super().__init__(timeout=300)
        self.current_page = "main"
        self.bot = bot
        self.guild_id = guild_id
    
    def create_main_embed(self):
        # Get current prefix for this server
        from bot.database.prefix_manager import prefix_manager
        prefix = "!" if not self.guild_id else prefix_manager.get_prefix(self.guild_id)
        
        embed = discord.Embed(
            title="❓ **Leo Help Center**",
            description=f"*Quick access to all commands • Use `{prefix}command` or `/command`*",
            color=0x5865f2
        )
        
        # Compact command categories
        embed.add_field(
            name="🎵 **Music**",
            value=f"`{prefix}play` • `{prefix}skip` • `{prefix}queue`\n*YouTube music streaming*",
            inline=True
        )
        
        embed.add_field(
            name="💰 **Economy**", 
            value=f"`{prefix}balance` • `{prefix}daily` • `{prefix}work`\n*Earn coins & buy items*",
            inline=True
        )
        
        embed.add_field(
            name="📈 **Levelling**",
            value=f"`{prefix}rank` • `{prefix}leaderboard`\n*XP system with rewards*",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ **Moderation**",
            value=f"`{prefix}ban` • `{prefix}kick` • `{prefix}clear`\n*Server management tools*",
            inline=True
        )
        
        embed.add_field(
            name="🎮 **Games**",
            value=f"`{prefix}coinflip` • `{prefix}slots` • `{prefix}8ball`\n*Fun interactive games*",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ **Settings**",
            value=f"`{prefix}setprefix` • `{prefix}embed`\n*Customize your server*",
            inline=True
        )
        
        # Quick tips at the bottom
        embed.add_field(
            name="💡 **Quick Tips**",
            value=f"🔄 **Both work:** `{prefix}help` = `/help`\n"
                  f"⚙️ **Custom prefix:** Use `/setprefix`\n"
                  f"ℹ️ **Bot info:** Use `/info`",
            inline=False
        )
        
        embed.set_footer(text="💡 Click buttons below for detailed command lists!", icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        return embed
    
    @discord.ui.button(label="🏠 Main", style=discord.ButtonStyle.secondary, row=0)
    async def main_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = "main"
        embed = self.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🎵 Music", style=discord.ButtonStyle.danger, row=0)
    async def music_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎵 Music & Audio Commands 🎶",
            description="🎧 **Transform your server into a music paradise!**\n\n✨ High-quality YouTube audio streaming with advanced queue management",
            color=COLORS['music']
        )
        embed.add_field(
            name="🎤 `/play [song/url]`", 
            value="🎵 Play any song from YouTube\n🔍 Search by name or paste URL\n📁 Automatically adds to queue", 
            inline=False
        )
        embed.add_field(
            name="📋 `/queue`", 
            value="📜 View current song queue\n⏰ See upcoming tracks\n🎯 Check your position", 
            inline=True
        )
        embed.add_field(
            name="⏭️ `/skip`", 
            value="⏩ Skip current song\n🗳️ Democratic voting system\n🚀 Instant for DJs", 
            inline=True
        )
        embed.add_field(
            name="🛑 `/stop`", 
            value="⏹️ Stop music completely\n🧹 Clear entire queue\n👋 Leave voice channel", 
            inline=True
        )
        embed.set_footer(text="🎶 Join a voice channel and start jamming! 🎶")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🛡️ Moderation", style=discord.ButtonStyle.blurple, row=0)
    async def moderation_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛡️ Server Moderation Tools 🔒",
            description="👮 **Keep your server safe and organized!**\n\n⚡ Powerful moderation commands for admins and moderators",
            color=COLORS['moderation']
        )
        embed.add_field(
            name="👢 `/kick [member] [reason]`", 
            value="🚪 Remove troublemakers\n📝 Optional reason logging\n⚠️ Requires permissions", 
            inline=False
        )
        embed.add_field(
            name="🔨 `/ban [member] [reason]`", 
            value="🚫 Permanently ban users\n📋 Reason documentation\n🛡️ Ultimate protection", 
            inline=True
        )
        embed.add_field(
            name="⏰ `/timeout [member] [duration]`", 
            value="🤫 Temporary mute users\n⏱️ Set custom duration\n🔄 Automatic unmute", 
            inline=True
        )
        embed.add_field(
            name="🧹 `/clear [amount]`", 
            value="🗑️ Bulk delete messages\n📊 Up to 100 messages\n💨 Keep chat clean", 
            inline=True
        )
        embed.set_footer(text="🔐 Powerful tools for responsible moderators! 🔐")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🎭 Social & Fun", style=discord.ButtonStyle.success, row=0)
    async def action_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎭 Social & Fun Commands 💫",
            description="🌈 **Express yourself with beautiful animated interactions!**\n\n✨ All commands come with stunning GIFs and custom messages",
            color=COLORS['action']
        )
        embed.add_field(
            name="💝 Affection Commands", 
            value="🤗 `/hug [user]` - Warm embraces\n💋 `/kiss [user]` - Sweet kisses\n🫳 `/pat [user]` - Gentle head pats\n🤗 `/cuddle [user]` - Cozy cuddles", 
            inline=True
        )
        embed.add_field(
            name="🎪 Playful Actions", 
            value="👋 `/slap [user]` - Playful slaps\n👉 `/poke [user]` - Cute pokes\n💃 `/dance [user]` - Dance together\n👋 `/wave [user]` - Friendly waves", 
            inline=True
        )
        embed.add_field(
            name="✨ Features", 
            value="🎨 **Beautiful GIFs** for every action\n💬 **Custom messages** with personality\n🎯 **Mention users** to interact\n🌟 **Express emotions** creatively", 
            inline=False
        )
        embed.set_footer(text="💖 Spread love and joy in your server! 💖")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔧 Utility", style=discord.ButtonStyle.secondary, row=1)
    async def utility_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🔧 Utility & Tools Commands ⚙️",
            description="🛠️ **Essential tools for server management and customization!**\n\n✨ Everything you need to make your server awesome",
            color=COLORS['info']
        )
        embed.add_field(
            name="🤖 Bot Information", 
            value="🤖 `/info` - Complete bot stats & links\n📊 Server count, latency & features\n🔗 Invite & support server links", 
            inline=False
        )
        embed.add_field(
            name="📝 Embed Builder", 
            value="📝 `/embed [channel]` - Create stunning embeds\n🎨 **Interactive builder** with buttons\n✨ **Dynamic placeholders** for personalization\n🌈 Colors, images, fields & more!", 
            inline=True
        )
        embed.add_field(
            name="🎊 Welcome System", 
            value="🎉 `/welcome [user]` - Test welcome messages\n🏠 `/setwelcomechannel` - Set welcome channel\n🎨 `/customwelcome` - Custom embeds\n🔄 `/resetwelcome` - Reset to default", 
            inline=True
        )
        embed.add_field(
            name="✨ Powerful Features", 
            value="🔥 **Real-time placeholders** in embeds\n🎯 **Interactive buttons** for easy editing\n🛡️ **Permission-based** admin commands\n💫 **Beautiful designs** for everything", 
            inline=False
        )
        embed.set_footer(text="⚙️ Power up your server with these amazing tools! ⚙️")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="⭐ Levelling", style=discord.ButtonStyle.primary, row=1)
    async def levelling_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="⭐ Levelling & XP System 📈",
            description="🚀 **Level up by being active in the server!**\n\n💎 Earn XP for chatting and unlock awesome role rewards",
            color=COLORS['success']
        )
        embed.add_field(
            name="📊 XP & Ranking Commands", 
            value="📈 `/rank [user]` - Check level and XP progress\n🏆 `/leaderboard [page]` - Server XP rankings\n⭐ **Automatic XP gain** from chatting", 
            inline=True
        )
        embed.add_field(
            name="🛡️ Server Protection", 
            value="⚠️ **Smart spam detection** warns users\n🔇 **Auto-timeout** after 3 warnings\n🧹 **Message cleanup** for spam", 
            inline=True
        )
        embed.add_field(
            name="🏆 Admin Features", 
            value="🎯 `/addlevelrole` - Set role rewards\n📢 `/setlevelupchannel` - Level announcements\n⚙️ `/levelsettings` - View configuration\n🔧 `/addxp` - Manually add/remove XP", 
            inline=False
        )
        embed.add_field(
            name="✨ System Features", 
            value="🎊 **Beautiful level-up announcements** with custom messages\n🏅 **Automatic role assignment** when reaching levels\n🛡️ **Built-in spam protection** keeps chat clean\n📊 **Detailed progress tracking** and leaderboards", 
            inline=False
        )
        embed.set_footer(text="⭐ Stay active and watch your level grow! ⭐")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="💰 Economy", style=discord.ButtonStyle.primary, row=2)
    async def economy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get current prefix for this server
        from bot.database.prefix_manager import prefix_manager
        prefix = "!" if not self.guild_id else prefix_manager.get_prefix(self.guild_id)
        
        embed = discord.Embed(
            title="💰 **Economy System**",
            description=f"*Build your wealth with coins, jobs & shopping!*",
            color=0xffd700
        )
        
        embed.add_field(
            name="💳 **Core Commands**", 
            value=f"`{prefix}balance` • `{prefix}daily` • `{prefix}work`\n*Check coins, claim rewards, earn money*", 
            inline=True
        )
        embed.add_field(
            name="🎰 **Casino Games**", 
            value=f"`{prefix}bet` • `{prefix}slots` • `{prefix}richest`\n*Gamble, jackpots & leaderboards*", 
            inline=True
        )
        embed.add_field(
            name="🛒 **Shopping**", 
            value=f"`{prefix}shop` • `{prefix}buy` • `{prefix}inventory`\n*Browse items, purchase & manage*", 
            inline=True
        )
        embed.add_field(
            name="✨ **Special Features**", 
            value="📈 **50 coins** per level up\n🔥 **Daily streaks** up to 500 coins\n💼 **6 jobs** with skill progression", 
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="💰 Start earning today!", icon_url=self.bot.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🎮 Games", style=discord.ButtonStyle.success, row=1)
    async def games_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎮 Games & Entertainment 🎪",
            description="🎯 **Fun games to play with friends and break the ice!**\n\n🎊 Perfect for keeping your community engaged and entertained",
            color=COLORS['action']
        )
        embed.add_field(
            name="🎲 Classic Games", 
            value="🪨 `/rps [choice]` - Rock Paper Scissors\n🪙 `/coinflip` - Heads or Tails\n🎲 `/dice [sides]` - Roll custom dice\n🎱 `/8ball [question]` - Magic predictions", 
            inline=True
        )
        embed.add_field(
            name="🎪 Interactive Fun", 
            value="💭 `/truthordare [choice]` - Truth or Dare\n🤔 `/wouldyourather` - Tough choices\n🎯 More games coming soon!\n🎊 Challenge your friends", 
            inline=True
        )
        embed.add_field(
            name="🌟 Game Features", 
            value="⚡ **Instant results** with fun animations\n🎨 **Beautiful embeds** for each game\n👥 **Multiplayer support** for group fun\n🏆 **Random outcomes** keep it exciting", 
            inline=False
        )
        embed.set_footer(text="🎲 Let the games begin! Challenge your friends! 🎲")
        await interaction.response.edit_message(embed=embed, view=self)


class EmbedBuilder:
    def __init__(self, user, target_channel):
        self.user = user
        self.target_channel = target_channel
        self.title = None
        self.description = None
        self.color = COLORS['info']
        self.fields = []
        self.thumbnail = None
        self.image = None
        self.author_name = None
        self.author_icon = None
        self.footer_text = None
        self.footer_icon = None
        self.timestamp = False
    
    def process_placeholders(self, text):
        """Process dynamic placeholders in text"""
        if not text:
            return text
        
        # User placeholders
        text = text.replace("{user_avatar}", self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)
        text = text.replace("{user_name}", self.user.display_name)
        text = text.replace("{user_mention}", self.user.mention)
        text = text.replace("{user_id}", str(self.user.id))
        
        # Server placeholders
        if self.target_channel.guild:
            guild = self.target_channel.guild
            text = text.replace("{server_name}", guild.name)
            text = text.replace("{server_icon}", guild.icon.url if guild.icon else "")
            text = text.replace("{server_member_count}", str(guild.member_count))
            text = text.replace("{server_id}", str(guild.id))
        
        # Channel placeholders
        text = text.replace("{channel_name}", self.target_channel.name)
        text = text.replace("{channel_mention}", self.target_channel.mention)
        text = text.replace("{channel_id}", str(self.target_channel.id))
        
        # Date and time placeholders
        from datetime import datetime
        now = datetime.now()
        text = text.replace("{date}", now.strftime("%B %d, %Y"))
        text = text.replace("{time}", now.strftime("%I:%M %p"))
        text = text.replace("{datetime}", now.strftime("%B %d, %Y at %I:%M %p"))
        
        return text
    
    def create_preview_embed(self):
        embed = discord.Embed(
            title="📝 Embed Builder",
            description="Use the buttons below to customize your embed. Click **Preview** to see how it looks!",
            color=COLORS['utility']
        )
        
        embed.add_field(
            name="🎯 Target Channel", 
            value=self.target_channel.mention,
            inline=True
        )
        
        embed.add_field(
            name="📊 Fields Added", 
            value=str(len(self.fields)),
            inline=True
        )
        
        embed.add_field(
            name="🎨 Color",
            value=f"#{self.color:06x}",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Available Placeholders",
            value="`{user_avatar}` `{user_name}` `{user_mention}` `{server_name}` `{server_icon}` `{date}` `{time}`",
            inline=False
        )
        
        embed.set_footer(text="Interactive Embed Builder • Use placeholders for dynamic content")
        return embed
    
    def create_actual_embed(self):
        embed = discord.Embed(color=self.color)
        
        if self.title:
            embed.title = self.process_placeholders(self.title)
        if self.description:
            embed.description = self.process_placeholders(self.description)
        
        for field in self.fields:
            embed.add_field(
                name=self.process_placeholders(field['name']), 
                value=self.process_placeholders(field['value']), 
                inline=field['inline']
            )
        
        if self.thumbnail:
            embed.set_thumbnail(url=self.process_placeholders(self.thumbnail))
        if self.image:
            embed.set_image(url=self.process_placeholders(self.image))
        if self.author_name:
            embed.set_author(
                name=self.process_placeholders(self.author_name), 
                icon_url=self.process_placeholders(self.author_icon) if self.author_icon else None
            )
        if self.footer_text or self.footer_icon:
            embed.set_footer(
                text=self.process_placeholders(self.footer_text) if self.footer_text else None, 
                icon_url=self.process_placeholders(self.footer_icon) if self.footer_icon else None
            )
        if self.timestamp:
            embed.timestamp = datetime.utcnow()
        
        return embed


class EmbedBuilderView(discord.ui.View):
    def __init__(self, embed_builder, bot):
        super().__init__(timeout=600)  # 10 minutes timeout
        self.embed_builder = embed_builder
        self.bot = bot
    
    @discord.ui.button(label="📝 Title", style=discord.ButtonStyle.secondary, row=0)
    async def set_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TitleModal(self.embed_builder)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📄 Description", style=discord.ButtonStyle.secondary, row=0)
    async def set_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DescriptionModal(self.embed_builder)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🎨 Color", style=discord.ButtonStyle.secondary, row=0)
    async def set_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ColorSelectView(self.embed_builder)
        embed = discord.Embed(
            title="🎨 Choose Embed Color",
            description="Select a color for your embed:",
            color=COLORS['utility']
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="➕ Add Field", style=discord.ButtonStyle.success, row=0)
    async def add_field(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = FieldModal(self.embed_builder)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🖼️ Images", style=discord.ButtonStyle.secondary, row=1)
    async def set_images(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ImageSelectView(self.embed_builder)
        embed = discord.Embed(
            title="🖼️ Image Options",
            description="Choose what type of image to add:",
            color=COLORS['utility']
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="👤 Author", style=discord.ButtonStyle.secondary, row=1)
    async def set_author(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AuthorModal(self.embed_builder)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🦶 Footer", style=discord.ButtonStyle.secondary, row=1)
    async def set_footer(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = FooterModal(self.embed_builder)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⏰ Timestamp", style=discord.ButtonStyle.secondary, row=1)
    async def toggle_timestamp(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed_builder.timestamp = not self.embed_builder.timestamp
        status = "enabled" if self.embed_builder.timestamp else "disabled"
        await interaction.response.send_message(f"✅ Timestamp {status}!", ephemeral=True)
    
    @discord.ui.button(label="❓ Help", style=discord.ButtonStyle.secondary, row=1)
    async def show_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        help_embed = discord.Embed(
            title="🔧 Embed Builder Help",
            description="**Dynamic Placeholders** - Use these in any text field for dynamic content:",
            color=COLORS['utility']
        )
        
        help_embed.add_field(
            name="👤 User Placeholders",
            value="`{user_avatar}` - Your avatar image\n"
                  "`{user_name}` - Your display name\n"
                  "`{user_mention}` - Mention you (@user)\n"
                  "`{user_id}` - Your user ID",
            inline=True
        )
        
        help_embed.add_field(
            name="🏠 Server Placeholders", 
            value="`{server_name}` - Server name\n"
                  "`{server_icon}` - Server icon image\n"
                  "`{server_member_count}` - Total members\n"
                  "`{server_id}` - Server ID",
            inline=True
        )
        
        help_embed.add_field(
            name="📅 Date & Channel",
            value="`{date}` - Current date\n"
                  "`{time}` - Current time\n"
                  "`{channel_name}` - Channel name\n"
                  "`{channel_mention}` - Channel mention",
            inline=True
        )
        
        help_embed.add_field(
            name="💡 Example Usage",
            value="**Title:** `Welcome {user_name}!`\n"
                  "**Description:** `Hey {user_mention}, welcome to {server_name}!`\n"
                  "**Thumbnail:** `{user_avatar}`\n"
                  "**Footer:** `Joined on {date}`",
            inline=False
        )
        
        help_embed.set_footer(text="Placeholders work in all text fields: title, description, fields, author, footer")
        await interaction.response.send_message(embed=help_embed, ephemeral=True)
    
    @discord.ui.button(label="👀 Preview", style=discord.ButtonStyle.primary, row=2)
    async def preview_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            actual_embed = self.embed_builder.create_actual_embed()
            await interaction.response.send_message(embed=actual_embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating preview: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="📤 Send", style=discord.ButtonStyle.success, row=2)
    async def send_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            actual_embed = self.embed_builder.create_actual_embed()
            await self.embed_builder.target_channel.send(embed=actual_embed)
            
            success_embed = discord.Embed(
                title="✅ Embed Sent!",
                description=f"Your embed has been sent to {self.embed_builder.target_channel.mention}",
                color=COLORS['success']
            )
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error sending embed: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="🗑️ Clear", style=discord.ButtonStyle.danger, row=2)
    async def clear_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed_builder = EmbedBuilder(self.embed_builder.user, self.embed_builder.target_channel)
        preview = self.embed_builder.create_preview_embed()
        await interaction.response.edit_message(embed=preview, view=self)


# Modal classes for input forms
class TitleModal(discord.ui.Modal):
    def __init__(self, embed_builder):
        super().__init__(title="Set Embed Title")
        self.embed_builder = embed_builder
        
        self.title_input = discord.ui.TextInput(
            label="Title",
            placeholder="Enter embed title...",
            default=self.embed_builder.title or "",
            max_length=256
        )
        self.add_item(self.title_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        self.embed_builder.title = self.title_input.value if self.title_input.value else None
        await interaction.response.send_message("✅ Title updated!", ephemeral=True)


class DescriptionModal(discord.ui.Modal):
    def __init__(self, embed_builder):
        super().__init__(title="Set Embed Description")
        self.embed_builder = embed_builder
        
        self.description_input = discord.ui.TextInput(
            label="Description",
            placeholder="Enter embed description...",
            default=self.embed_builder.description or "",
            style=discord.TextStyle.paragraph,
            max_length=4000
        )
        self.add_item(self.description_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        self.embed_builder.description = self.description_input.value if self.description_input.value else None
        await interaction.response.send_message("✅ Description updated!", ephemeral=True)


class FieldModal(discord.ui.Modal):
    def __init__(self, embed_builder):
        super().__init__(title="Add Embed Field")
        self.embed_builder = embed_builder
        
        self.name_input = discord.ui.TextInput(
            label="Field Name",
            placeholder="Enter field name...",
            max_length=256
        )
        
        self.value_input = discord.ui.TextInput(
            label="Field Value", 
            placeholder="Enter field value...",
            style=discord.TextStyle.paragraph,
            max_length=1024
        )
        
        self.inline_input = discord.ui.TextInput(
            label="Inline? (yes/no)",
            placeholder="yes or no",
            default="yes",
            max_length=3
        )
        
        self.add_item(self.name_input)
        self.add_item(self.value_input)
        self.add_item(self.inline_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        inline = self.inline_input.value.lower() in ['yes', 'y', 'true', '1']
        
        self.embed_builder.fields.append({
            'name': self.name_input.value,
            'value': self.value_input.value,
            'inline': inline
        })
        
        await interaction.response.send_message(f"✅ Field added! Total fields: {len(self.embed_builder.fields)}", ephemeral=True)


class AuthorModal(discord.ui.Modal):
    def __init__(self, embed_builder):
        super().__init__(title="Set Embed Author")
        self.embed_builder = embed_builder
        
        self.name_input = discord.ui.TextInput(
            label="Author Name",
            placeholder="Enter author name...",
            default=self.embed_builder.author_name or "",
            max_length=256
        )
        
        self.icon_input = discord.ui.TextInput(
            label="Author Icon URL (optional)",
            placeholder="Enter icon URL...",
            default=self.embed_builder.author_icon or "",
            required=False
        )
        
        self.add_item(self.name_input)
        self.add_item(self.icon_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        self.embed_builder.author_name = self.name_input.value if self.name_input.value else None
        self.embed_builder.author_icon = self.icon_input.value if self.icon_input.value else None
        await interaction.response.send_message("✅ Author updated!", ephemeral=True)


class FooterModal(discord.ui.Modal):
    def __init__(self, embed_builder):
        super().__init__(title="Set Embed Footer")
        self.embed_builder = embed_builder
        
        self.text_input = discord.ui.TextInput(
            label="Footer Text",
            placeholder="Enter footer text...",
            default=self.embed_builder.footer_text or "",
            max_length=2048
        )
        
        self.icon_input = discord.ui.TextInput(
            label="Footer Icon URL (optional)",
            placeholder="Enter icon URL...",
            default=self.embed_builder.footer_icon or "",
            required=False
        )
        
        self.add_item(self.text_input)
        self.add_item(self.icon_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        self.embed_builder.footer_text = self.text_input.value if self.text_input.value else None
        self.embed_builder.footer_icon = self.icon_input.value if self.icon_input.value else None
        await interaction.response.send_message("✅ Footer updated!", ephemeral=True)


class ColorSelectView(discord.ui.View):
    def __init__(self, embed_builder):
        super().__init__(timeout=300)
        self.embed_builder = embed_builder
    
    @discord.ui.button(label="🔴 Red", style=discord.ButtonStyle.danger)
    async def red_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed_builder.color = COLORS['error']
        await interaction.response.send_message("✅ Color set to red!", ephemeral=True)
    
    @discord.ui.button(label="🟢 Green", style=discord.ButtonStyle.success)
    async def green_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed_builder.color = COLORS['success']
        await interaction.response.send_message("✅ Color set to green!", ephemeral=True)
    
    @discord.ui.button(label="🔵 Blue", style=discord.ButtonStyle.primary)
    async def blue_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed_builder.color = COLORS['info']
        await interaction.response.send_message("✅ Color set to blue!", ephemeral=True)
    
    @discord.ui.button(label="🟡 Yellow", style=discord.ButtonStyle.secondary)
    async def yellow_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed_builder.color = COLORS['action']
        await interaction.response.send_message("✅ Color set to yellow!", ephemeral=True)
    
    @discord.ui.button(label="🟣 Purple", style=discord.ButtonStyle.secondary)
    async def purple_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.embed_builder.color = COLORS['utility']
        await interaction.response.send_message("✅ Color set to purple!", ephemeral=True)


class ImageSelectView(discord.ui.View):
    def __init__(self, embed_builder):
        super().__init__(timeout=300)
        self.embed_builder = embed_builder
    
    @discord.ui.button(label="🖼️ Main Image", style=discord.ButtonStyle.primary)
    async def set_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ImageModal(self.embed_builder, "image")
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📸 Thumbnail", style=discord.ButtonStyle.secondary)
    async def set_thumbnail(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ImageModal(self.embed_builder, "thumbnail") 
        await interaction.response.send_modal(modal)


class ImageModal(discord.ui.Modal):
    def __init__(self, embed_builder, image_type):
        super().__init__(title=f"Set {image_type.title()}")
        self.embed_builder = embed_builder
        self.image_type = image_type
        
        current_url = getattr(self.embed_builder, image_type, "") or ""
        
        self.url_input = discord.ui.TextInput(
            label=f"{image_type.title()} URL",
            placeholder="Enter image URL...",
            default=current_url
        )
        self.add_item(self.url_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        setattr(self.embed_builder, self.image_type, self.url_input.value if self.url_input.value else None)
        await interaction.response.send_message(f"✅ {self.image_type.title()} updated!", ephemeral=True)


# Welcome Customizer Classes
class WelcomeCustomizer:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.settings = get_guild_settings(guild_id)
        self.custom_embed = self.settings.get('custom_embed', {
            'title': "🎉 Welcome to {server_name}!",
            'description': "Hey {user_mention}! 👋 Welcome to our amazing community!",
            'color': COLORS['success'],
            'fields': [],
            'thumbnail': '{user_avatar}',
            'footer': 'Welcome to {server_name} • {date}',
            'timestamp': True
        })
    
    def create_preview_embed(self):
        embed = discord.Embed(
            title="🎨 Welcome Message Customizer",
            description="Use the buttons below to customize your welcome message. Changes are saved automatically!",
            color=COLORS['utility']
        )
        
        embed.add_field(
            name="📝 Current Title",
            value=f"`{self.custom_embed.get('title', 'Not set')}`",
            inline=False
        )
        
        embed.add_field(
            name="📄 Current Description", 
            value=f"`{self.custom_embed.get('description', 'Not set')[:100]}...`" if len(self.custom_embed.get('description', '')) > 100 else f"`{self.custom_embed.get('description', 'Not set')}`",
            inline=False
        )
        
        embed.add_field(
            name="🎨 Current Color",
            value=f"#{self.custom_embed.get('color', COLORS['success']):06x}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Custom Fields",
            value=str(len(self.custom_embed.get('fields', []))),
            inline=True
        )
        
        embed.add_field(
            name="🔧 Available Placeholders",
            value="`{user_name}` `{user_mention}` `{user_avatar}` `{server_name}` `{server_member_count}` `{date}` `{time}`",
            inline=False
        )
        
        embed.set_footer(text="Welcome Customizer • Changes save automatically")
        return embed
    
    def save_settings(self):
        set_guild_settings(self.guild_id, {'custom_embed': self.custom_embed})


class WelcomeCustomizerView(discord.ui.View):
    def __init__(self, customizer):
        super().__init__(timeout=600)
        self.customizer = customizer
    
    @discord.ui.button(label="📝 Edit Title", style=discord.ButtonStyle.secondary, row=0)
    async def edit_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = WelcomeTextModal(self.customizer, "title", "Welcome Title")
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📄 Edit Description", style=discord.ButtonStyle.secondary, row=0)
    async def edit_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = WelcomeTextModal(self.customizer, "description", "Welcome Description", style=discord.TextStyle.paragraph)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🎨 Change Color", style=discord.ButtonStyle.secondary, row=0)
    async def change_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = WelcomeColorView(self.customizer)
        embed = discord.Embed(title="🎨 Choose Welcome Color", color=COLORS['utility'])
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="➕ Add Field", style=discord.ButtonStyle.success, row=0)
    async def add_field(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = WelcomeFieldModal(self.customizer)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🖼️ Set Images", style=discord.ButtonStyle.secondary, row=1)
    async def set_images(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = WelcomeImageModal(self.customizer)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🦶 Edit Footer", style=discord.ButtonStyle.secondary, row=1)
    async def edit_footer(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = WelcomeTextModal(self.customizer, "footer", "Welcome Footer")
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Clear Fields", style=discord.ButtonStyle.danger, row=1)
    async def clear_fields(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.customizer.custom_embed['fields'] = []
        self.customizer.save_settings()
        await interaction.response.send_message("✅ All custom fields cleared!", ephemeral=True)
    
    @discord.ui.button(label="👀 Preview", style=discord.ButtonStyle.primary, row=2)
    async def preview(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Create a preview embed using the custom settings
        preview_embed = discord.Embed(
            title=self.customizer.custom_embed.get('title', 'Welcome!').replace('{server_name}', interaction.guild.name).replace('{user_name}', interaction.user.display_name).replace('{user_mention}', interaction.user.mention),
            description=self.customizer.custom_embed.get('description', 'Welcome!').replace('{server_name}', interaction.guild.name).replace('{user_name}', interaction.user.display_name).replace('{user_mention}', interaction.user.mention),
            color=self.customizer.custom_embed.get('color', COLORS['success'])
        )
        
        for field in self.customizer.custom_embed.get('fields', []):
            preview_embed.add_field(
                name=field['name'].replace('{server_name}', interaction.guild.name),
                value=field['value'].replace('{server_name}', interaction.guild.name).replace('{user_name}', interaction.user.display_name).replace('{user_mention}', interaction.user.mention),
                inline=field.get('inline', True)
            )
        
        if self.customizer.custom_embed.get('thumbnail'):
            if '{user_avatar}' in self.customizer.custom_embed['thumbnail']:
                preview_embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            else:
                preview_embed.set_thumbnail(url=self.customizer.custom_embed['thumbnail'])
        
        if self.customizer.custom_embed.get('footer'):
            preview_embed.set_footer(text=self.customizer.custom_embed['footer'].replace('{server_name}', interaction.guild.name).replace('{date}', datetime.now().strftime("%B %d, %Y")))
        
        if self.customizer.custom_embed.get('timestamp', True):
            preview_embed.timestamp = datetime.utcnow()
        
        await interaction.response.send_message(embed=preview_embed, ephemeral=True)


class WelcomeTextModal(discord.ui.Modal):
    def __init__(self, customizer, field_key, title, style=discord.TextStyle.short):
        super().__init__(title=f"Edit {title}")
        self.customizer = customizer
        self.field_key = field_key
        
        self.text_input = discord.ui.TextInput(
            label=title,
            placeholder=f"Enter {title.lower()}... (use placeholders like {{user_name}})",
            default=self.customizer.custom_embed.get(field_key, ""),
            style=style,
            max_length=4000 if style == discord.TextStyle.paragraph else 256
        )
        self.add_item(self.text_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        self.customizer.custom_embed[self.field_key] = self.text_input.value
        self.customizer.save_settings()
        await interaction.response.send_message(f"✅ {self.field_key.title()} updated!", ephemeral=True)


class WelcomeFieldModal(discord.ui.Modal):
    def __init__(self, customizer):
        super().__init__(title="Add Welcome Field")
        self.customizer = customizer
        
        self.name_input = discord.ui.TextInput(
            label="Field Name",
            placeholder="Enter field name...",
            max_length=256
        )
        
        self.value_input = discord.ui.TextInput(
            label="Field Value",
            placeholder="Enter field value... (use placeholders like {user_name})",
            style=discord.TextStyle.paragraph,
            max_length=1024
        )
        
        self.inline_input = discord.ui.TextInput(
            label="Inline? (yes/no)",
            placeholder="yes or no",
            default="yes",
            max_length=3
        )
        
        self.add_item(self.name_input)
        self.add_item(self.value_input)
        self.add_item(self.inline_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        inline = self.inline_input.value.lower() in ['yes', 'y', 'true', '1']
        
        if 'fields' not in self.customizer.custom_embed:
            self.customizer.custom_embed['fields'] = []
        
        self.customizer.custom_embed['fields'].append({
            'name': self.name_input.value,
            'value': self.value_input.value,
            'inline': inline
        })
        
        self.customizer.save_settings()
        await interaction.response.send_message(f"✅ Field added! Total: {len(self.customizer.custom_embed['fields'])}", ephemeral=True)


class WelcomeImageModal(discord.ui.Modal):
    def __init__(self, customizer):
        super().__init__(title="Set Welcome Images")
        self.customizer = customizer
        
        self.thumbnail_input = discord.ui.TextInput(
            label="Thumbnail URL",
            placeholder="Enter thumbnail URL or use {user_avatar}",
            default=self.customizer.custom_embed.get('thumbnail', ''),
            required=False
        )
        
        self.image_input = discord.ui.TextInput(
            label="Main Image URL (Optional)",
            placeholder="Enter main image URL...",
            default=self.customizer.custom_embed.get('image', ''),
            required=False
        )
        
        self.add_item(self.thumbnail_input)
        self.add_item(self.image_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.thumbnail_input.value:
            self.customizer.custom_embed['thumbnail'] = self.thumbnail_input.value
        
        if self.image_input.value:
            self.customizer.custom_embed['image'] = self.image_input.value
        
        self.customizer.save_settings()
        await interaction.response.send_message("✅ Images updated!", ephemeral=True)


class WelcomeColorView(discord.ui.View):
    def __init__(self, customizer):
        super().__init__(timeout=300)
        self.customizer = customizer
    
    @discord.ui.button(label="🔴 Red", style=discord.ButtonStyle.danger)
    async def red_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.customizer.custom_embed['color'] = COLORS['error']
        self.customizer.save_settings()
        await interaction.response.send_message("✅ Color set to red!", ephemeral=True)
    
    @discord.ui.button(label="🟢 Green", style=discord.ButtonStyle.success)
    async def green_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.customizer.custom_embed['color'] = COLORS['success']
        self.customizer.save_settings()
        await interaction.response.send_message("✅ Color set to green!", ephemeral=True)
    
    @discord.ui.button(label="🔵 Blue", style=discord.ButtonStyle.primary)
    async def blue_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.customizer.custom_embed['color'] = COLORS['info']
        self.customizer.save_settings()
        await interaction.response.send_message("✅ Color set to blue!", ephemeral=True)
    
    @discord.ui.button(label="🟡 Yellow", style=discord.ButtonStyle.secondary)
    async def yellow_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.customizer.custom_embed['color'] = COLORS['action']
        self.customizer.save_settings()
        await interaction.response.send_message("✅ Color set to yellow!", ephemeral=True)
    
    @discord.ui.button(label="🟣 Purple", style=discord.ButtonStyle.secondary)
    async def purple_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.customizer.custom_embed['color'] = COLORS['utility']
        self.customizer.save_settings()
        await interaction.response.send_message("✅ Color set to purple!", ephemeral=True)