import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from bot.database.levelling import levelling_system
from config.settings import COLORS

class LevellingHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.processing_levelups = set()  # Prevent duplicate level up messages
        
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bots and system messages
        if message.author.bot or not message.guild:
            return
            
        print(f"Message received from {message.author.name}: {message.content[:50]}...")  # Debug log
        
        # Check if XP is enabled for this server
        settings = levelling_system.get_server_settings(message.guild.id)
        if not settings.get("xp_enabled", True):
            print("XP system disabled for this server")
            return
        
        # Check for spam first
        if settings.get("spam_protection", True):
            await self._handle_spam_detection(message)
        
        # Add XP to user
        await self._handle_xp_gain(message)
    
    async def _handle_spam_detection(self, message):
        """Handle spam detection and warnings"""
        is_spam = levelling_system.check_spam(message.guild.id, message.author.id)
        
        if is_spam:
            print(f"Spam detected from {message.author.name}")  # Debug log
            
            # Add warning
            warning_count, should_timeout = levelling_system.add_warning(
                message.guild.id, message.author.id
            )
            
            # Create warning embed
            embed = discord.Embed(
                title="⚠️ Spam Warning",
                description=f"{message.author.mention}, please slow down your messages!",
                color=COLORS['warning']
            )
            embed.add_field(
                name="Warning Details",
                value=f"🚨 **Warning {warning_count}/3**\n⏰ Sending messages too quickly\n🛡️ Please wait before sending more messages",
                inline=False
            )
            
            if should_timeout:
                embed.add_field(
                    name="⏰ Timeout Applied",
                    value="You have been temporarily muted for 10 minutes due to repeated spam warnings.",
                    inline=False
                )
                embed.color = COLORS['error']
                
                # Apply timeout
                try:
                    timeout_until = discord.utils.utcnow() + timedelta(minutes=10)
                    await message.author.timeout(timeout_until, reason="Spam detection - 3 warnings")
                except discord.Forbidden:
                    embed.add_field(
                        name="❌ Timeout Failed",
                        value="I don't have permission to timeout this user.",
                        inline=False
                    )
            else:
                embed.set_footer(text="💡 Tip: Wait a few seconds between messages to avoid warnings!")
            
            # Send warning message
            try:
                await message.channel.send(embed=embed, delete_after=10)
            except discord.Forbidden:
                pass
            
            # Delete spam message if possible
            try:
                await message.delete()
            except discord.Forbidden:
                pass
    
    async def _handle_xp_gain(self, message):
        """Handle XP gain and level ups"""
        # Check if message is long enough (prevent spam XP)
        if len(message.content.strip()) < 3:
            return
        
        # Add XP
        level_up, new_xp, old_level, new_level = levelling_system.add_xp(
            message.guild.id, message.author.id
        )
        
        if level_up:
            print(f"Level up triggered for {message.author.name}: {old_level} -> {new_level}")  # Debug log
            await self._handle_level_up(message, old_level, new_level, new_xp)
        else:
            print(f"XP added for {message.author.name}: {new_xp} XP (Level {new_level})")  # Debug log
    
    async def _handle_level_up(self, message, old_level, new_level, xp):
        """Handle level up event"""
        user_key = f"{message.guild.id}:{message.author.id}:{new_level}"
        if user_key in self.processing_levelups:
            return
        
        self.processing_levelups.add(user_key)
        
        try:
            settings = levelling_system.get_server_settings(message.guild.id)
            
            print(f"Level up detected: {message.author.name} reached level {new_level}")  # Debug log
            
            # Create level up embed
            embed = discord.Embed(
                title="🎉 Level Up! 🎉",
                description=settings.get("levelup_message", "🎉 {user_mention} leveled up to **Level {level}**! 🚀").format(
                    user_mention=message.author.mention,
                    user_name=message.author.display_name,
                    level=new_level
                ),
                color=COLORS['success']
            )
            
            embed.add_field(
                name="📊 Stats",
                value=f"🆙 **Level:** {old_level} → {new_level}\n💎 **Total XP:** {xp:,}\n🎯 **Next Level:** {levelling_system.calculate_xp_for_level(new_level + 1):,} XP",
                inline=True
            )
            
            # Calculate rank
            rank = levelling_system.get_user_rank(message.guild.id, message.author.id)
            embed.add_field(
                name="🏆 Server Rank",
                value=f"#{rank}" if rank else "Not ranked",
                inline=True
            )
            
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.set_footer(text="🌟 Keep chatting to earn more XP! 🌟")
            
            # Get level up channel
            levelup_channel_id = settings.get("levelup_channel")
            if levelup_channel_id:
                levelup_channel = self.bot.get_channel(levelup_channel_id)
                if levelup_channel:
                    await levelup_channel.send(embed=embed)
                else:
                    # Fallback to current channel
                    await message.channel.send(embed=embed)
            else:
                # Send in current channel
                await message.channel.send(embed=embed)
            
            # Handle role rewards
            await self._handle_role_rewards(message.author, message.guild, new_level)
            
            # Economy integration - give coins for leveling up!
            try:
                from bot.database.economy import economy_system
                bonus_coins = new_level * 50  # 50 coins per level reached
                economy_system.add_coins(message.guild.id, message.author.id, bonus_coins, f"Level up to {new_level}")
                
                # Add to level up embed
                embed.add_field(
                    name="💰 Level Up Bonus",
                    value=f"+{bonus_coins} coins!",
                    inline=True
                )
            except Exception as e:
                print(f"Error adding level up coins: {e}")
            
        finally:
            # Remove from processing set after a delay
            await asyncio.sleep(1)
            self.processing_levelups.discard(user_key)
    
    async def _handle_role_rewards(self, member, guild, new_level):
        """Handle automatic role assignment for level ups"""
        settings = levelling_system.get_server_settings(guild.id)
        level_roles = settings.get("level_roles", {})
        
        if not level_roles:
            return
        
        try:
            # Find roles to add for current level
            roles_to_add = []
            roles_to_remove = []
            
            for level_str, role_id in level_roles.items():
                level_req = int(level_str)
                role = guild.get_role(role_id)
                
                if not role:
                    continue
                
                if new_level >= level_req:
                    # User qualifies for this role
                    if role not in member.roles:
                        roles_to_add.append(role)
                else:
                    # User no longer qualifies (shouldn't happen but just in case)
                    if role in member.roles:
                        roles_to_remove.append(role)
            
            # Add new roles
            if roles_to_add:
                await member.add_roles(*roles_to_add, reason=f"Level up to {new_level}")
            
            # Remove old roles (if any)
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason=f"Level change to {new_level}")
                
        except discord.Forbidden:
            # Bot doesn't have permission to manage roles
            pass
        except Exception as e:
            print(f"Error handling role rewards: {e}")

async def setup(bot):
    await bot.add_cog(LevellingHandler(bot))