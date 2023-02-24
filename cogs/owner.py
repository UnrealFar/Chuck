import typing


import discord
from discord.ext import commands
from discord import app_commands
from bot import Unreal


class OwnerCog(commands.Cog):
    bot: Unreal

    def __init__(self, bot: Unreal):
        self.name = "Owner"
        self.bot = bot


async def setup(bot: Unreal):
    await bot.add_cog(OwnerCog(bot))
