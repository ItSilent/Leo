"""
Music Bot Utility Class
"""
import asyncio
import discord
import yt_dlp
import random
from config.settings import YTDL_OPTIONS, FFMPEG_OPTIONS

class MusicBot:
    def __init__(self):
        self.voice_clients = {}
        self.queues = {}
        self.current_songs = {}
        self.loop_modes = {}  # False = no loop, True = loop queue
        self.shuffle_modes = {}  # Track shuffle state per guild
    
    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]
    
    def add_to_queue(self, guild_id, song):
        queue = self.get_queue(guild_id)
        queue.append(song)
    
    def get_next_song(self, guild_id):
        queue = self.get_queue(guild_id)
        if queue:
            if self.shuffle_modes.get(guild_id, False):
                # Shuffle mode: pick random song
                index = random.randint(0, len(queue) - 1)
                return queue.pop(index)
            else:
                # Normal mode: first in queue
                return queue.pop(0)
        elif self.loop_modes.get(guild_id, False) and guild_id in self.current_songs:
            # Loop mode: repeat current song
            return self.current_songs[guild_id]
        return None
    
    def shuffle_queue(self, guild_id):
        queue = self.get_queue(guild_id)
        random.shuffle(queue)
        return len(queue)
    
    def toggle_loop(self, guild_id):
        current_state = self.loop_modes.get(guild_id, False)
        self.loop_modes[guild_id] = not current_state
        return self.loop_modes[guild_id]
    
    def toggle_shuffle(self, guild_id):
        current_state = self.shuffle_modes.get(guild_id, False)
        self.shuffle_modes[guild_id] = not current_state
        return self.shuffle_modes[guild_id]
    
    def clear_queue(self, guild_id):
        queue_length = len(self.get_queue(guild_id))
        self.queues[guild_id] = []
        return queue_length

class YTDLSource:
    def __init__(self, source, *, data):
        self.source = source
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        
        ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)
        
        try:
            print(f"Extracting info for: {url}")
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            
            if not data:
                print("No data returned from yt-dlp")
                return None
            
            # Handle playlist results - get first entry
            if 'entries' in data:
                if not data['entries']:
                    print("No entries found in playlist")
                    return None
                data = data['entries'][0]
            
            if not data.get('url'):
                print("No URL found in extracted data")
                return None
                
            filename = data['url'] if stream else ytdl.prepare_filename(data)
            print(f"Playing audio from: {filename}")
            
            # Create FFmpeg source with proper options
            try:
                source = discord.FFmpegOpusAudio(
                    filename,
                    before_options=FFMPEG_OPTIONS['before_options'],
                    options=FFMPEG_OPTIONS['options']
                )
                print("Using Opus audio source")
                return cls(source, data=data)
            except Exception as opus_error:
                print(f"Opus failed, trying PCM: {opus_error}")
                try:
                    source = discord.FFmpegPCMAudio(
                        filename,
                        before_options=FFMPEG_OPTIONS['before_options'],
                        options=FFMPEG_OPTIONS['options']
                    )
                    print("Using PCM audio source")
                    return cls(source, data=data)
                except Exception as pcm_error:
                    print(f"PCM also failed: {pcm_error}")
                    return None
        except Exception as e:
            print(f"Error in YTDLSource.from_url: {e}")
        return None

# Global music bot instance
music_bot = MusicBot()