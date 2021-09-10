from discord.ext import commands
import discord
import random
import asyncio

class Giveaways(commands.Cog):
    """Giveaways"""

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def gstart(self, ctx):
        await ctx.send("Oooh a giveaway?? Nicee!! So, lets get started! Please answer the questions i ask you within 30 seconds!")
        
        questions = ["Which channel are we doin' this giveaway in?", "How long is the giveaway gonna be? (s|m|h|d)", "Whats the prize gonna be? 👀"]
        answers = []
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        for i in questions:
            await ctx.send(i)
            
            try:
                msg = await self.bot.wait_for("message", timeout = 30.0, check = check)
            except asyncio.TimeoutError:
                await ctx.send("You didn't answer in time! Please be quicker next time!")
                return
            else:
                answers.append(msg.content)

        try:
            c_id = int(answers[0][2:-1])
        except:
            await ctx.send(f"You didn't mention a channel properly! Please mention it in {ctx.channel.mention} format!")
            return
        
        channel = self.bot.get_channel(c_id)
        
        time = convert(answers[1])
        if time == -1:
            await ctx.send("You didn't answer the time with a proper unit. Please use (s|m|h|d) format!")
            return
        elif time == -2:
            await ctx.send("The time must be an integer! Please enter an integer")
            return
        
        prize = answers[2]
        
        await ctx.send(f"The giveaway will be in {channel.mention} and will last for {answers[1]}!")
        
        embed = discord.Embed(title = "Giveaway!", description = f"{prize}", colour = discord.Colour.random())
        embed.add_field(name = "Hosted by:", value = ctx.author.mention)
        embed.set_footer(text = f"Ends {answers[1]} from now!")
        giveaway_msg = await channel.send(embed = embed)
        await giveaway_msg.add_reaction("🎉")
        await asyncio.sleep(time)
        
        new_msg = await channel.fetch_message(giveaway_msg.id)
        users = await new_msg.reactions[0].users().flatten()
        
        winner = random.choice(users)
        await channel.send(f"Congratulations {winner.mention}! You won **{prize}**")

    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def reroll(self, ctx, channel: discord.TextChannel, id):
        try:
            new_msg = await channel.fetch_message(id)
        except:
            await ctx.send("The ID was entered incorrectly!")
            return
        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))
        winner = random.choice(users)
        await channel.send(f"Congratulations {winner.mention}! You are the new winner of the giveaway!")

def convert(time):
    pos = ["s","m","h","d"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    
    unit = time[-1]
    
    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2
    
    return val * time_dict[unit]

def setup(bot):
    bot.add_cog(Giveaways(bot))
