import typing


import discord
from discord.ext import commands, tasks
from discord import app_commands
from bot import Unreal


class MiscCog(commands.Cog):
    bot: Unreal

    def __init__(self, bot: Unreal):
        self.name = "Misc"
        self.bot: Unreal = bot
        self.sc = None
        self.smsg = None

    async def cog_load(self):
        self.update_bot_stats.start()

    @tasks.loop(minutes=30)
    async def update_bot_stats(self):
        await self.bot.wait_until_ready()
        self.sc = sc = self.sc or await self.bot.fetch_channel(887939435210104862)
        self.smsg = self.smsg or await sc.fetch_message(890070751670075412)
        gs = len(self.bot.guilds)
        ss = len(self.bot.shards)
        us = len(self.bot.users)
        sem = discord.Embed(title="Chuck's Stats", colour=0xF47FFF)
        sem.description = f"""> **User Count**: I am watching over **(`{us}`)** users!
        > **Server Count**: I am in **(`{gs}`)** servers!
        > **Shard Count**: I am running with a shard count of **(`{ss}`)**
        > **Last Updated**: {discord.utils.format_dt(discord.utils.utcnow(), style="R")}
        """
        await self.smsg.edit(embed=sem)
        d = {"server_count": gs, "shard_count": ss}
        await self.bot.session.post(
            "https://top.gg/api/bots/864785515978031115/stats", data=d
        )
        print(f"Updated bot stats on TOPGG!\nData={d}")


async def setup(bot: Unreal):
    await bot.add_cog(MiscCog(bot))
