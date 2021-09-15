from discord.ext import commands
import discord
import time
import asyncio

class Misc(commands.Cog):
    """Miscellaneous commands that do not fit anywhere else"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        """Sends a suggestion to the server!"""
        suggestEm = discord.Embed(description = f"{ctx.author.mention}", colour = ctx.author.colour)
        suggestEm.add_field(name = "NEW SUGGESTION", value = f"{suggestion}")
        suggestEm.set_thumbnail(url = ctx.author.display_avatar.url)
        suggestEm.set_footer(text = f"Suggestion made in {ctx.channel}")
        suggestChannel = discord.utils.get(ctx.guild.text_channels, name = "suggestions")
        if suggestChannel:
            await ctx.send(f"Suggestion made successfully in {suggestChannel.mention}!")
            sentMsg = await suggestChannel.send(embed = suggestEm)
            await sentMsg.add_reaction("👍")
            await sentMsg.add_reaction("👎")
        else:
            overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)}
            await ctx.guild.create_text_channel("suggestions", overwrites=overwrites)
            suggestChannel = discord.utils.get(ctx.guild.text_channels, name = "suggestions")
            await ctx.send(f"Created suggestion channel {suggestChannel.mention}! Please do not change the name of this channel!")
            sentMsg = await suggestChannel.send(embed = suggestEm)
            await sentMsg.add_reaction("👍")
            await sentMsg.add_reaction("👎")

    @suggest.error
    async def suggest_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Chill mate! You're on a cooldown for this command!")

    #@commands.command()
    #@commands.cooldown(1, 5, commands.BucketType.guild)
    #async def ping(ctx: commands.Context):
        #"""Shows the bot ping"""
        #start_time = time.time()
        #msg = await ctx.send("Testing ping...")
        #end_time = time.time()
        #bot_ping = round(self.bot.latency * 1000)
        #api_ping = round((end_time - start_time) * 1000)
        #await msg.delete()
        #if bot_ping <= 100:
            #bpsignal = "<:online:874181086312280064>"
        #elif bot_ping >=101:
            #bpsignal = "<:idle:874181495886065664>"
        #elif bot_ping>=300:
            #bpsignal = "<:dnd:874181456472182864>"
        #if api_ping <= 100:
            #apisignal = "<:online:874181086312280064>"
        #elif api_ping >=101:
            #apisignal = "<:idle:874181495886065664>"
        #elif api_ping >= 300:
            #apisignal = "<:dnd:874181456472182864>"
        #pingEm = discord.Embed(title="Pong!", description="", colour = discord.Color.blurple())
        #pingEm.add_field(name="Bot Ping", value=f"{bpsignal}  {bot_ping}ms", inline=False)
        #pingEm.add_field(name="API Ping", value=f"{apisignal} {api_ping}ms", inline=False)
        #await ctx.send(embed = pingEm)
  
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def invite(self, ctx):
        """Shows the invite links for the bot"""
        embed=discord.Embed(title="Invite")
        embed.add_field(name="Invite me to your server", value="[Bot Invite link](https://top.gg/bot/864785515978031115/invite)", inline=False)
        embed.add_field(name="Join the support server", value="[Server link](https://discord.gg/4RdYvsE7Jy)")
        await ctx.send(embed=embed)

    @commands.command(aliases=["server-info"])
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def serverinfo(self, ctx):
        """Shows info about a guild!"""
        serverinvite = await ctx.channel.create_invite(max_age = 600, unique = False, reason = "Used for Server Info command")
        embed = discord.Embed(title = 'Server Info', colour = discord.Colour.red())
        embed.add_field(name = "Server Name", value = f"{ctx.guild.name}", inline = True)
        embed.add_field(name = "Member Count", value = ctx.guild.member_count, inline = True)
        embed.add_field(name = "Owner", value = ctx.guild.owner, inline = True)
        try:
            embed.add_field(name = "Invite link", value = f"[Invite link]({serverinvite})")
        except:
            pass
        embed.add_field(name = "Server ID", value = ctx.guild.id, inline = True)
        embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command(aliases=['userinfo'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def whois(self, ctx, member: discord.Member = None):
        """Show information about a specified user"""
        if member == None:
            member = ctx.author
        embed = discord.Embed(title=f"User Info - {member}", timestamp=ctx.message.created_at, colour = discord.Colour.red())
        embed.add_field(name="Display Name", value = member.display_name)
        embed.add_field(name = "ID" , value = member.id , inline = False)
        if isinstance(member, discord.Member):
            embed.add_field(name = "Joined This Server" , value = member.joined_at.strftime("%a, %#d %B %Y") , inline = False)
        else:
            embed.add_field(name = "In this server?", value = "No", inline =False)
        embed.add_field(name = "Joined Discord" , value = member.created_at.strftime("%a, %#d %B %Y") , inline = False)
        embed.set_thumbnail(url = member.display_avatar.url)
        embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def vote(self, ctx):
        """Shows the top.gg vote link for Chuck"""
        voteEm = discord.Embed(title = "Vote for Chuck", description = "", colour = discord.Colour.gold())
        voteEm.add_field(name = "Vote on Top.gg", value = "[Vote](https://top.gg/bot/864785515978031115/vote)")
        await ctx.send(embed = voteEm)
        
    @commands.command(aliases=["guildcount"])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def servercount(self, ctx):
        """Shows the amount of servers the bot is in"""
        await ctx.send( f"I'm in ***{len(self.bot.guilds)}*** servers!")

def setup(bot):
    bot.add_cog(Misc(bot))
