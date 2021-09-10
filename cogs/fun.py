from discord.ext import commands
import discord
import random
import asyncio

class Fun(commands.Cog):
    """Fun to use commands!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot == False:
            logChannel = discord.utils.get(message.guild.text_channels, name = "log")
            logEm = discord.Embed(title = "Message deleted", description = f"In {message.channel.mention}")
            logEm.add_field(name = f"Message sent by {message.author}", value = f"{message.content}")
            logEm.set_thumbnail(url = message.author.display_avatar.url)
            if logChannel:
                try:
                    await logChannel.send(embed = logEm)
                except:
                    pass
            elif not logChannel:
                try:
                    overwrites = {message.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False)}
                    logChannel = await message.guild.create_text_channel("log", overwrites=overwrites)
                    logChannel = discord.utils.get(message.guild.text_channels, name = "log")
                    await logChannel.send(embed = logEm)
                except:
                    pass

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.channel)
    async def say(self, ctx, *, message=None):
        """The bot says a message for you"""
        if message == None:
            await ctx.send("You must provide a value to say!")
        else:
            try:
                await ctx.message.delete()
            except:
                pass
            await ctx.send(message)
    
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def embed(self, ctx, *, message=None):
        """The bot embeds a message for you!"""
        if message == None:
            await ctx.send("You must provide a value to say!") 
        else:
            try:
                await ctx.message.delete()
            except:
                pass
            sayEmbed = discord.Embed(title = f'{ctx.author.name} says:', colour = discord.Colour.red())
            sayEmbed.add_field(name = 'Message',value = message)
            await ctx.send(embed = sayEmbed)

    @commands.command(aliases=['av'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx, member : discord.Member = None):
        """Shows the avatar image of a user!"""
        if member == None:
            member = ctx.author
        memberAvatar = member.avatar.url
        embed = discord.Embed(title = f"{member.name}'s avatar")
        embed.set_image(url = memberAvatar)
        await ctx.send(embed = embed)

    @commands.command(aliases=['8ball','8b'])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def eightball(self, ctx, *, question):
        """Ask the 8ball a question"""
        responses = ['Hell no.', 'Prolly not.', 'Idk bro.', 'Prolly.', 'Hell yeah my dude.', 'It is certain.', 'It is decidedly so.', 'Without a Doubt.', 'Yes - Definitaly.', 'You may rely on it.', 'As i see it, Yes.', 'Most Likely.', 'Outlook Good.', 'Yes', 'No!', 'Signs a point to Yes!', 'Reply Hazy, Try again.', 
'IDK but you should Definitely vote for this bot on Top.gg', 'Better not tell you know.', 'Cannot predict now.', 'Concentrate and ask again.', 'Dont Count on it.', 'My reply is No.', 'My sources say No.', 'Outlook not so good.', 'Very Doubtful']
        em = discord.Embed(name=":8ball:", description="", colour=discord.Colour.red())
        em.add_field(name="Question", value=question)
        em.add_field(name="Answer", value=f"{random.choice(responses)}")
        em.set_footer(icon_url = ctx.author.avatar.url, text = f"Requested by {ctx.author.name}")
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Fun(bot))
