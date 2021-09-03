import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from dotenv import load_dotenv
import os
import json
#import traceback

load_dotenv()

async def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]

TOKEN = os.getenv("token")
bot = commands.Bot(command_prefix=(get_prefix), intents=discord.Intents.all(), case_insensitive=True,  description='Awesome multi-purpose and fun bot!')
bot.remove_command("help")

@bot.event
async def on_guild_join(guild):
    try:
        channel = guild.system_channel
        if channel is not None:
            joinEm=discord.Embed(title="Thank you for adding me to the server!", description="", colour=discord.Colour.blurple())
            joinEm.add_field(name="Prefix", value="The bot's prefix is ?", inline=False)
            joinEm.add_field(name="Commands", value="Do ?help for a list of all the bot commands!", inline=False)
            joinEm.set_footer(icon_url="https://images-ext-1.discordapp.net/external/2NTlKKViwT-O75ct7SeCkG_hSa5SsBYvw9csO1JEfwo/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/859996173943177226/19ec5346838e19dab0d715d5820f2b5a.webp", text="With love, PikaPi#6298")
        await channel.send(embed=joinEm)
    except:
        print("Can't send the join_guild message!")
    
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = 'c!'
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent = 4)

@bot.event
async def on_guild_remove(guild):
    try:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
            prefixes.pop(str(guild.id))
    except:
        return
        
#error-handling
@bot.event
async def on_command_error(ctx, error):
    #error
    embed = discord.Embed(title = "Error", description = error, colour = discord.Colour.green())
    await ctx.send(embed = embed)
    #traceback
    #etype = type(error)
    #trace = error.__traceback__
    #lines = traceback.format_exception(etype,error, trace)
    #traceback_text = ''.join(lines)
    #errorEm=discord.Embed(Title="Error", description=traceback_text, colour=discord.Colour.green())
    #await ctx.send(embed=errorEm)

@bot.event
async def on_message(message):
    if message.author.bot == False:
        try:
            log_channel = bot.get_channel(882503983174930443)
            logEm = discord.Embed(title = "Message", description = f"{message.author}")
            logEm.add_field(name = f"In {message.guild.name}", value = f"{message.content}")
            await log_channel.send(embed = logEm)
        except:
            pass
    if message.guild is None:
        return
    if bot.user.mentioned_in(message):
        await message.channel.send(f"The prefix is {await get_prefix(bot, message)}")
        await bot.process_commands(message)
    else:
        await bot.process_commands(message)
    
@bot.command()
@has_permissions(administrator=True)
async def prefix(ctx, prefix="c!"):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(ctx.guild.id)] = prefix
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)
    await ctx.send(f"The prefix for this server has been set to **{prefix}**")

class help(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", colour = discord.Colour.blurple())
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Extras")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=True)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        emb = discord.Embed(title=self.get_command_signature(command), colour = discord.Colour.red())
        emb.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            emb.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=emb)

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Error", description=str(error))
            await ctx.send(embed=embed)

bot.help_command = help()

initial_extensions = ['cogs.misc','cogs.mod','cogs.fun','cogs.events','cogs.economy','cogs.owner','cogs.nsfw']
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)
        
@bot.command()
@commands.is_owner()
async def updatestatus(ctx, *, newstatus = None):
    if newstatus == None:
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"over {len(bot.guilds)} servers"))
        await ctx.send(f"Reset status to ```Watching over {len(bot.guilds)} guilds```")
    else:
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{newstatus}"))
        await ctx.send(f"Set status to {newstatus}")
    
bot.run(TOKEN)