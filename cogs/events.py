from discord.ext import commands
import discord

import datetime

class Events(commands.Cog):
    """Events"""

    def __init__(self, bot):
        self.bot = bot
 
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name = "welcome")
        welcomeEm = discord.Embed(description = f"Welcome to {member.guild}, {member.mention}")
        welcomeEm.set_thumbnail(url = member.avatar_url)
        welcomeEm.set_author(name = member.name, icon_url = member.avatar_url)
        welcomeEm.set_footer(text = member.guild.name, icon_url = member.guild.icon_url)
        welcomeEm.timestamp = datetime.datetime.utcnow()
        if channel:
            await channel.set_permissions(member.guild.default_role, read_messages=True, send_messages=False)
            await channel.send(embed = welcomeEm)
        elif not channel:
            overwrites = {member.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)}
            await guild.create_text_channel("welcome", overwrites=overwrites)
            channel = discord.utils.get(member.guild.text_channels, name = "welcome")
            await channel.send(embed = welcomeEm)
        try:
            await member.send(embed = welcomeEm)
        except:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = discord.utils.get(member.guild.text_channels, name = "welcome")
        welcomeEm = discord.Embed(description = f"{member.mention} has left us!")
        welcomeEm.set_thumbnail(url = member.avatar_url)
        welcomeEm.set_author(name = member.name, icon_url = member.avatar_url)
        welcomeEm.set_footer(text = member.guild.name, icon_url = member.guild.icon_url)
        welcomeEm.timestamp = datetime.datetime.utcnow()
        if channel:
            await channel.set_permissions(member.guild.default_role, read_messages=True, send_messages=False)
            await channel.send(embed = welcomeEm)
        elif not channel:
            overwrites = {member.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)}
            channel = await member.guild.create_text_channel("welcome", overwrites=overwrites)
            channel = discord.utils.get(member.guild.text_channels, name = "welcome")
            await channel.send(embed = welcomeEm)

def setup(bot):
    bot.add_cog(Events(bot))
