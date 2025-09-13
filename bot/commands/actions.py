"""
Action Commands Module
"""
import discord
from discord.ext import commands
from datetime import datetime
from bot.utils.gif_handler import get_gif
from config.settings import COLORS

class ActionCommands:
    def __init__(self, bot):
        self.bot = bot

    async def setup_commands(self):
        @self.bot.tree.command(name="hug", description="Give someone a warm hug!")
        @discord.app_commands.describe(user="The user you want to hug")
        async def hug(interaction: discord.Interaction, user: discord.Member):
            gif_url = await get_gif("hug")
            
            embed = discord.Embed(
                title="🤗 Hug!",
                description=f"**{interaction.user.mention}** hugs **{user.mention}**!",
                color=0xffb3d9
            )
            
            if gif_url:
                embed.set_image(url=gif_url)
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="kiss", description="Give someone a sweet kiss!")
        @discord.app_commands.describe(user="The user you want to kiss")
        async def kiss(interaction: discord.Interaction, user: discord.Member):
            gif_url = await get_gif("kiss")
            
            embed = discord.Embed(
                title="💋 Kiss!",
                description=f"**{interaction.user.mention}** kisses **{user.mention}**!",
                color=0xff6b9d
            )
            
            if gif_url:
                embed.set_image(url=gif_url)
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="slap", description="Slap someone playfully!")
        @discord.app_commands.describe(user="The user you want to slap")
        async def slap(interaction: discord.Interaction, user: discord.Member):
            gif_url = await get_gif("slap")
            
            embed = discord.Embed(
                title="👋 Slap!",
                description=f"**{interaction.user.mention}** slaps **{user.mention}**!",
                color=0xff6b6b
            )
            
            if gif_url:
                embed.set_image(url=gif_url)
            
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="poke", description="Poke someone to get their attention!")
        @discord.app_commands.describe(user="The user you want to poke")
        async def poke(interaction: discord.Interaction, user: discord.Member):
            gif_url = await get_gif("poke")
            
            embed = discord.Embed(
                title="👆 Poke!",
                description=f"**{interaction.user.mention}** pokes **{user.mention}**!",
                color=0xffd93d
            )
            
            if gif_url:
                embed.set_image(url=gif_url)
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="pat", description="Give someone a gentle pat!")
        @discord.app_commands.describe(user="The user you want to pat")
        async def pat(interaction: discord.Interaction, user: discord.Member):
            gif_url = await get_gif("pat head")
            
            embed = discord.Embed(
                title="🤚 Pat!",
                description=f"**{interaction.user.mention}** pats **{user.mention}**!",
                color=0xa8e6cf
            )
            
            if gif_url:
                embed.set_image(url=gif_url)
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="cuddle", description="Cuddle with someone!")
        @discord.app_commands.describe(user="The user you want to cuddle")
        async def cuddle(interaction: discord.Interaction, user: discord.Member):
            gif_url = await get_gif("cuddle")
            
            embed = discord.Embed(
                title="🫂 Cuddle!",
                description=f"**{interaction.user.mention}** cuddles with **{user.mention}**!",
                color=0xffaaa5
            )
            
            if gif_url:
                embed.set_image(url=gif_url)
            
            embed.set_footer(text="Cuddles make everything better!", 
                            icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None)
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="dance", description="Dance with someone or by yourself!")
        @discord.app_commands.describe(user="The user you want to dance with (optional)")
        async def dance(interaction: discord.Interaction, user: discord.Member = None):
            gif_url = await get_gif("dance")
            
            if user:
                embed = discord.Embed(
                    title="💃 Let's Dance!",
                    description=f"**{interaction.user.mention}** dances with **{user.mention}**! What amazing moves! 🕺",
                    color=0xc44569,
                    timestamp=datetime.utcnow()
                )
            else:
                embed = discord.Embed(
                    title="💃 Solo Dance!",
                    description=f"**{interaction.user.mention}** is dancing solo! Looking great! 🕺",
                    color=0xc44569,
                    timestamp=datetime.utcnow()
                )
            
            if gif_url:
                embed.set_image(url=gif_url)
            
            embed.set_footer(text="Dance like nobody's watching!", 
                            icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None)
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="wave", description="Wave hello to someone!")
        @discord.app_commands.describe(user="The user you want to wave to")
        async def wave(interaction: discord.Interaction, user: discord.Member):
            gif_url = await get_gif("wave hello")
            
            embed = discord.Embed(
                title="👋 Friendly Wave!",
                description=f"**{interaction.user.mention}** waves hello to **{user.mention}**! Hey there! 😊",
                color=0x54a0ff,
                timestamp=datetime.utcnow()
            )
            
            if gif_url:
                embed.set_image(url=gif_url)
            
            embed.set_footer(text="Such a friendly greeting!", 
                            icon_url=self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None)
            
            await interaction.response.send_message(embed=embed)