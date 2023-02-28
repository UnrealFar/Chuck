import typing


import discord
import aiosqlite
from discord.ext import commands
from discord import app_commands
from bot import Unreal


class EconomyCog(commands.Cog):
    name = "Economy"
    bot: Unreal
    eco = app_commands.Group(
        name="economy", description="Commands related to economy system."
    )

    def __init__(self, bot: Unreal):
        self.bot = bot

    async def cog_load(self):
        self.db = db = await aiosqlite.connect("db/economy.sqlite")
        async with db.execute(
            """CREATE TABLE IF NOT EXISTS economy
            (user_id TEXT PRIMARY KEY, coins BIGINT DEFAULT 100, cash BIGINT DEFAULT 0)
            """
        ):
            await db.commit()

    async def _create_account(self, user_id):
        try:
            async with self.db.execute(
                """INSERT INTO economy (user_id)
                VALUES (?)
                """,
                (str(user_id),),
            ):
                await self.db.commit()
            return True
        except:
            return False

    async def _fetch_account(self, user_id):
        async with self.db.execute(
            """SELECT coins, cash FROM economy WHERE user_id = ?
            """,
            (str(user_id),),
        ) as cur:
            return await cur.fetchone()

    async def _add_bal(self, user_id, coins=0, cash=0):
        try:
            async with self.db.execute(
                f"""UPDATE economy
                SET coins = coins + {coins}, cash = cash + {cash}
                WHERE user_id = {str(user_id)}
                """
            ):
                await self.db.commit()
            return False
        except:
            return True

    @eco.command(
        name="register",
    )
    async def register_cmd(self, i: discord.Interaction) -> None:
        """Register yourself to the Chuck Economy System!"""
        uid = i.user.id
        _ch = await self._fetch_account(uid)
        if _ch:
            await i.response.send_message("You already have an account!")
        else:
            await self._create_account(uid)
            em = discord.Embed(
                title="Welcome to Chuck Economy System!", colour=discord.Colour.gold()
            )
            await i.response.send_message(embed=em)


async def setup(bot: Unreal):
    await bot.add_cog(EconomyCog(bot))
