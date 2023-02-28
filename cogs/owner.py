import typing


import discord
from discord.ext import commands
from discord import app_commands
from bot import Unreal


class OwnerCog(commands.Cog):
    name = "Owner"
    bot: Unreal

    def __init__(self, bot: Unreal):
        self.bot = bot


async def setup(bot: Unreal):
    await bot.add_cog(OwnerCog(bot))
