import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from bot.database.economy import economy_system
from config.settings import COLORS

class EconomyAdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="addcoins", description="Add coins to a user (Admin only)")
    @app_commands.describe(
        member="The member to give coins to",
        amount="Amount of coins to add (can be negative to remove)"
    )
    async def add_coins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
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
                description="You can't give coins to bots!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get current balance
        old_data = economy_system.get_user_data(interaction.guild.id, member.id)
        old_balance = old_data["balance"]
        
        # Add coins
        if amount > 0:
            new_balance = economy_system.add_coins(interaction.guild.id, member.id, amount, "Admin grant")
        else:
            success = economy_system.remove_coins(interaction.guild.id, member.id, abs(amount), "Admin removal")
            if not success:
                embed = discord.Embed(
                    title="❌ Insufficient Funds",
                    description=f"{member.display_name} doesn't have enough coins to remove {abs(amount):,}!",
                    color=COLORS['error']
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            new_data = economy_system.get_user_data(interaction.guild.id, member.id)
            new_balance = new_data["balance"]
        
        # Create response
        action = "Added" if amount > 0 else "Removed"
        embed = discord.Embed(
            title=f"✅ Coins {action}",
            description=f"{action} **{abs(amount):,}** coins {'to' if amount > 0 else 'from'} {member.mention}",
            color=COLORS['success']
        )
        
        embed.add_field(
            name="💰 Balance Change",
            value=f"**{old_balance:,}** → **{new_balance:,}** coins",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="reseteconomy", description="Reset a user's economy data (Admin only)")
    @app_commands.describe(member="The member to reset")
    async def reset_economy(self, interaction: discord.Interaction, member: discord.Member):
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
                description="Bots don't have economy data!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Reset to default
        economy_system.update_user_data(
            interaction.guild.id, 
            member.id,
            balance=economy_system.starting_balance,
            bank=0,
            total_earned=economy_system.starting_balance,
            total_spent=0,
            daily_streak=0,
            last_daily=0,
            last_work=0,
            inventory={},
            job=None,
            job_experience={},
            achievements=[]
        )
        
        embed = discord.Embed(
            title="✅ Economy Reset",
            description=f"Reset {member.mention}'s economy data to default values",
            color=COLORS['success']
        )
        embed.add_field(
            name="💰 New Balance",
            value=f"{economy_system.starting_balance:,} coins",
            inline=True
        )
        embed.set_footer(text="All progress, items, and statistics have been reset.")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="economystats", description="View server economy statistics (Admin only)")
    async def economy_stats(self, interaction: discord.Interaction):
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
        
        # Get all users for this guild
        data = economy_system._load_data(economy_system.economy_file)
        guild_str = str(interaction.guild.id)
        
        if guild_str not in data or not data[guild_str]:
            embed = discord.Embed(
                title="📊 Economy Statistics",
                description="No economy data found for this server!",
                color=COLORS['info']
            )
            await interaction.response.send_message(embed=embed)
            return
        
        users_data = data[guild_str]
        
        # Calculate statistics
        total_users = len(users_data)
        total_coins = sum(user['balance'] + user['bank'] for user in users_data.values())
        total_earned = sum(user['total_earned'] for user in users_data.values())
        total_spent = sum(user['total_spent'] for user in users_data.values())
        avg_balance = total_coins / total_users if total_users > 0 else 0
        
        # Find richest user
        richest_id = max(users_data.keys(), key=lambda k: users_data[k]['balance'] + users_data[k]['bank'])
        richest_user = self.bot.get_user(int(richest_id))
        richest_amount = users_data[richest_id]['balance'] + users_data[richest_id]['bank']
        
        # Daily streak champion
        streak_champion_id = max(users_data.keys(), key=lambda k: users_data[k]['daily_streak'])
        streak_champion = self.bot.get_user(int(streak_champion_id))
        streak_amount = users_data[streak_champion_id]['daily_streak']
        
        embed = discord.Embed(
            title="📊 Server Economy Statistics",
            description=f"Economy overview for **{interaction.guild.name}**",
            color=COLORS['info']
        )
        
        embed.add_field(
            name="👥 User Statistics",
            value=f"**{total_users:,}** active users\n**{avg_balance:.0f}** average balance",
            inline=True
        )
        
        embed.add_field(
            name="💰 Coin Statistics", 
            value=f"**{total_coins:,}** total coins\n**{total_earned:,}** total earned\n**{total_spent:,}** total spent",
            inline=True
        )
        
        embed.add_field(
            name="🏆 Champions",
            value=f"**Richest:** {richest_user.display_name if richest_user else 'Unknown'}\n└ {richest_amount:,} coins\n**Streak King:** {streak_champion.display_name if streak_champion else 'Unknown'}\n└ {streak_amount} days",
            inline=False
        )
        
        embed.set_footer(text="💡 Use /richest to see public leaderboards!")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyAdminCommands(bot))