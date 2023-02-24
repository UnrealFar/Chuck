from __future__ import annotations

import os
import traceback
import typing
import time
import datetime
import discord
import functools
import orjson
import aiohttp
import asyncio
import app
import utils
from discord.ext import commands
from discord import app_commands


class Unreal(commands.AutoShardedBot):

    session: aiohttp.ClientSession
    app: aiohttp.web.Application

    owner_guilds = [discord.Object(g_id) for g_id in orjson.loads(os.environ['owner_guilds']) if "owner_guilds" in os.environ]
    owner_ids = (
        859996173943177226,
        990495982850551838,
    )

    def __init__(self,) -> None:
        self.token = os.environ['bot_token']
        self.dbl_token = os.environ['dbl_token']
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            message_content=True,
        )
        allowed_mentions = discord.AllowedMentions(
            roles=False,
            everyone=False,
            users=True
        )
        super().__init__(
            intents=intents,
            allowed_mentions=allowed_mentions,
            command_prefix=commands.when_mentioned_or("k!"),
            owner_ids=self.owner_ids,
        )

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

        cogs = (
            "jishaku",
            "cogs.music",
            "cogs.tags",
            "cogs.fun",
            "cogs.owner",
            "cogs.misc",
            "cogs.economy",
            "cogs.welcome",
        )

        for cog in cogs:
            await self.load_extension(cog)

        await self.tree.sync()
        await self.run_async(utils.update_readme_commands)

        self.app = app.app
        app.app.bot = self
        runner = aiohttp.web.AppRunner(self.app)
        await runner.setup()
        site = aiohttp.web.TCPSite(runner, '0.0.0.0', 30106)
        await site.start()

    async def on_ready(self) -> None:
        print(self.user, "is ready!", end=" ")
        dt = datetime.datetime.now()
        print("Current time and date are", dt.strftime("%-Hh:%-Mm:%-Ss and %-d/%-m/%Y"))
        self.vote_channel = await self.fetch_channel(880294980076326933)

    async def on_guild_join(self, guild):
        try:
            channel = guild.system_channel
            if channel is not None:
                joinEm=discord.Embed(title="Thank you for adding me to the server!", description="", colour=0xf47fff)
                joinEm.set_thumbnail(url = "https://cdn.discordapp.com/avatars/864785515978031115/230913aa17624128fba8fc09504a86cb.png")
                joinEm.set_footer(icon_url="https://cdn.discordapp.com/avatars/859996173943177226/e1c7916a0597d2fe6453e03559b825ac.png", text="With love, farrr#6470")
                await channel.send(embed=joinEm)
        except:
            pass

    async def on_error(self, event, *args, **kwargs) -> None:
        err = traceback.format_exc()
        print(f"An error ocurred in event `{event}`\n", err)

    async def on_message(self, message: discord.Message) -> None:
        if not message.author.bot:
            print(message.author, ":", message.content)
            await self.process_commands(message)

    async def vote(self, dat, y):
        await self.wait_until_ready()
        t = dat['type']
        u = dat['user']
        c = self.vote_channel
        if y == 0:
            em = discord.Embed(colour = 0xf47fff)
            if t == 'upvote':
                em.title = "New vote!"
                em.description = f"Thank you for voting <@{u}>!"
            elif t == 'test':
                em.title = "Test vote!"
            await c.send(embed = em)
        elif y == 1:
            pass


    async def run_async(self, func, *args, **kwargs) -> typing.Any:
        async with self:
            return await self.loop.run_in_executor(
                None,
                functools.partial(
                    func, *args, **kwargs,
                )
            )

    def run(self) -> Unreal:
        return super().run(self.token)

bot = Unreal()

@bot.hybrid_command(name="ping")
async def ping_cmd(ctx: commands.Context): 
    """Get the bot's latency!"""
    l = bot.latency
    ft = time.perf_counter()
    om = await ctx.send("Pong!")
    st = time.perf_counter()
    embed = discord.Embed(
        title = "Pong!",
        description = f"""🏓 Websocket Ping: **`{round(l*1000, 2)}`ms**
        🏓 API latency: **`{round((st-ft)*1000, 2)}`ms**
        """,
    )
    await om.edit(content = None, embed = embed)

run = lambda: bot.run()
