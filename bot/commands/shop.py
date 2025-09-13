import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import math
from bot.database.economy import economy_system
from bot.utils.hybrid_helpers import hybrid_send
from config.settings import COLORS

class ShopCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="shop", description="Browse the server shop")
    async def shop(self, ctx: commands.Context):
        if not ctx.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        shop_items = economy_system.get_shop_items(ctx.guild.id)
        
        if not shop_items:
            embed = discord.Embed(
                title="🛒 Server Shop",
                description="The shop is currently empty! Come back later.",
                color=COLORS['info']
            )
            await hybrid_send(ctx, embed=embed)
            return
        
        embed = discord.Embed(
            title="🛒 Server Shop",
            description="**Welcome to the shop!** Use `/buy <item>` to purchase items.",
            color=COLORS['info']
        )
        
        for item_id, item_data in shop_items.items():
            embed.add_field(
                name=f"{item_id} {item_data['name']}",
                value=f"💰 **{item_data['price']:,}** coins\n{item_data['description']}",
                inline=True
            )
        
        user_data = economy_system.get_user_data(ctx.guild.id, ctx.author.id)
        embed.set_footer(text=f"Your balance: {user_data['balance']:,} coins | Use /inventory to see your items")
        
        await hybrid_send(ctx, embed=embed)
    
    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item="The item to buy (use the emoji from /shop)")
    async def buy(self, interaction: discord.Interaction, item: str):
        if not ctx.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        success, message = economy_system.buy_item(ctx.guild.id, ctx.author.id, item)
        
        if success:
            embed = discord.Embed(
                title="✅ Purchase Successful!",
                description=message,
                color=COLORS['success']
            )
            
            user_data = economy_system.get_user_data(ctx.guild.id, ctx.author.id)
            embed.add_field(
                name="💰 Remaining Balance",
                value=f"{user_data['balance']:,} coins",
                inline=True
            )
        else:
            embed = discord.Embed(
                title="❌ Purchase Failed",
                description=message,
                color=COLORS['error']
            )
        
        embed.set_footer(text="💡 Use /inventory to see your items!")
        
        await hybrid_send(ctx, embed=embed)
    
    @app_commands.command(name="inventory", description="View your inventory")
    async def inventory(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
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
                description="Bots don't have inventories!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        user_data = economy_system.get_user_data(ctx.guild.id, target.id)
        shop_items = economy_system.get_shop_items(ctx.guild.id)
        
        embed = discord.Embed(
            title=f"🎒 {target.display_name}'s Inventory",
            color=COLORS['info']
        )
        
        if not user_data['inventory']:
            embed.description = "This inventory is empty! Visit the `/shop` to buy items."
        else:
            inventory_text = ""
            total_value = 0
            
            for item_id, quantity in user_data['inventory'].items():
                if quantity > 0 and item_id in shop_items:
                    item_data = shop_items[item_id]
                    item_value = item_data['price'] * quantity
                    total_value += item_value
                    
                    inventory_text += f"{item_id} **{item_data['name']}** x{quantity}\n"
                    inventory_text += f"└ Worth: {item_value:,} coins\n\n"
            
            if inventory_text:
                embed.description = inventory_text
                embed.add_field(
                    name="💎 Total Inventory Value",
                    value=f"{total_value:,} coins",
                    inline=True
                )
            else:
                embed.description = "This inventory is empty! Visit the `/shop` to buy items."
        
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="💡 More items coming soon!")
        
        await hybrid_send(ctx, embed=embed)
    
    @app_commands.command(name="richest", description="See the richest users in the server")
    @app_commands.describe(category="What to rank by")
    @app_commands.choices(category=[
        app_commands.Choice(name="💰 Current Balance", value="balance"),
        app_commands.Choice(name="💎 Total Earned", value="total_earned"),
        app_commands.Choice(name="🔥 Daily Streak", value="streak")
    ])
    async def richest(self, interaction: discord.Interaction, category: str = "balance"):
        if not ctx.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        leaderboard = economy_system.get_leaderboard(ctx.guild.id, category, limit=10)
        
        if not leaderboard:
            embed = discord.Embed(
                title="📊 Economy Leaderboard",
                description="No users found! Start using economy commands to appear here!",
                color=COLORS['info']
            )
            await hybrid_send(ctx, embed=embed)
            return
        
        # Title mapping
        titles = {
            "balance": "💰 Richest Users",
            "total_earned": "💎 Top Earners",
            "streak": "🔥 Daily Streak Champions"
        }
        
        embed = discord.Embed(
            title=f"📊 {titles.get(category, 'Economy Leaderboard')}",
            description=f"Top performers in **{ctx.guild.name}**",
            color=COLORS['success']
        )
        
        leaderboard_text = ""
        for i, (user_id, user_data) in enumerate(leaderboard, 1):
            user = self.bot.get_user(user_id)
            if not user:
                continue
            
            # Rank emoji
            if i == 1:
                rank_emoji = "🥇"
            elif i == 2:
                rank_emoji = "🥈" 
            elif i == 3:
                rank_emoji = "🥉"
            else:
                rank_emoji = f"**{i}.**"
            
            # Value based on category
            if category == "balance":
                value = f"{user_data['balance']:,} coins"
            elif category == "total_earned":
                value = f"{user_data['total_earned']:,} coins earned"
            elif category == "streak":
                value = f"{user_data['daily_streak']} day streak"
            
            leaderboard_text += f"{rank_emoji} {user.display_name}\n"
            leaderboard_text += f"└ {value}\n\n"
        
        embed.description += f"\n\n{leaderboard_text}"
        embed.set_footer(text="💡 Use economy commands to climb the ranks!")
        
        await hybrid_send(ctx, embed=embed)

async def setup(bot):
    await bot.add_cog(ShopCommands(bot))