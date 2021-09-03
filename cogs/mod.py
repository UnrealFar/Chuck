from discord.ext import commands
from discord.ext.commands import has_permissions
import discord

import asyncio
import json

class Mod(commands.Cog):
    """Commands for moderators"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member:discord.Member, *,reason=None):
        """Kicks a member from the guild"""
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked for: {reason}")

    @commands.command(name="ban")
    @commands.cooldown(2, 15, commands.BucketType.guild)
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member:discord.Member, *,reason=None):
        """Bans a member from the guild"""
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned for: {reason}")

    @commands.command(name="unban")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """Unbans a member from the guild"""
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.channel.send(f"Unbanned: {user.mention}")
    
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        """Mutes the specified user."""
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")
        if not mutedRole:
            mutedRole = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)
        if mutedRole in member.roles:
            await ctx.send("This member has already been muted!")
            return
        embed = discord.Embed(title="Muted", description=f"{member.mention} was muted ", colour=discord.Colour.light_gray())
        embed.add_field(name="reason:", value=reason, inline=False)
        await ctx.send(embed=embed)
        await member.add_roles(mutedRole)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmutes a specified user."""
        mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
        if mutedRole not in member.roles:
            await ctx.send("You can't unmute a person who is not currently muted!")
            return
        await member.remove_roles(mutedRole)
        embed = discord.Embed(title="Unmute", description=f"{ctx.author.mention} unmuted {member.mention}",colour=discord.Colour.light_gray())
        await ctx.send(embed=embed)

    @commands.command(aliases=['clear'])
    @commands.cooldown(2, 15, commands.BucketType.default)
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, amount:int=None):
        """Purges/Clears a certain amount of messages"""
        amount = amount
        if amount == None:
            amount = 1
        if amount >= 501:
            await ctx.send("Maximum purge limit is 500!")
            return
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f"{amount} messages have been cleared")
        await asyncio.sleep(5)
        await msg.delete()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @has_permissions(manage_roles=True)
    async def addrole(self, ctx, member:discord.Member, role:discord.Role):
        """Add roles to a member"""
        if role in member.roles:
            await ctx.send("This member already has this role!")
            return
        await member.add_roles(role)
        await ctx.send(f"Successfully added **{role}** to {member}")

    @commands.command()
    @has_permissions(administrator = True)
    async def nuke(self, ctx, channel: discord.TextChannel = None):
        """Nuke a channel!"""
        if channel == None: 
            await ctx.send("You did not mention a channel!")
            return
        nuke_channel = discord.utils.get(ctx.guild.channels, name=channel.name)
        if nuke_channel is not None:
            new_channel = await nuke_channel.clone(reason="Has been Nuked!")
            await nuke_channel.delete()
            await new_channel.send("THIS CHANNEL HAS BEEN NUKED!")
            await new_channel.send("https://cdn.discordapp.com/attachments/832980836659494944/833749914336493638/boom.gif")
        else:
            await ctx.send(f"No channel named {channel.name} was found!")

def setup(bot):
    bot.add_cog(Mod(bot))
  