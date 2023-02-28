import typing

import jishaku
import discord
import aiosqlite
from discord.ext import commands
from discord import app_commands
from bot import Unreal


class InvitesCog(commands.Cog):
    name = "Invites"
    bot: Unreal

    def __init__(self, bot: Unreal):
        self.bot = bot
        self.cache: typing.Dict[int, typing.Dict[str, discord.Invite]] = {}

    async def cog_load(self):
        ...


    async def cache_guild_invites(self, guild_id) -> typing.Dict[str, discord.Invite]:
        d = self.cache[guild_id] = self.cache.get(guild_id) or {}
        try:
            guild = self.bot.get_guild(guild_id) or await self.bot.fetch_guild(guild_id)
            for invite in await guild.invites():
                d[invite.code] = invite
        except: pass
        return d

    async def fetch_invites(self, member: discord.Member) -> typing.List[discord.Invite]:
        guild_id = member.guild.id
        invites = self.cache.get(guild_id) or await self.cache_guild_invites(guild_id)
        return [i for i in invites.values() if i.inviter.id == member.id]

    async def fetch_inviter(self, invitee: discord.Member):
        guild_id = invitee.guild.id
        self.cache[guild_id] = self.cache.get(guild_id) or await self.cache_guild_invites(guild_id)
        for new_invite in await invitee.guild.invites():
            for cached_invite in self.cache[guild_id].values():
                if new_invite.code == cached_invite.code and new_invite.uses - cached_invite.uses == 1 or cached_invite.revoked:
                    if cached_invite.revoked:
                        self.cache[guild_id].pop(cached_invite.code)
                    elif new_invite.inviter == cached_invite.inviter:
                        self.cache[guild_id][cached_invite.code] = new_invite
                    else:
                        self.cache[guild_id][cached_invite.code].uses += 1
                    return cached_invite.inviter

    @app_commands.command(name = "invites")
    @app_commands.describe(member = "The member whose invites you want to check!", show_invites = "Whether all of the invites created by the member should be shown!")
    async def inv_cmd(self, i: discord.Interaction, member: typing.Optional[discord.Member] = None, show_invites: bool = False):
        """Check the invites a member has."""
        member = member or i.user
        invites = await self.fetch_invites(member)
        invitees = sum([x.uses for x in invites])
        embed = discord.Embed(
            title = f"{member}'s invites'", colour = discord.Colour.gold()
        )
        embed.description=f"You have invited **{invitees}** people to this server!\n"
        if show_invites:
            for inv in invites:
                embed.description+=f"`{inv.code}`: **{inv.uses}** uses\n"
        await i.response.send_message(embed = embed)

async def setup(bot: Unreal):
    await bot.add_cog(InvitesCog(bot))
