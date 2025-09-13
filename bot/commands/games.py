"""
Games Commands Module
"""
import discord
from discord.ext import commands
import random
from datetime import datetime
from config.settings import COLORS

class GamesCommands:
    def __init__(self, bot):
        self.bot = bot
        
        # Truth or Dare questions
        self.truth_questions = [
            "What's your biggest fear?",
            "Who was your first crush?",
            "What's the most embarrassing thing you've done?",
            "What's your biggest secret?",
            "If you could date anyone, who would it be?",
            "What's the last lie you told?",
            "What's your most embarrassing childhood memory?",
            "Who in this server do you trust the most?",
            "What's something you've never told anyone?",
            "What's your biggest regret?",
            "If you could switch lives with someone for a day, who would it be?",
            "What's the weirdest thing you've ever eaten?",
            "What's your most irrational fear?",
            "Who was your worst teacher and why?",
            "What's the most childish thing you still do?"
        ]
        
        self.dare_challenges = [
            "Send a selfie to the chat",
            "Do 10 pushups",
            "Sing your favorite song for 30 seconds",
            "Do your best animal impression",
            "Tell a joke",
            "Change your nickname for the next hour",
            "Share an embarrassing photo",
            "Do your best dance moves",
            "Speak in an accent for the next 10 minutes",
            "Tell everyone your most embarrassing moment",
            "Do a cartwheel (if safe to do so)",
            "Recite the alphabet backwards",
            "Tell a scary story",
            "Do your best celebrity impression",
            "Share your most unpopular opinion"
        ]
        
        # 8-Ball responses
        self.eight_ball_responses = [
            "🎱 It is certain",
            "🎱 It is decidedly so", 
            "🎱 Without a doubt",
            "🎱 Yes definitely",
            "🎱 You may rely on it",
            "🎱 As I see it, yes",
            "🎱 Most likely",
            "🎱 Outlook good",
            "🎱 Yes",
            "🎱 Signs point to yes",
            "🎱 Reply hazy, try again",
            "🎱 Ask again later",
            "🎱 Better not tell you now",
            "🎱 Cannot predict now",
            "🎱 Concentrate and ask again",
            "🎱 Don't count on it",
            "🎱 My reply is no",
            "🎱 My sources say no",
            "🎱 Outlook not so good",
            "🎱 Very doubtful"
        ]

    async def setup_commands(self):
        @self.bot.tree.command(name="testbot", description="Test if the bot is working")
        async def test_bot(interaction: discord.Interaction):
            await interaction.response.send_message("🏓 Pong! Bot is working!", ephemeral=True)

        @self.bot.tree.command(name="rps", description="Play Rock Paper Scissors against the bot")
        @discord.app_commands.describe(choice="Your choice: rock, paper, or scissors")
        @discord.app_commands.choices(choice=[
            discord.app_commands.Choice(name="🪨 Rock", value="rock"),
            discord.app_commands.Choice(name="📄 Paper", value="paper"),
            discord.app_commands.Choice(name="✂️ Scissors", value="scissors")
        ])
        async def rock_paper_scissors(interaction: discord.Interaction, choice: discord.app_commands.Choice[str]):
            user_choice = choice.value
            bot_choice = random.choice(["rock", "paper", "scissors"])
            
            choice_emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
            
            # Determine winner
            if user_choice == bot_choice:
                result = "🤝 It's a tie!"
                color = COLORS['info']
            elif (user_choice == "rock" and bot_choice == "scissors") or \
                 (user_choice == "paper" and bot_choice == "rock") or \
                 (user_choice == "scissors" and bot_choice == "paper"):
                result = "🎉 You win!"
                color = COLORS['success']
            else:
                result = "😔 You lose!"
                color = COLORS['error']
            
            embed = discord.Embed(
                title="🎮 Rock Paper Scissors",
                description=f"**{interaction.user.mention}** vs **Bot**",
                color=color
            )
            embed.add_field(name="Your Choice", value=f"{choice_emojis[user_choice]} {user_choice.title()}", inline=True)
            embed.add_field(name="Bot's Choice", value=f"{choice_emojis[bot_choice]} {bot_choice.title()}", inline=True)
            embed.add_field(name="Result", value=result, inline=False)
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="truthordare", description="Get a random truth question or dare challenge")
        @discord.app_commands.describe(choice="Choose truth or dare")
        @discord.app_commands.choices(choice=[
            discord.app_commands.Choice(name="💭 Truth", value="truth"),
            discord.app_commands.Choice(name="💪 Dare", value="dare")
        ])
        async def truth_or_dare(interaction: discord.Interaction, choice: discord.app_commands.Choice[str]):
            if choice.value == "truth":
                question = random.choice(self.truth_questions)
                embed = discord.Embed(
                    title="💭 Truth Question",
                    description=f"**{interaction.user.mention}**, {question}",
                    color=COLORS['info']
                )
            else:
                dare = random.choice(self.dare_challenges)
                embed = discord.Embed(
                    title="💪 Dare Challenge",
                    description=f"**{interaction.user.mention}**, {dare}",
                    color=COLORS['error']
                )
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="8ball", description="Ask the magic 8-ball a question")
        @discord.app_commands.describe(question="Your yes/no question")
        async def eight_ball(interaction: discord.Interaction, question: str):
            response = random.choice(self.eight_ball_responses)
            
            embed = discord.Embed(
                title="🎱 Magic 8-Ball",
                color=COLORS['info']
            )
            embed.add_field(name="Question", value=question, inline=False)
            embed.add_field(name="Answer", value=response, inline=False)
            embed.set_footer(text=f"Asked by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="coinflip", description="Flip a coin")
        async def coin_flip(interaction: discord.Interaction):
            result = random.choice(["Heads", "Tails"])
            emoji = "🟡" if result == "Heads" else "⚪"
            
            embed = discord.Embed(
                title="🪙 Coin Flip",
                description=f"**{emoji} {result}!**",
                color=COLORS['info']
            )
            embed.set_footer(text=f"Flipped by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="dice", description="Roll a dice")
        @discord.app_commands.describe(sides="Number of sides on the dice (default: 6)")
        async def roll_dice(interaction: discord.Interaction, sides: int = 6):
            if sides < 2 or sides > 100:
                await interaction.response.send_message("❌ Please choose between 2 and 100 sides!", ephemeral=True)
                return
                
            result = random.randint(1, sides)
            
            embed = discord.Embed(
                title="🎲 Dice Roll",
                description=f"**You rolled a {result}!**\n(d{sides})",
                color=COLORS['info']
            )
            embed.set_footer(text=f"Rolled by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name="wouldyourather", description="Get a random 'Would You Rather' question")
        async def would_you_rather(interaction: discord.Interaction):
            questions = [
                "Would you rather have the ability to fly or be invisible?",
                "Would you rather have unlimited money or unlimited time?",
                "Would you rather be able to read minds or predict the future?",
                "Would you rather live forever or live for 100 years?",
                "Would you rather have super strength or super speed?",
                "Would you rather never be able to lie or never be able to tell the truth?",
                "Would you rather be famous or rich but not both?",
                "Would you rather lose all your memories or never be able to make new ones?",
                "Would you rather be able to teleport or time travel?",
                "Would you rather always be hot or always be cold?",
                "Would you rather have no internet or no phone?",
                "Would you rather be really tall or really short?",
                "Would you rather have three arms or three legs?",
                "Would you rather never sleep or never eat?",
                "Would you rather control fire or control water?"
            ]
            
            question = random.choice(questions)
            
            embed = discord.Embed(
                title="🤔 Would You Rather",
                description=question,
                color=COLORS['action']
            )
            embed.set_footer(text=f"Question for {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)