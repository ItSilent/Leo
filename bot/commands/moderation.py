"""
Moderation Commands Module
"""
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from config.settings import COLORS

class ModerationCommands:
    def __init__(self, bot):
        self.bot = bot

    async def setup_commands(self):
        @self.bot.tree.command(name="kick", description="Kick a member from the server")
        @discord.app_commands.describe(member="The member to kick", reason="Reason for kicking")
        async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
            try:
                await member.kick(reason=reason)
                
                embed = discord.Embed(
                    title="👢 Member Kicked",
                    description=f"**{member.mention}** has been kicked.\nReason: {reason}",
                    color=COLORS['moderation']
                )
                
                await interaction.response.send_message(embed=embed)
                
            except discord.Forbidden:
                await interaction.response.send_message("❌ I don't have permission to kick this member!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)

        @self.bot.tree.command(name="ban", description="Ban a member from the server")
        @discord.app_commands.describe(member="The member to ban", reason="Reason for banning")
        async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
            try:
                await member.ban(reason=reason, delete_message_days=1)
                
                embed = discord.Embed(
                    title="🔨 Member Banned",
                    description=f"**{member.mention}** has been banned.\nReason: {reason}",
                    color=COLORS['error']
                )
                
                await interaction.response.send_message(embed=embed)
                
            except discord.Forbidden:
                await interaction.response.send_message("❌ I don't have permission to ban this member!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)

        @self.bot.tree.command(name="timeout", description="Timeout a member")
        @discord.app_commands.describe(
            member="The member to timeout",
            duration="Duration (e.g., 1h, 30m, 1d)",
            reason="Reason for timeout"
        )
        async def timeout(interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
            try:
                duration_mapping = {
                    's': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days'
                }
                
                unit = duration[-1].lower()
                if unit not in duration_mapping:
                    await interaction.response.send_message("❌ Invalid duration format! Use: 1s, 30m, 1h, 1d", ephemeral=True)
                    return
                
                try:
                    amount = int(duration[:-1])
                except ValueError:
                    await interaction.response.send_message("❌ Invalid duration format! Use: 1s, 30m, 1h, 1d", ephemeral=True)
                    return
                
                kwargs = {duration_mapping[unit]: amount}
                timeout_duration = timedelta(**kwargs)
                
                if timeout_duration.total_seconds() > 2419200:  # 28 days max
                    await interaction.response.send_message("❌ Timeout duration cannot exceed 28 days!", ephemeral=True)
                    return
                
                await member.timeout(timeout_duration, reason=reason)
                
                embed = discord.Embed(
                    title="⏰ Member Timed Out",
                    description=f"**{member.mention}** has been timed out.",
                    color=COLORS['moderation'],
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Duration", value=duration, inline=True)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
                embed.set_footer(text="Moderation Action")
                
                await interaction.response.send_message(embed=embed)
                
            except discord.Forbidden:
                await interaction.response.send_message("❌ I don't have permission to timeout this member!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)

        @self.bot.tree.command(name="clear", description="Delete a specified number of messages")
        @discord.app_commands.describe(amount="Number of messages to delete (1-100)")
        async def clear(interaction: discord.Interaction, amount: int):
            if amount < 1 or amount > 100:
                await interaction.response.send_message("❌ Please specify a number between 1 and 100!", ephemeral=True)
                return
            
            try:
                deleted = await interaction.channel.purge(limit=amount)
                
                embed = discord.Embed(
                    title="🧹 Messages Cleared",
                    description=f"Successfully deleted **{len(deleted)}** messages.",
                    color=COLORS['success'],
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"Cleared by {interaction.user.display_name}")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            except discord.Forbidden:
                await interaction.response.send_message("❌ I don't have permission to delete messages!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)