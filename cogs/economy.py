from discord.ext import commands
import discord

import asyncio
import random
import json
import os

if os.path.exists('amounts.json'):
    with open('amounts.json', 'r') as file:
        amounts = json.load(file)
else:
    amounts = {}

class Economy(commands.Cog):
    """Economy system"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global amounts
        try:
            with open('amounts.json') as f:
                amounts = json.load(f)
        except FileNotFoundError:
            print("Could not load amounts.json")
            amounts = {}
        await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"over {len(self.bot.guilds)} servers"))
        print(f"{self.bot.user} is ready")
            
    @commands.command(aliases = ["bal"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def balance(self, ctx):
        id = str(ctx.message.author.id)
        if id in amounts:
            balEm = discord.Embed(title = f"{ctx.author.name}' s balance")
            balEm.add_field(name = "Wallet", value = "{}".format(amounts[id]))
            await ctx.send(embed = balEm)
        else:
            await ctx.send("You do not have an account! Please use `<prefix>register`!")
            
    @commands.command()
    @commands.cooldown(1, 10000, commands.BucketType.user)
    async def register(self, ctx):
        id = f"{ctx.author.id}"
        if id not in amounts:
            amounts[id] = 100
            await ctx.send("You are now registered")
            _save()
        else:
            await ctx.send("You already have an account!")
            
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def transfer(self, ctx, other: discord.Member, amount: int):
        primary_id = str(ctx.message.author.id)
        other_id = str(other.id)
        if primary_id not in amounts:
            await ctx.send("You do not have an account! Please use `<prefix>register`!")
            return
        if primary_id == other_id:
            await ctx.send("Bruh, you can't transfer money to yourself!")
            return
        if other_id not in amounts:
            await ctx.send("The other party does not have an account")
            return
        if amounts[primary_id] < amount:
            await ctx.send("You cannot afford this transfer")
            return
        if amount <= 0:
            await ctx.send("You have to add money first")
            return
        else:
            msg = await ctx.send(f"Are you sure that you want to transfer {amount} to {other}")
            await msg.add_reaction("✅")
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "✅"
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await channel.send("Cancelled")
                return
            else:
                await ctx.send(f"Transferred {amount} to {other.mention}")
                amounts[primary_id] -= amount
                amounts[other_id] += amount
                msg = await ctx.send("Transferring!")
                await msg.delete()
                transferEm = discord.Embed(title = "Successful transfer!", description = f"Transfer between {ctx.author.mention} and {other.mention}!")
                transferEm.add_field(name = "\u200b", value = f"{ctx.author.name} gave {other.name} **{amount} coins!**")
                await ctx.send(embed = transferEm)
                _save()
            
    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def beg(self, ctx):
        earnings = random.randrange(-100, 1001)
        userid = str(ctx.author.id)
        amounts[f"{userid}"] += earnings
        if f"{userid}" not in amounts:
            await ctx.send("Please register yourself with `<prefix>register`!")
        if earnings == 0:
            responses = ["Get lost, beggar!", "Don't you know that begging is against the rules?!"]
        elif earnings < 0:
            responses = [f"The guy whom you asked the money robbed **{-earnings}** from you"]
        else:
            responses = [f"A kind stranger gave you **{earnings}** coins!", f"A rich guy gave you **{earnings}** coins!"]
        response = random.choice(responses)
        await ctx.send(f"{response}")
        _save()

def _save():
    with open('amounts.json', 'w+') as f:
        json.dump(amounts, f)
        
def setup(bot):
    bot.add_cog(Economy(bot))
