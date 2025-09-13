"""
Music Commands Module
"""
import asyncio
import discord
from discord.ext import commands
from datetime import datetime
from bot.utils.music_bot import music_bot, YTDLSource
from config.settings import COLORS

class MusicCommands:
    def __init__(self, bot):
        self.bot = bot

    async def setup_commands(self):
        @self.bot.tree.command(name="play", description="Play a song from YouTube")
        @discord.app_commands.describe(song="The song name or YouTube URL to play")
        async def play(interaction: discord.Interaction, song: str):
            if not interaction.user.voice:
                await interaction.response.send_message("❌ You need to be in a voice channel to use music commands!", ephemeral=True)
                return
            
            if not interaction.guild.voice_client:
                voice_channel = interaction.user.voice.channel
                await voice_channel.connect()
                music_bot.voice_clients[interaction.guild.id] = interaction.guild.voice_client
            
            await interaction.response.defer()
            
            print(f"Attempting to play song: {song}")
            player = await YTDLSource.from_url(song, loop=self.bot.loop, stream=True)
            
            if not player:
                await interaction.followup.send("❌ Failed to load the song. Please check the song name or try a different search term.")
                return
            
            # Verify player has required attributes
            if not hasattr(player, 'title') or not hasattr(player, 'url'):
                await interaction.followup.send("❌ Song loaded but missing required information. Please try again.")
                return
            
            voice_client = interaction.guild.voice_client
            song_info = {
                'title': player.title or "Unknown Title",
                'url': player.url or song,
                'uploader': player.uploader or "Unknown Uploader",
                'duration': player.duration or 0
            }
            
            if voice_client.is_playing():
                music_bot.add_to_queue(interaction.guild.id, song_info)
                embed = discord.Embed(
                    title="📋 Added to Queue",
                    description=f"**{song_info['title']}**\nby {song_info['uploader']}",
                    color=COLORS['music'],
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"Position in queue: #{len(music_bot.get_queue(interaction.guild.id))}")
                await interaction.followup.send(embed=embed)
                return
            
            def after_playing(error):
                if error:
                    print(f'Player error: {error}')
                
                try:
                    fut = asyncio.run_coroutine_threadsafe(self.play_next_song(interaction.guild.id), self.bot.loop)
                    fut.result()
                except Exception as e:
                    print(f"Error in after_playing: {e}")
            
            voice_client.play(player.source, after=after_playing)
            music_bot.current_songs[interaction.guild.id] = song_info
            
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"**{song_info['title']}**\nby {song_info['uploader']}",
                color=COLORS['music'],
                timestamp=datetime.utcnow()
            )
            
            view = MusicControlView()
            await interaction.followup.send(embed=embed, view=view)

        @self.bot.tree.command(name="skip", description="Skip the current song")
        async def skip(interaction: discord.Interaction):
            voice_client = interaction.guild.voice_client
            if not voice_client or not voice_client.is_playing():
                await interaction.response.send_message("❌ Nothing is currently playing!", ephemeral=True)
                return
            
            voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped the current song!")

        @self.bot.tree.command(name="stop", description="Stop music and disconnect from voice channel")
        async def stop(interaction: discord.Interaction):
            voice_client = interaction.guild.voice_client
            if not voice_client:
                await interaction.response.send_message("❌ Bot is not connected to a voice channel!", ephemeral=True)
                return
            
            music_bot.queues[interaction.guild.id] = []
            if interaction.guild.id in music_bot.current_songs:
                del music_bot.current_songs[interaction.guild.id]
            
            await voice_client.disconnect()
            await interaction.response.send_message("🛑 Stopped music and disconnected from voice channel!")

        @self.bot.tree.command(name="queue", description="Show the current music queue")
        async def queue(interaction: discord.Interaction):
            queue = music_bot.get_queue(interaction.guild.id)
            if not queue:
                await interaction.response.send_message("📋 Queue is empty!", ephemeral=True)
                return
            
            embed = discord.Embed(title="📋 Music Queue", color=COLORS['music'])
            queue_text = ""
            for i, song in enumerate(queue[:10], 1):
                queue_text += f"{i}. {song['title']}\n"
            
            if len(queue) > 10:
                queue_text += f"\n... and {len(queue) - 10} more songs"
            
            embed.description = queue_text or "Queue is empty!"
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def play_next_song(self, guild_id):
        next_song = music_bot.get_next_song(guild_id)
        if not next_song:
            return
        
        try:
            voice_client = music_bot.voice_clients.get(guild_id)
            if not voice_client:
                return
            
            player = await YTDLSource.from_url(next_song['url'], loop=self.bot.loop, stream=True)
            if not player:
                print(f"Failed to load next song: {next_song.get('title', 'Unknown')}")
                await self.play_next_song(guild_id)
                return
            
            # Verify player has required attributes
            if not hasattr(player, 'source'):
                print("Player missing audio source")
                await self.play_next_song(guild_id)
                return
            
            def after_playing(error):
                if error:
                    print(f'Player error: {error}')
                try:
                    fut = asyncio.run_coroutine_threadsafe(self.play_next_song(guild_id), self.bot.loop)
                    fut.result()
                except Exception as e:
                    print(f"Error in after_playing: {e}")
            
            voice_client.play(player.source, after=after_playing)
            music_bot.current_songs[guild_id] = next_song
            
        except Exception as e:
            print(f"Error playing next song: {e}")

class MusicControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.secondary, row=0)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            button.label = "▶️ Resume"
            await interaction.response.edit_message(view=self)
        elif voice_client and voice_client.is_paused():
            voice_client.resume()
            button.label = "⏸️ Pause"
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)
    
    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.primary, row=0)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)
    
    @discord.ui.button(label="🛑 Stop", style=discord.ButtonStyle.danger, row=0)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = interaction.guild.voice_client
        if voice_client:
            music_bot.queues[interaction.guild.id] = []
            if interaction.guild.id in music_bot.current_songs:
                del music_bot.current_songs[interaction.guild.id]
            await voice_client.disconnect()
            await interaction.response.send_message("🛑 Stopped and disconnected!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Bot is not connected!", ephemeral=True)
    
    @discord.ui.button(label="📋 Queue", style=discord.ButtonStyle.secondary, row=0)
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        queue = music_bot.get_queue(interaction.guild.id)
        current_song = music_bot.current_songs.get(interaction.guild.id)
        
        embed = discord.Embed(title="📋 Music Queue", color=COLORS['music'])
        
        if current_song:
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**{current_song['title']}**\nby {current_song['uploader']}",
                inline=False
            )
        
        if queue:
            queue_text = ""
            for i, song in enumerate(queue[:8], 1):  # Show max 8 songs
                queue_text += f"{i}. {song['title']}\n"
            
            if len(queue) > 8:
                queue_text += f"\n... and {len(queue) - 8} more songs"
            
            embed.add_field(name="⏭️ Up Next", value=queue_text, inline=False)
        else:
            embed.add_field(name="⏭️ Up Next", value="Queue is empty", inline=False)
        
        # Show current modes
        loop_mode = music_bot.loop_modes.get(interaction.guild.id, False)
        shuffle_mode = music_bot.shuffle_modes.get(interaction.guild.id, False)
        modes = []
        if loop_mode:
            modes.append("🔁 Loop")
        if shuffle_mode:
            modes.append("🔀 Shuffle")
        
        if modes:
            embed.add_field(name="🎛️ Active Modes", value=" • ".join(modes), inline=False)
        
        embed.set_footer(text=f"Total songs in queue: {len(queue)}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🎵 Now Playing", style=discord.ButtonStyle.secondary, row=0)
    async def now_playing_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        current_song = music_bot.current_songs.get(interaction.guild.id)
        voice_client = interaction.guild.voice_client
        
        if not current_song or not voice_client:
            await interaction.response.send_message("❌ Nothing is currently playing!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{current_song['title']}**",
            color=COLORS['music']
        )
        
        embed.add_field(name="👤 Uploader", value=current_song.get('uploader', 'Unknown'), inline=True)
        
        duration = current_song.get('duration', 0)
        if duration:
            minutes, seconds = divmod(duration, 60)
            embed.add_field(name="⏱️ Duration", value=f"{int(minutes)}:{int(seconds):02d}", inline=True)
        
        # Voice status
        if voice_client.is_playing():
            status = "▶️ Playing"
        elif voice_client.is_paused():
            status = "⏸️ Paused"
        else:
            status = "⏹️ Stopped"
        embed.add_field(name="📊 Status", value=status, inline=True)
        
        # Show active modes
        loop_mode = music_bot.loop_modes.get(interaction.guild.id, False)
        shuffle_mode = music_bot.shuffle_modes.get(interaction.guild.id, False)
        modes = []
        if loop_mode:
            modes.append("🔁 Loop")
        if shuffle_mode:
            modes.append("🔀 Shuffle")
        
        if modes:
            embed.add_field(name="🎛️ Active Modes", value=" • ".join(modes), inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔀 Shuffle", style=discord.ButtonStyle.secondary, row=1)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        queue = music_bot.get_queue(interaction.guild.id)
        if not queue:
            await interaction.response.send_message("❌ Queue is empty - nothing to shuffle!", ephemeral=True)
            return
        
        shuffled_count = music_bot.shuffle_queue(interaction.guild.id)
        is_shuffle_mode = music_bot.toggle_shuffle(interaction.guild.id)
        
        if is_shuffle_mode:
            button.label = "🔀 Shuffle: ON"
            button.style = discord.ButtonStyle.success
            message = f"🔀 Shuffle mode **enabled** and queue shuffled! ({shuffled_count} songs)"
        else:
            button.label = "🔀 Shuffle"
            button.style = discord.ButtonStyle.secondary
            message = f"🔀 Shuffle mode **disabled**. Queue was shuffled one last time! ({shuffled_count} songs)"
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(message, ephemeral=True)
    
    @discord.ui.button(label="🗑️ Clear Queue", style=discord.ButtonStyle.danger, row=1)
    async def clear_queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cleared_count = music_bot.clear_queue(interaction.guild.id)
        
        if cleared_count == 0:
            await interaction.response.send_message("❌ Queue is already empty!", ephemeral=True)
        else:
            await interaction.response.send_message(f"🗑️ Cleared {cleared_count} songs from the queue!", ephemeral=True)
    
    @discord.ui.button(label="🔁 Loop", style=discord.ButtonStyle.secondary, row=1)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        is_loop_mode = music_bot.toggle_loop(interaction.guild.id)
        
        if is_loop_mode:
            button.label = "🔁 Loop: ON"
            button.style = discord.ButtonStyle.success
            message = "🔁 Loop mode **enabled** - Current song will repeat when queue is empty!"
        else:
            button.label = "🔁 Loop"
            button.style = discord.ButtonStyle.secondary
            message = "🔁 Loop mode **disabled**"
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(message, ephemeral=True)