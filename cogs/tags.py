from __future__ import annotations

import typing
import traceback
import aiosqlite

import discord
import jishaku
from discord.ext import commands
from discord import app_commands
from discord import ui
from bot import Unreal


class TCreateM(ui.Modal, title="Create a tag"):
    name = ui.TextInput(label="Name of the tag")
    content = ui.TextInput(
        label="Content of the tag", style=discord.TextStyle.paragraph
    )

    def __init__(self, tc: Tags, g_id: int, a_id: int):
        super().__init__()
        self.tc: Tags = tc
        self.g_id: int = g_id
        self.a_id: int = a_id

    async def on_submit(self, i: discord.Interaction):
        name = str(self.name).lower()
        content = str(self.content)
        db = self.tc.db
        async with db.execute(
            """SELECT (name)
            FROM tags
            WHERE g_id = ? AND name = ?
            """,
            (str(self.g_id), name),
        ) as cur:
            if await cur.fetchone() != None:
                return await i.response.send_message(
                    f"There already exists a tag called {name} in this server!"
                )
        async with db.execute(
            """INSERT INTO tags
            (g_id, a_id, name, content, created)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(self.g_id), str(self.a_id), name, content, discord.utils.utcnow()),
        ):
            await db.commit()
            await i.response.send_message(f"Created tag **{name}**!")


class TEditM(ui.Modal, title="Edit a tag"):
    name = ui.TextInput(label="Name of tag")
    content = ui.TextInput(label="New content", style=discord.TextStyle.paragraph)

    def __init__(self, tc: Tags, g_id: int, a_id: int):
        super().__init__()
        self.tc: Tags = tc
        self.g_id: int = g_id
        self.a_id: int = a_id

    async def on_submit(self, i: discord.Interaction):
        name = str(self.name).lower()
        content = str(self.content)
        db = self.tc.db
        async with db.execute(
            """SELECT a_id
            FROM tags
            WHERE g_id = ? AND name = ?
            """,
            (self.g_id, name),
        ) as cur:
            cd = await cur.fetchone()
            if cd == None:
                return await i.response.send_message(
                    f"There exists no tag called {name} in this server!"
                )
            if int(cd[0]) != i.user.id:
                return await i.response.send_message(
                    "Only the owner of the tag can edit a tag!"
                )
        async with db.execute(
            """UPDATE tags
            SET content = ?, created = ?
            WHERE g_id = ? AND name = ?
            """,
            (
                content,
                discord.utils.utcnow(),
                self.g_id,
                name,
            ),
        ):
            await db.commit()
            await i.response.send_message(f"Edited tag **{name}**!")


class Tags(commands.Cog):
    name = "Tags"
    db: aiosqlite.Connection

    tag_group = app_commands.Group(
        name="tag", description="Commands related to tag system."
    )

    def __init__(self, bot: Unreal):
        self.bot: Unreal = bot

    async def cog_load(self):
        self.db = db = await aiosqlite.connect("db/tags.sqlite")
        async with db.execute(
            """CREATE TABLE IF NOT EXISTS tags
            (g_id TEXT, a_id TEXT, name TEXT, content LONGTEXT, created DATETIME)
            """
        ):
            await db.commit()

    @tag_group.command(name="view", example='/tag view chuck')
    @app_commands.describe(
        name="The name of tag to search for!",
        raw="Whether the bot should send the raw content of the tag!",
    )
    async def tcmd(
        self,
        i: discord.Interaction,
        name: str,
        raw: bool = False,
    ):
        """View a tag"""
        async with self.db.execute(
            """SELECT content
            FROM tags
            WHERE g_id = ? AND name = ?
            """,
            (str(i.guild_id), name.lower()),
        ) as cur:
            td = await cur.fetchone()
            if not td:
                return await i.response.send_message(
                    "A tag with that name does not exist!"
                )
            await i.response.send_message(
                td[0] if raw is False else f"```\n{td[0]}\n```"
            )

    @tag_group.command(name="list")
    async def tlist(
        self,
        i: discord.Interaction,
    ):
        """View all tags in this server!"""
        pag = commands.Paginator("", "")
        async with self.db.execute(
            """SELECT name, a_id
            FROM tags
            WHERE g_id = ?""",
            (str(i.guild.id),),
        ) as cur:
            l = await cur.fetchall()
        for t in l:
            pag.add_line(f"**`{t[0]}`**: <@{t[1]}>")
        emb = discord.Embed(
            title="Tag List",
            description=(pag.pages[0] if len(pag) > 1 else "No songs in queue!"),
            colour=discord.Colour.gold(),
        )
        emb.set_footer(
            text=f"Requested by {i.user}", icon_url=i.user.display_avatar.url
        )
        embp = jishaku.paginators.PaginatorEmbedInterface(
            self.bot,
            pag,
            embed=emb,
            owner=i.user,
        )
        await i.response.send_message(embed=emb, view=embp)

    @tag_group.command(name="create")
    async def tcreate(
        self,
        i: discord.Interaction,
    ):
        """Create a tag with ui interface."""
        if not i.guild:
            return await i.response.send_message(
                "You have to be in a guild to run this command!"
            )
        await i.response.send_modal(TCreateM(self, i.guild_id, i.user.id))

    @tag_group.command(name="edit")
    async def tedit(
        self,
        i: discord.Interaction,
    ):
        """Edit a tag with ui interface."""
        if not i.guild:
            return await i.response.send_message(
                "You have to be in a guild to run this command!"
            )
        await i.response.send_modal(TEditM(self, i.guild_id, i.user.id))

    @tag_group.command(name="delete", example='/delete tag chuck')
    @app_commands.describe(name="Name of tag to delete.")
    async def tdelete(self, i: discord.Interaction, name: str):
        """Delete a tag"""
        name = name.lower()
        async with self.db.execute(
            """SELECT a_id
            FROM tags
            WHERE g_id = ? AND name = ?
            """,
            (
                str(i.guild_id),
                name,
            ),
        ) as cur:
            d = await cur.fetchone()
            if not d:
                return await i.response.send_message(
                    "A tag with this name does not exist!"
                )
            if int(d[0]) != i.user.id or not i.user.guild_permissions.administrator:
                return await i.response.send_message(
                    "You cannot delete this tag as you are neither its owner or a guild administrator!"
                )
        async with self.db.execute(
            """DELETE FROM tags
            WHERE g_id = ? AND name = ?
            """,
            (
                str(i.guild_id),
                name,
            ),
        ) as cur:
            await self.db.commit()
            await i.response.send_message("Successfully deleted the tag!")


async def setup(bot: Unreal):
    await bot.add_cog(Tags(bot))
