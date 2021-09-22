from discord.ext import commands
import discord

import json
import os
import datetime
import random

class Events(commands.Cog):
    """Events"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if ctx.author.bot == True:
            return
        if ctx.guild == None:
            return
        else:
            log_channel = self.bot.get_channel(882503983174930443)
            logEm = discord.Embed(title = "Command excecuted")
            logEm.add_field(name = f"In {ctx.guild.name}", value = f"{ctx.command.qualified_name}")
            await log_channel.send(embed = logEm)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name = "welcome")
        welcomeEm = discord.Embed(description = f"Welcome to {member.guild}, {member.mention}")
        welcomeEm.set_thumbnail(url = member.display_avatar.url)
        welcomeEm.set_author(name = member.name, icon_url = member.display_avatar.url)
        try:
            welcomeEm.set_footer(text = member.guild.name, icon_url = member.guild.icon.url)
        except:
            pass
        welcomeEm.timestamp = datetime.datetime.utcnow()
        if channel:
            try:
                await channel.send(embed = welcomeEm)
            except:
                pass
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
        channel = discord.utils.get(member.guild.text_channels, name = "bye")
        welcomeEm = discord.Embed(description = f"{member} has left us! <:cry:883694072534040579>")
        welcomeEm.set_thumbnail(url = member.display_avatar.url)
        welcomeEm.set_author(name = member.name, icon_url = member.display_avatar.url)
        try:
            welcomeEm.set_footer(text = member.guild.name, icon_url = member.guild.icon.url)
        except:
            pass
        welcomeEm.timestamp = datetime.datetime.utcnow()
        if channel:
            try:
                await channel.send(embed = welcomeEm)
            except:
                pass
        elif not channel:
            try:
                overwrites = {member.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)}
                channel = await member.guild.create_text_channel("bye", overwrites=overwrites)
                channel = discord.utils.get(member.guild.text_channels, name = "bye")
                await channel.send(embed = welcomeEm)
            except:
                pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(description = f"{ctx.author.mention}")
        embed.add_field(name = "Error while excecuting command", value = error)
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Events(bot))
