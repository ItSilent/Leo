import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from bot.database.prefix_manager import prefix_manager
from bot.utils.hybrid_helpers import hybrid_send
from config.settings import COLORS

class PrefixAdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="setprefix", description="Change the command prefix for this server")
    @app_commands.describe(prefix="The new prefix to use (1-5 characters)")
    async def set_prefix(self, ctx: commands.Context, prefix: str):
        """Change the command prefix for this server (Admin only)"""
        if not ctx.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
            
        # Check permissions
        if not hasattr(ctx.author, 'guild_permissions') or not ctx.author.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need **Manage Server** permissions to change the prefix!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        # Validate and set prefix
        success = prefix_manager.set_prefix(ctx.guild.id, prefix)
        
        if not success:
            embed = discord.Embed(
                title="❌ Invalid Prefix",
                description="**Invalid prefix!** Prefix must be:\n\n" +
                           "• 1-5 characters long\n" +
                           "• Cannot contain spaces, @, or #\n" +
                           "• Cannot start with /\n" +
                           "• Cannot be only whitespace",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="✅ Prefix Changed",
            description=f"Server prefix changed to: **`{prefix}`**\n\n" +
                       f"You can now use commands like:\n" +
                       f"• `{prefix}help` (prefix command)\n" +
                       f"• `/help` (slash command)",
            color=COLORS['success']
        )
        embed.add_field(
            name="💡 Both Work!",
            value=f"Both `{prefix}command` and `/command` will work!\nUsers can choose their preferred style.",
            inline=False
        )
        embed.set_footer(text="Hybrid commands give users the best of both worlds!")
        
        await hybrid_send(ctx, embed=embed)
    
    @commands.hybrid_command(name="prefix", description="Show the current command prefix for this server")
    async def show_prefix(self, ctx: commands.Context):
        """Show the current command prefix for this server"""
        if not ctx.guild:
            embed = discord.Embed(
                title="📋 Current Prefix",
                description="In DMs, use `!` as the prefix or `/` for slash commands",
                color=COLORS['info']
            )
            await hybrid_send(ctx, embed=embed)
            return
        
        current_prefix = prefix_manager.get_prefix(ctx.guild.id)
        
        embed = discord.Embed(
            title="📋 Current Prefix",
            description=f"**Current prefix:** `{current_prefix}`",
            color=COLORS['info']
        )
        embed.add_field(
            name="🎮 How to Use Commands",
            value=f"**Prefix Commands:** `{current_prefix}help`, `{current_prefix}balance`\n" +
                  f"**Slash Commands:** `/help`, `/balance`\n\n" +
                  f"Both styles work exactly the same!",
            inline=False
        )
        embed.add_field(
            name="⚙️ Change Prefix",
            value=f"Use `{current_prefix}setprefix <new_prefix>` or `/setprefix` to change it\n" +
                  f"(Requires Manage Server permission)",
            inline=False
        )
        embed.set_footer(text="💡 You can also mention the bot as a prefix!")
        
        await hybrid_send(ctx, embed=embed)
    
    @commands.hybrid_command(name="resetprefix", description="Reset the server prefix to default (!)")
    async def reset_prefix(self, ctx: commands.Context):
        """Reset the server prefix to default (Admin only)"""
        if not ctx.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in servers!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
            
        # Check permissions
        if not hasattr(ctx.author, 'guild_permissions') or not ctx.author.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need **Manage Server** permissions to reset the prefix!",
                color=COLORS['error']
            )
            await hybrid_send(ctx, embed=embed, ephemeral=True)
            return
        
        default_prefix = prefix_manager.reset_prefix(ctx.guild.id)
        
        embed = discord.Embed(
            title="✅ Prefix Reset",
            description=f"Server prefix reset to default: **`{default_prefix}`**\n\n" +
                       f"You can now use commands like:\n" +
                       f"• `{default_prefix}help` (prefix command)\n" +
                       f"• `/help` (slash command)",
            color=COLORS['success']
        )
        embed.set_footer(text="Default prefix restored!")
        
        await hybrid_send(ctx, embed=embed)

async def setup(bot):
    await bot.add_cog(PrefixAdminCommands(bot))