import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from bot.database.levelling import levelling_system
from config.settings import COLORS

class LevellingAdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="setlevelupchannel", description="Set the channel for level up announcements (Admin only)")
    @app_commands.describe(channel="The channel to send level up messages to (leave empty to use current channel)")
    async def set_levelup_channel(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
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
        
        target_channel = channel or interaction.channel
        
        # Update settings
        levelling_system.update_server_settings(
            interaction.guild.id,
            levelup_channel=target_channel.id if target_channel else None
        )
        
        embed = discord.Embed(
            title="✅ Level Up Channel Set",
            description=f"Level up announcements will now be sent to {target_channel.mention}",
            color=COLORS['success']
        )
        embed.set_footer(text="Users will see level up messages in this channel when they level up!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="addlevelrole", description="Add a role reward for reaching a specific level (Admin only)")
    @app_commands.describe(
        level="The level required to get this role",
        role="The role to give to users who reach this level"
    )
    async def add_level_role(self, interaction: discord.Interaction, level: int, role: discord.Role):
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need Administrator permissions to use this command!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if level < 1:
            embed = discord.Embed(
                title="❌ Invalid Level",
                description="Level must be 1 or higher!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if bot can manage this role
        if role >= interaction.guild.me.top_role:
            embed = discord.Embed(
                title="❌ Role Hierarchy Error",
                description="I can't manage this role because it's higher than or equal to my highest role!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Add level role
        levelling_system.set_level_role(interaction.guild.id, level, role.id)
        
        embed = discord.Embed(
            title="✅ Level Role Added",
            description=f"Users who reach **Level {level}** will automatically get the {role.mention} role!",
            color=COLORS['success']
        )
        embed.add_field(
            name="💡 Note",
            value="Existing users at this level or higher will get the role when they send their next message.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="removelevelrole", description="Remove a role reward for a specific level (Admin only)")
    @app_commands.describe(level="The level to remove the role reward from")
    async def remove_level_role(self, interaction: discord.Interaction, level: int):
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need Administrator permissions to use this command!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get current level roles
        level_roles = levelling_system.get_level_roles(interaction.guild.id)
        
        if str(level) not in level_roles:
            embed = discord.Embed(
                title="❌ No Role Found",
                description=f"There is no role reward set for Level {level}!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Remove level role
        levelling_system.remove_level_role(interaction.guild.id, level)
        
        embed = discord.Embed(
            title="✅ Level Role Removed",
            description=f"Removed role reward for **Level {level}**",
            color=COLORS['success']
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="levelroles", description="View all level role rewards (Admin only)")
    async def level_roles(self, interaction: discord.Interaction):
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need Administrator permissions to use this command!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        level_roles = levelling_system.get_level_roles(interaction.guild.id)
        
        if not level_roles:
            embed = discord.Embed(
                title="📋 Level Role Rewards",
                description="No level role rewards are currently set up.\n\nUse `/addlevelrole` to add role rewards for specific levels!",
                color=COLORS['info']
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title="🏆 Level Role Rewards",
            description="Current role rewards for levelling up:",
            color=COLORS['success']
        )
        
        # Sort by level
        sorted_roles = sorted(level_roles.items(), key=lambda x: int(x[0]))
        
        roles_text = ""
        for level_str, role_id in sorted_roles:
            role = interaction.guild.get_role(role_id)
            if role:
                roles_text += f"**Level {level_str}:** {role.mention}\n"
            else:
                roles_text += f"**Level {level_str}:** ❌ *Role not found (ID: {role_id})*\n"
        
        embed.add_field(
            name="🎯 Role Rewards",
            value=roles_text or "No valid roles found",
            inline=False
        )
        
        embed.set_footer(text="Use /addlevelrole or /removelevelrole to manage role rewards")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="levelsettings", description="View and configure levelling system settings (Admin only)")
    async def level_settings(self, interaction: discord.Interaction):
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need Administrator permissions to use this command!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        settings = levelling_system.get_server_settings(interaction.guild.id)
        
        embed = discord.Embed(
            title="⚙️ Levelling System Settings",
            description=f"Current configuration for **{interaction.guild.name}**",
            color=COLORS['info']
        )
        
        # Level up channel
        levelup_channel_id = settings.get("levelup_channel")
        if levelup_channel_id:
            channel = self.bot.get_channel(levelup_channel_id)
            channel_text = channel.mention if channel else f"❌ *Channel not found (ID: {levelup_channel_id})*"
        else:
            channel_text = "Same channel as level up message"
        
        embed.add_field(
            name="📢 Level Up Channel",
            value=channel_text,
            inline=False
        )
        
        # XP System
        embed.add_field(
            name="💎 XP System",
            value=f"{'✅ Enabled' if settings.get('xp_enabled', True) else '❌ Disabled'}",
            inline=True
        )
        
        # Spam Protection
        embed.add_field(
            name="🛡️ Spam Protection",
            value=f"{'✅ Enabled' if settings.get('spam_protection', True) else '❌ Disabled'}",
            inline=True
        )
        
        # Role count
        level_roles = settings.get("level_roles", {})
        embed.add_field(
            name="🏆 Level Roles",
            value=f"{len(level_roles)} role rewards set",
            inline=True
        )
        
        # Level up message
        embed.add_field(
            name="💬 Level Up Message",
            value=f"```{settings.get('levelup_message', '🎉 {user_mention} leveled up to **Level {level}**! 🚀')}```",
            inline=False
        )
        
        embed.set_footer(text="Use the various level commands to modify these settings!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="togglexp", description="Enable or disable the XP system (Admin only)")
    async def toggle_xp(self, interaction: discord.Interaction):
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need Administrator permissions to use this command!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        settings = levelling_system.get_server_settings(interaction.guild.id)
        current_state = settings.get("xp_enabled", True)
        new_state = not current_state
        
        levelling_system.update_server_settings(interaction.guild.id, xp_enabled=new_state)
        
        embed = discord.Embed(
            title="✅ XP System Updated",
            description=f"XP system is now **{'Enabled' if new_state else 'Disabled'}**",
            color=COLORS['success']
        )
        
        if new_state:
            embed.add_field(
                name="🎉 XP Enabled",
                value="Users will now earn XP for sending messages and can level up!",
                inline=False
            )
        else:
            embed.add_field(
                name="⏸️ XP Disabled",
                value="Users will no longer earn XP. Existing levels and XP are preserved.",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="togglespamprotection", description="Enable or disable spam protection (Admin only)")
    async def toggle_spam_protection(self, interaction: discord.Interaction):
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need Administrator permissions to use this command!",
                color=COLORS['error']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        settings = levelling_system.get_server_settings(interaction.guild.id)
        current_state = settings.get("spam_protection", True)
        new_state = not current_state
        
        levelling_system.update_server_settings(interaction.guild.id, spam_protection=new_state)
        
        embed = discord.Embed(
            title="✅ Spam Protection Updated",
            description=f"Spam protection is now **{'Enabled' if new_state else 'Disabled'}**",
            color=COLORS['success']
        )
        
        if new_state:
            embed.add_field(
                name="🛡️ Protection Enabled",
                value="Users who spam messages will receive warnings and potential timeouts.",
                inline=False
            )
        else:
            embed.add_field(
                name="⚠️ Protection Disabled",
                value="Spam detection is disabled. Users can send messages without restrictions.",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LevellingAdminCommands(bot))