import discord
from discord.ext import commands

async def hybrid_send(ctx: commands.Context, embed: discord.Embed = None, content: str = None, ephemeral: bool = False):
    """
    Hybrid-safe send function that works for both slash and prefix commands
    """
    if ctx.interaction:
        # This is a slash command
        if ctx.interaction.response.is_done():
            # Response already sent, use followup
            await ctx.interaction.followup.send(content=content, embed=embed, ephemeral=ephemeral)
        else:
            # Send initial response
            await ctx.interaction.response.send_message(content=content, embed=embed, ephemeral=ephemeral)
    else:
        # This is a prefix command - ignore ephemeral
        await ctx.send(content=content, embed=embed)

async def hybrid_defer(ctx: commands.Context):
    """
    Hybrid-safe defer function
    """
    if ctx.interaction:
        await ctx.interaction.response.defer()
    else:
        # For prefix commands, just start typing
        async with ctx.typing():
            pass