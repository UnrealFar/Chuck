from discord.ext import commands
import discord

import json
import os
import datetime

class Events(commands.Cog):
    """Events"""

    def __init__(self, bot):
        self.bot = bot
 
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name = "welcome")
        welcomeEm = discord.Embed(description = f"Welcome to {member.guild}, {member.mention}")
        welcomeEm.set_thumbnail(url = member.avatar.url)
        welcomeEm.set_author(name = member.name, icon_url = member.avatar.url)
        try:
            welcomeEm.set_footer(text = member.guild.name, icon_url = member.guild.icon.url)
        except:
            pass
        welcomeEm.timestamp = datetime.datetime.utcnow()
        if channel:
            await channel.send(embed = welcomeEm)
        elif not channel:
            try:
                overwrites = {member.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)}
                await member.guild.create_text_channel("welcome", overwrites=overwrites)
                channel = discord.utils.get(member.guild.text_channels, name = "welcome")
                await channel.send(embed = welcomeEm)
            except:
                pass
        try:
            await member.send(embed = welcomeEm)
        except:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = discord.utils.get(member.guild.text_channels, name = "welcome")
        welcomeEm = discord.Embed(description = f"{member.mention} has left us!")
        welcomeEm.set_thumbnail(url = member.avatar.url)
        welcomeEm.set_author(name = member.name, icon_url = member.display_avatar.url)
        try:
            welcomeEm.set_footer(text = member.guild.name, icon_url = member.guild.icon.url)
        except:
            pass
        welcomeEm.timestamp = datetime.datetime.utcnow()
        if channel:
            await channel.send(embed = welcomeEm)
        elif not channel:
            try:
                overwrites = {member.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)}
                channel = await member.guild.create_text_channel("welcome", overwrites=overwrites)
                channel = discord.utils.get(member.guild.text_channels, name = "welcome")
                await channel.send(embed = welcomeEm)
            except:
                pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot == False:
            logChannel = discord.utils.get(message.guild.text_channels, name = "log")
            logEm = discord.Embed(title = "Message deleted", description = f"In {message.channel.mention}")
            logEm.add_field(name = f"Message sent by {message.author}", value = f"{message.content}")
            logEm.set_thumbnail(url = message.author.avatar.url)
            if logChannel:
                try:
                    await logChannel.send(embed = logEm)
                except:
                    pass
            elif not logChannel:
                try:
                    overwrites = {message.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False)}
                    logChannel = await message.guild.create_text_channel("log", overwrites=overwrites)
                    logChannel = discord.utils.get(message.guild.text_channels, name = "log")
                    await logChannel.send(embed = logEm)
                except:
                    pass

def setup(bot):
    bot.add_cog(Events(bot))
