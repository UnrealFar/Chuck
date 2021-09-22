from discord.ext import commands
from discord.ext.commands import has_permissions
import discord
import asyncio
import json

async def get_prefix(bot, message):
    if message.guild != None:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        return prefixes.get(str(message.guild.id), "c!")
    else:
        return ("c!")

class DurationConverter(commands.Converter):
    async def convert(self, ctx, argument):
        amount = argument[:-1]
        unit = argument[-1]
        if amount.isdigit() and unit in ['s', 'm', 'h', 'd']:
            return(int(amount), unit)
        await ctx.send(commands.BadArgument(message = "Not a valid duration!"))

class Mod(commands.Cog):
    """Commands for moderators"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: commands.MemberConverter, *,reason=None):
        """Kicks a member from the guild"""
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked for: {reason}")

    @commands.command()
    @has_permissions(ban_members = True)
    async def tempban(self, ctx, member: commands.MemberConverter, duration: DurationConverter):
        """Temporarily bans a user from the guild for a given time!"""
        multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        amount, unit = duration
        await ctx.guild.ban(member)
        await ctx.reply(f"**{member}** was banned for **{amount}{unit}** by **{ctx.author}**")
        try:
            await member.send(f"You were temporarily banned from **{ctx.guild.name}** for **{amount}{unit}**")
        except:
            pass
        asyncio.sleep(amount * multiplier[unit])
        await ctx.guild.unban(member)
        await ctx.send(f"**{member}** who was banned through the tempban by **{ctx.author}** was unbanned as the timer is over!")
        try:
            inv = await ctx.channel.creat_invite(reason = f"{ctx.author} was unbanned as they were tempbanned!", unique = False)
            await member.send(f"Yeehaw! You were unbanned from {ctx.guild.name} as your tempban timer is out!\nYou can join back with {inv}")
        except:
            pass

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
        try:
            await ctx.message.delete()
        except:
            pass
        deleted = await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f"{len(deleted)} messages have been cleared")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except:
            pass

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
            nukeEm = discord.Embed(title = "THIS CHANNEL HAS BEEN NUKED!")
            nukeEm.set_image(url = "https://c.tenor.com/Ms3zVqn7qcUAAAAd/nuke-press-the-button.gif")
            nukeEm.set_footer(text = f"Nuked by {ctx.author}", icon_url = f"{ctx.author.display_avatar.url}")
            await new_channel.send(embed = nukeEm)
        else:
            await ctx.send(f"No channel named {channel.name} was found!")

    @commands.command()
    @commands.guild_only()
    async def prefix(self, ctx, prefix = None):
        if prefix == None:
            await ctx.send(f"The prefix for this guild is {await get_prefix()}")
            return
        if ctx.author.guild_permissions.administrator:
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)
            prefixes[str(ctx.guild.id)] = prefix
            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await ctx.send(f"The prefix for this server has been set to **{prefix}**")

def setup(bot):
    bot.add_cog(Mod(bot))
    
