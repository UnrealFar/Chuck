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
        embed=discord.Embed(title="Invite Links!", colour = discord.Colour.gold())
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label = 'Invite me to your server!', url = 'https://top.gg/bot/864785515978031115/vote', style = discord.ButtonStyle.url))
        view.add_item(discord.ui.Button(label = 'Join the support server!', url = 'https://discord.gg/4RdYvsE7Jy', style = discord.ButtonStyle.url))
        await ctx.send(embed = embed, view = view)

    @commands.command(aliases=["server-info"])
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def serverinfo(self, ctx):
        """Shows info about a guild!"""
        embed = discord.Embed(title = 'Server Info', colour = discord.Colour.red())
        embed.add_field(name = "Server Name", value = f"{ctx.guild.name}", inline = True)
        embed.add_field(name = "Member Count", value = ctx.guild.member_count, inline = True)
        embed.add_field(name = "Owner", value = ctx.guild.owner, inline = True)
        try:
            serverinvite = await ctx.channel.create_invite(max_age = 600, unique = False, reason = "Used for Server Info command")
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label = 'Server Invite', url = f"{serverinvite}", style = discord.ButtonStyle.url))
        except:
            pass
        embed.add_field(name = "Server ID", value = ctx.guild.id, inline = True)
        embed.set_footer(icon_url = ctx.author.display_avatar.url, text = f"Requested by {ctx.author.name}")
        if not serverinvite:
            await ctx.send(embed = embed)
        else:
            await ctx.send(embed = embed, view = view)

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
    async def vote(self, ctx):
        """Shows the top.gg vote link for Chuck"""
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label = 'Vote on Top.GG', url = 'https://top.gg/bot/864785515978031115/vote', style = discord.ButtonStyle.url))
        view.add_item(discord.ui.Button(label = 'Vote on Discord Boats', url = 'https://discord.boats/bot/864785515978031115/vote', style = discord.ButtonStyle.url))
        view.add_item(discord.ui.Button(label = 'Vote on DisBotList', url = 'https://disbotlist.xyz/bot/864785515978031115/vote', style = discord.ButtonStyle.url))
        voteEm = discord.Embed(title = "Vote for Chuck!", description = "Vote rewards coming soon!", colour = discord.Colour.red())
        await ctx.send(embed = voteEm, view = view)
        
    @commands.command(aliases=["guildcount"])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def servercount(self, ctx):
        """Shows the amount of servers the bot is in"""
        await ctx.send( f"I'm in ***{len(self.bot.guilds)}*** servers!")

def setup(bot):
    bot.add_cog(Misc(bot))
