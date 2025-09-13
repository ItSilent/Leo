import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import math
from bot.database.levelling import levelling_system
from config.settings import COLORS

class LevellingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="rank", description="Check your or someone else's level and XP")
    async def rank(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        target = member or interaction.user
        
        if target.bot:
            embed = discord.Embed(
                title="❌ Error",
                description="Bots don't have levels!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get user data
        user_data = levelling_system.get_user_data(interaction.guild.id, target.id)
        rank = levelling_system.get_user_rank(interaction.guild.id, target.id)
        
        # Calculate progress to next level
        current_level = user_data["level"]
        current_xp = user_data["xp"]
        xp_for_current = levelling_system.calculate_xp_for_level(current_level)
        xp_for_next = levelling_system.calculate_xp_for_level(current_level + 1)
        xp_progress = current_xp - xp_for_current
        xp_needed = xp_for_next - xp_for_current
        
        # Create progress bar
        progress_percentage = (xp_progress / xp_needed) * 100
        bar_length = 20
        filled_length = int(bar_length * progress_percentage / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        # Create embed
        embed = discord.Embed(
            title=f"📊 {target.display_name}'s Level Stats",
            color=COLORS['info']
        )
        
        embed.add_field(
            name="🏆 Current Level",
            value=f"**Level {current_level}**",
            inline=True
        )
        
        embed.add_field(
            name="🥇 Server Rank",
            value=f"**#{rank}**" if rank else "Not ranked",
            inline=True
        )
        
        embed.add_field(
            name="💎 Total XP",
            value=f"**{current_xp:,}** XP",
            inline=True
        )
        
        embed.add_field(
            name="📈 Progress to Next Level",
            value=f"`{bar}` {progress_percentage:.1f}%\n**{xp_progress:,}** / **{xp_needed:,}** XP\n*({xp_for_next - current_xp:,} XP to go)*",
            inline=False
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"💬 **Messages:** {user_data['total_messages']:,}\n⚡ **Avg XP/Message:** {current_xp / max(user_data['total_messages'], 1):.1f}",
            inline=True
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="🌟 Keep chatting to earn more XP! 🌟")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="Show the server's XP leaderboard")
    async def leaderboard(self, interaction: discord.Interaction, page: Optional[int] = 1):
        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        page = max(1, page or 1)  # Ensure page is at least 1
        per_page = 10
        start_index = (page - 1) * per_page
        
        # Get leaderboard data
        all_users = levelling_system.get_leaderboard(interaction.guild.id, limit=None)
        total_pages = math.ceil(len(all_users) / per_page) if all_users else 1
        page = min(page, total_pages)  # Ensure page doesn't exceed maximum
        
        page_users = all_users[start_index:start_index + per_page]
        
        if not page_users:
            embed = discord.Embed(
                title="📊 Server Leaderboard",
                description="No users found! Start chatting to appear on the leaderboard!",
                color=COLORS['info']
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Create embed
        embed = discord.Embed(
            title="🏆 Server XP Leaderboard",
            description=f"Top active members in **{interaction.guild.name}**",
            color=COLORS['success']
        )
        
        leaderboard_text = ""
        for i, (user_id, user_data) in enumerate(page_users, start=start_index + 1):
            user = self.bot.get_user(user_id)
            if not user:
                continue
            
            # Determine rank emoji
            if i == 1:
                rank_emoji = "🥇"
            elif i == 2:
                rank_emoji = "🥈"
            elif i == 3:
                rank_emoji = "🥉"
            else:
                rank_emoji = f"**{i}.**"
            
            level = user_data["level"]
            xp = user_data["xp"]
            messages = user_data["total_messages"]
            
            leaderboard_text += f"{rank_emoji} {user.display_name}\n"
            leaderboard_text += f"└ Level **{level}** • **{xp:,}** XP • **{messages:,}** messages\n\n"
        
        embed.description += f"\n\n{leaderboard_text}"
        
        if total_pages > 1:
            embed.set_footer(text=f"📄 Page {page}/{total_pages} • Use /leaderboard [page] to navigate")
        else:
            embed.set_footer(text="🌟 Keep chatting to climb the ranks! 🌟")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="addxp", description="Add XP to a user (Admin only)")
    @app_commands.describe(
        member="The member to give XP to",
        amount="Amount of XP to add (can be negative to remove)"
    )
    async def add_xp(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Check permissions
        if not hasattr(interaction.user, 'guild_permissions') or not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need Administrator permissions to use this command!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.bot:
            embed = discord.Embed(
                title="❌ Error",
                description="You can't give XP to bots!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get current data
        old_data = levelling_system.get_user_data(interaction.guild.id, member.id)
        old_level = old_data["level"]
        old_xp = old_data["xp"]
        
        # Add XP (force add without cooldown)
        level_up, new_xp, _, new_level = levelling_system.add_xp(
            interaction.guild.id, member.id, amount
        )
        
        # Create response
        action = "Added" if amount > 0 else "Removed"
        embed = discord.Embed(
            title=f"✅ XP {action}",
            description=f"{action} **{abs(amount):,}** XP {'to' if amount > 0 else 'from'} {member.mention}",
            color=COLORS['success']
        )
        
        embed.add_field(
            name="📊 Before → After",
            value=f"**Level:** {old_level} → {new_level}\n**XP:** {old_xp:,} → {new_xp:,}",
            inline=False
        )
        
        if level_up:
            embed.add_field(
                name="🎉 Level Up!",
                value=f"{member.display_name} leveled up to **Level {new_level}**!",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="resetwarnings", description="Reset a user's spam warnings (Moderator only)")
    @app_commands.describe(member="The member to reset warnings for")
    async def reset_warnings(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Check permissions
        if not hasattr(interaction.user, 'guild_permissions') or not (interaction.user.guild_permissions.kick_members or interaction.user.guild_permissions.administrator):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need Kick Members or Administrator permissions to use this command!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        warning_count = levelling_system.get_user_warnings(interaction.guild.id, member.id)
        levelling_system.reset_warnings(interaction.guild.id, member.id)
        
        embed = discord.Embed(
            title="✅ Warnings Reset",
            description=f"Reset **{warning_count}** warnings for {member.mention}",
            color=COLORS['success']
        )
        embed.set_footer(text="The user can now send messages normally.")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LevellingCommands(bot))