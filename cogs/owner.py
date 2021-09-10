from discord.ext import commands
import discord
import random
import asyncio

class Owner(commands.Cog):
    """Commands for owner"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def updatestatus(self, ctx, *, newstatus = None):
        if newstatus == None:
            await ctx.send(f"Updated status to ```Watching over {len(self.bot.guilds)} guilds```")
            await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"over {len(self.bot.guilds)} servers"))
        else:
            await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{newstatus}"))
            await ctx.send(f"Set status to {newstatus}")

def setup(bot):
    bot.add_cog(Owner(bot))
