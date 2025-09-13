import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import math
import random
from datetime import datetime, timedelta
from bot.database.economy import economy_system
from bot.utils.hybrid_helpers import hybrid_send
from config.settings import COLORS

class EconomyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="balance", description="Check your or someone else's coin balance")
    @app_commands.describe(member="The member to check balance for")
    async def balance(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        if not ctx.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
            
        target = member or ctx.author
        
        if target.bot:
            embed = discord.Embed(
                title="❌ Error",
                description="Bots don't have economies!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        user_data = economy_system.get_user_data(ctx.guild.id, target.id)
        
        embed = discord.Embed(
            title=f"💰 {target.display_name}'s Wallet",
            color=COLORS['success']
        )
        
        embed.add_field(
            name="💵 Cash",
            value=f"**{user_data['balance']:,}** coins",
            inline=True
        )
        
        embed.add_field(
            name="🏦 Bank",
            value=f"**{user_data['bank']:,}** coins",
            inline=True
        )
        
        total_worth = user_data['balance'] + user_data['bank']
        embed.add_field(
            name="💎 Net Worth",
            value=f"**{total_worth:,}** coins",
            inline=True
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"💰 **Total Earned:** {user_data['total_earned']:,}\n💸 **Total Spent:** {user_data['total_spent']:,}\n🔥 **Daily Streak:** {user_data['daily_streak']} days",
            inline=False
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="💡 Use daily command to claim your daily reward!")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="daily", description="Claim your daily coin reward")
    async def daily(self, ctx: commands.Context):
        if not ctx.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        success, amount, streak, streak_broken = economy_system.claim_daily(ctx.guild.id, ctx.author.id)
        
        if not success:
            # Calculate time until next daily
            user_data = economy_system.get_user_data(ctx.guild.id, ctx.author.id)
            next_daily = user_data['last_daily'] + 86400
            wait_time = next_daily - datetime.now().timestamp()
            hours = int(wait_time // 3600)
            minutes = int((wait_time % 3600) // 60)
            
            embed = discord.Embed(
                title="⏰ Already Claimed",
                description=f"You've already claimed your daily reward today!\n\nCome back in **{hours}h {minutes}m** for your next reward.",
                color=COLORS['error']
            )
            embed.set_footer(text="💡 Don't break your streak!")
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"You received **{amount:,}** coins!",
            color=COLORS['success']
        )
        
        if streak_broken:
            embed.add_field(
                name="💔 Streak Broken",
                value="You missed a day and your streak was reset!",
                inline=False
            )
        else:
            embed.add_field(
                name="🔥 Daily Streak",
                value=f"**{streak}** days in a row!",
                inline=True
            )
            
            if streak >= 7:
                embed.add_field(
                    name="🎉 Streak Bonus",
                    value="You're on fire! Keep it up!",
                    inline=True
                )
        
        user_data = economy_system.get_user_data(ctx.guild.id, ctx.author.id)
        embed.add_field(
            name="💰 New Balance",
            value=f"{user_data['balance']:,} coins",
            inline=True
        )
        
        embed.set_footer(text="💡 Come back tomorrow to continue your streak!")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="work", description="Work a job to earn coins")
    @app_commands.describe(job="Choose a specific job to work")
    @app_commands.choices(job=[
        app_commands.Choice(name="💻 Programmer", value="programmer"),
        app_commands.Choice(name="🎨 Designer", value="designer"),
        app_commands.Choice(name="📺 Streamer", value="streamer"),
        app_commands.Choice(name="👨‍🍳 Chef", value="chef"),
        app_commands.Choice(name="🎮 Pro Gamer", value="gamer"),
        app_commands.Choice(name="📚 Teacher", value="teacher")
    ])
    async def work(self, ctx: commands.Context, job: Optional[str] = None):
        if not ctx.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        success, earnings, message, leveled_up = economy_system.work_job(ctx.guild.id, ctx.author.id, job)
        
        if not success:
            user_data = economy_system.get_user_data(ctx.guild.id, ctx.author.id)
            if datetime.now().timestamp() - user_data['last_work'] < 3600:
                wait_time = 3600 - (datetime.now().timestamp() - user_data['last_work'])
                minutes = int(wait_time // 60)
                embed = discord.Embed(
                    title="😴 Still Tired",
                    description=f"You need to rest for **{minutes}** more minutes before working again!",
                    color=COLORS['error']
                )
            else:
                embed = discord.Embed(
                    title="💼 Work Failed",
                    description=message,
                    color=COLORS['error']
                )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        user_data = economy_system.get_user_data(ctx.guild.id, ctx.author.id)
        job_name = economy_system.jobs.get(user_data['job'], {}).get('name', 'Unknown')
        
        embed = discord.Embed(
            title="💼 Work Complete!",
            description=message,
            color=COLORS['success']
        )
        
        if earnings > 0:
            embed.add_field(
                name="💰 Earnings",
                value=f"**+{earnings:,}** coins",
                inline=True
            )
            
            embed.add_field(
                name="💵 New Balance",
                value=f"{user_data['balance']:,} coins",
                inline=True
            )
            
            # Job experience
            if user_data['job'] in user_data['job_experience']:
                exp = user_data['job_experience'][user_data['job']]
                embed.add_field(
                    name="📈 Experience",
                    value=f"Level {exp // 10} ({exp % 10}/10)",
                    inline=True
                )
                
                if leveled_up:
                    embed.add_field(
                        name="🆙 Level Up!",
                        value=f"You're now a Level {exp // 10} {job_name.split()[1]}!",
                        inline=False
                    )
        
        embed.set_footer(text="💡 Come back in an hour to work again!")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="bet", description="Bet coins on a coinflip")
    @app_commands.describe(
        bet="Amount of coins to bet",
        choice="Heads or tails"
    )
    @app_commands.choices(choice=[
        app_commands.Choice(name="Heads", value="heads"),
        app_commands.Choice(name="Tails", value="tails")
    ])
    async def bet(self, ctx: commands.Context, bet: int, choice: str):
        if not ctx.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        if bet <= 0:
            embed = discord.Embed(
                title="❌ Invalid Bet",
                description="You must bet at least 1 coin!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        can_bet, won, amount_change, result = economy_system.gamble_coinflip(ctx.guild.id, ctx.author.id, bet, choice)
        
        if not can_bet:
            embed = discord.Embed(
                title="❌ Insufficient Funds",
                description="You don't have enough coins for this bet!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        # Create result embed
        result_emoji = "🪙" if result == "heads" else "🔸"
        
        if won:
            embed = discord.Embed(
                title="🎉 You Won!",
                description=f"The coin landed on **{result}** {result_emoji}\n\nYou won **{amount_change:,}** coins!",
                color=COLORS['success']
            )
        else:
            embed = discord.Embed(
                title="💸 You Lost!",
                description=f"The coin landed on **{result}** {result_emoji}\n\nYou lost **{abs(amount_change):,}** coins!",
                color=COLORS['error']
            )
        
        user_data = economy_system.get_user_data(ctx.guild.id, ctx.author.id)
        embed.add_field(
            name="💰 New Balance",
            value=f"{user_data['balance']:,} coins",
            inline=True
        )
        
        embed.set_footer(text="🎲 Try slots for more gambling fun!")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="slots", description="Play the slot machine")
    @app_commands.describe(bet="Amount of coins to bet")
    async def slots(self, ctx: commands.Context, bet: int):
        if not ctx.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        if bet <= 0:
            embed = discord.Embed(
                title="❌ Invalid Bet",
                description="You must bet at least 1 coin!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        can_bet, winnings, message, slot_result = economy_system.gamble_slots(ctx.guild.id, ctx.author.id, bet)
        
        if not can_bet:
            embed = discord.Embed(
                title="❌ Insufficient Funds",
                description="You don't have enough coins for this bet!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        # Create slot machine display
        slots_display = f"🎰 [ {slot_result[0]} | {slot_result[1]} | {slot_result[2]} ] 🎰"
        
        if winnings > 0:
            embed = discord.Embed(
                title=message,
                description=f"{slots_display}\n\n🎉 **You won {winnings:,} coins!**",
                color=COLORS['success']
            )
        else:
            embed = discord.Embed(
                title=message,
                description=f"{slots_display}\n\n💸 **You lost {bet:,} coins!**",
                color=COLORS['error']
            )
        
        user_data = economy_system.get_user_data(ctx.guild.id, ctx.author.id)
        embed.add_field(
            name="💰 New Balance",
            value=f"{user_data['balance']:,} coins",
            inline=True
        )
        
        embed.set_footer(text="🍀 Feeling lucky? Try again!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyCommands(bot))