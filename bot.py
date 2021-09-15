import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from dotenv import load_dotenv
import os
import json
import traceback

load_dotenv()

async def get_prefix(bot, message):
    if message.guild != None:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        return prefixes.get(str(message.guild.id), "c!")
    else:
        return ("c!")

TOKEN = os.getenv("token")
bot = commands.AutoShardedBot(command_prefix=(get_prefix), intents=discord.Intents.all(), case_insensitive=True,  description='Awesome multi-purpose and fun bot!', shard_count = 10)
bot.remove_command("help")

@bot.event
async def on_guild_join(guild):
    try:
        channel = guild.system_channel
        if channel is not None:
            joinEm=discord.Embed(title="Thank you for adding me to the server!", description="", colour=discord.Colour.blurple())
            joinEm.add_field(name="Prefix", value="The bot's prefix is c!", inline=False)
            joinEm.add_field(name="Commands", value="Do ?help for a list of all the bot commands!", inline=False)
            joinEm.set_footer(icon_url="https://images-ext-1.discordapp.net/external/1qUCiiAC2VexuiXFtwtRUjhY-7YO5xUzHeiRS6rJ7QA/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/859996173943177226/cb3a07af653f2878ba1795256dcb822c.png?width=598&height=598", text="With love, Far.GG#6298")
        await channel.send(embed=joinEm)
    except:
        pass
    
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = 'c!'
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent = 4)

#SLASH COMMANDS
@bot.slash_command()
@commands.guild_only()
@commands.has_permissions(manage_nicknames = True)
async def nickname(ctx, member: discord.Member, *, new_nick):
    old_name = member.name
    try:
        await member.edit(nick = new_nick)
    except Exception as e:
        await ctx.send(e)
        return
    await ctx.respond(f"{old_name}'s nickname was set to {new_nick}!")

@bot.event
async def on_guild_remove(guild):
    try:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
            prefixes.pop(str(guild.id))
    except:
        return

class HelpCommand(commands.HelpCommand):
    def get_ending_note(self):
        return "Use c!{0} [command] for more info on a command.".format(
            self.invoked_with
        )

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = "|".join(command.aliases)
            fmt = f"[{command.name}|{aliases}]"
            if parent:
                fmt = f"{parent}, {fmt}"
            alias = fmt
        else:
            alias = command.name if not parent else f"{parent} {command.name}"
        return f"{alias} {command.signature}"

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Chuck's Help Menu!", color=discord.Color.blurple())
        description = self.context.bot.description
        if description:
            embed.description = description

        for cog_, cmds in mapping.items():
            name = "Other Commands" if cog_ is None else cog_.qualified_name
            filtered = await self.filter_commands(cmds, sort=True)
            if filtered:
                value = "\u002C ".join(f"`{c.name}`" for c in cmds)
                if cog_ and cog_.description:
                    value = "{0}\n{1}".format(cog_.description, value)

                embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog_):
        embed = discord.Embed(title=f"{cog_.qualified_name} Commands")
        if cog_.description:
            embed.description = cog_.description

        filtered = await self.filter_commands(cog_.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(
                name=self.get_command_signature(command),
                value=command.short_doc or "...",
                inline=False,
            )

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=group.qualified_name)
        if group.help:
            embed.description = group.help

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            for command in filtered:
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=command.short_doc or "...",
                    inline=False,
                )

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)


    send_command_help = send_group_help

bot.help_command = HelpCommand()

initial_extensions = ['cogs.misc','cogs.mod','cogs.fun','cogs.events','cogs.economy','cogs.owner','cogs.nsfw','cogs.giveaways', 'cogs.levels']
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.message_command()
@bot.slash_command(guild_ids = [860767299236921344])
async def load(ctx, *, name: str):
    if ctx.author.id != 859996173943177226:
        await ctx.respond("Only my owner can use this command ;-;")
        return
    try:
        bot.load_extension(f"cogs.{name}")
        await ctx.send(f'"**{name}**" Cog loaded!')
    except Exception as e:
        await ctx.send(e)

@bot.message_command()
@bot.slash_command(guild_ids = [860767299236921344])
async def reload(ctx, *, name: str):
    if ctx.author.id != 859996173943177226:
        await ctx.send("Only my owner can use this command ;-;")
        return
    try:
        bot.reload_extension(f"cogs.{name}")
        await ctx.send(f'"**{name}**" Cog reloaded!')
    except Exception as e:
        await ctx.send(e)

@bot.message_command()
@bot.slash_command(guild_ids = [860767299236921344])
async def unload(ctx, *, name: str):
    if ctx.author.id != 859996173943177226:
        await ctx.send("Only my owner can use this command ;-;")
    try:
        bot.unload_extension(f"cogs.{name}")
        await ctx.send(f'"**{name}**" Cog unloaded!')
    except Exception as e:
        await ctx.send(e)

@bot.message_command()
@bot.slash_command()
async def ping(ctx):
    """🏓Shows Chuck's ping"""
    bot_ping = round(bot.latency * 1000)
    pingEm = discord.Embed(title="Pong!", description="", colour = discord.Color.blurple())
    pingEm.add_field(name="Bot Ping", value=f"🏓 {bot_ping}ms", inline=False)
    await ctx.send(embed = pingEm)

@bot.message_command()
@bot.slash_command()
async def unbanall(ctx):
    if ctx.author.id != 859996173943177226:
        await ctx.respond("Only my owner can use this command ;-;")
        return
    banned_users = await ctx.guild.bans()
    try:
        for ban_entry in banned_users:
            await ctx.guild.unban(ban_entry.user)
        await ctx.send(f"Unbaned everyone!")
    except Exception as e:
        await ctx.send(f"{e}")

bot.run(TOKEN)