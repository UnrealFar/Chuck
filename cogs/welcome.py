from __future__ import annotations

import aiosqlite
import orjson
import discord
from discord.ext import commands
from discord import app_commands, ui
from bot import Unreal


def propint(d: int):
    d = str(d)
    if d.endswith("1"):
        return d + "st"
    elif d.endswith("2"):
        return d + "nd"
    elif d.endswith("3"):
        return d + "rd"
    return d + "th"


class WSetupM(discord.ui.Modal, title="Welcome Setup"):
    ctx: commands.Context

    ch = ui.TextInput(
        label="Channel ID",
    )
    msg = ui.TextInput(
        label="Welcome Message", style=discord.TextStyle.paragraph, required=False
    )
    emb = ui.TextInput(
        label="Welcome Embed(json format)",
        style=discord.TextStyle.paragraph,
        required=False,
    )

    def __init__(self, cog: WelcomeCog, ctx: commands.Context):
        self.ctx = ctx
        self.cog = cog
        super().__init__()

    async def on_submit(self, i: discord.Interaction):
        d = {}
        if self.msg.value:
            d["msg"] = self.msg.value
        if self.emb.value:
            try:
                e = orjson.loads(self.emb.value)
                for t in e:
                    if t not in ("title", "description", "colour"):
                        e.pop(t, None)
                d["emb"] = orjson.dumps(e).decode()
            except:
                d["emb"] = {}
        d["ch_id"] = int(self.ch.value)
        db = self.cog.db
        async with db.execute(
            """SELECT (ch_id)
            FROM welcome
            WHERE g_id = ?
            """,
            (i.guild_id,),
        ) as fcur:
            if await fcur.fetchone():
                async with db.execute(
                    f"""UPDATE welcome
                    SET msg = ?, emb = ?, ch_id = ?
                    WHERE g_id = {i.guild_id}
                    """,
                    (d["msg"], d["emb"], d["ch_id"]),
                ):
                    await db.commit()
            else:
                async with db.execute(
                    """INSERT INTO welcome
                    (ch_id, g_id, msg, emb)
                    VALUES (?, ?, ?, ?)
                    """,
                    (d["ch_id"], i.guild_id, d["msg"], d["emb"]),
                ):
                    await db.commit()
        await i.response.send_message(
            "You have successfully set up the welcome system!"
        )


class WelcomeCog(commands.Cog, name="Welcome"):
    db: aiosqlite.Connection

    def __init__(self, bot: Unreal):
        self.bot: Unreal = bot

    async def cog_load(self):
        self.db = db = await aiosqlite.connect("db/welcome.sqlite")
        async with db.execute(
            """CREATE TABLE IF NOT EXISTS welcome
            (msg TEXT, emb TEXT, ch_id BIGINT, g_id BIGINT)
            """
        ):
            await db.commit()

    def format_m(self, s: str, m: discord.Member) -> str:
        return s.format(
            name=m.name,
            discrim=m.discriminator,
            mention=m.mention,
            server=m.guild.name,
            members=len(m.guild.members),
            propint=propint,
        )

    @commands.Cog.listener()
    async def on_member_join(self, m: discord.Member):
        async with self.db.execute(
            """SELECT msg, emb, ch_id
            FROM welcome
            WHERE g_id = ?
            """,
            (m.guild.id,),
        ) as cur:
            d = await cur.fetchone()
            if not d:
                return
            ts = {}
            c = d[0]
            if c:
                ts["content"] = self.format_m(c, m)
            emb = d[1]
            emb = orjson.loads(emb)
            print(emb)
            try:
                cl = int(emb.get("colour"))
            except:
                cl = getattr(discord.Colour, emb["colour"], discord.Colour.random)()
            if len(emb) > 0:
                ts["embed"] = discord.Embed(
                    title=self.format_m(emb.get("title"), m),
                    description=self.format_m(emb.get("description"), m),
                    colour=cl,
                )
            await m.guild.get_channel(d[2]).send(**ts)

    @commands.hybrid_group(name="welcome")
    async def welc(self, ctx: commands.Context):
        ...

    @app_commands.help_desc(
        {
            "name": "welcome setup",
            "description": "Set up welcoming system for your server!",
            "cog": "welcome",
            "syntax": "/welcome setup",
            "example": "/welcome setup",
        }
    )
    @welc.command(name="setup")
    async def welsetup(self, ctx: commands.Context):
        """Set up the Chuck Welcome system in your server!"""
        i = ctx.interaction
        if not i:
            await ctx.send("Please use `/welcome setup` to setup the welcome system!")
        await i.response.send_modal(WSetupM(self, ctx))


async def setup(bot: Unreal):
    await bot.add_cog(WelcomeCog(bot))
