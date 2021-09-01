from discord.ext import commands
import discord

import json
import os

if os.path.exists('amounts.json'):
    with open('amounts.json', 'r') as file:
        amounts = json.load(file)
else:
    amounts = {}

class Events(commands.Cog):
    """Events"""

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
    async def balance(self, ctx):
        id = str(ctx.message.author.id)
        if id in amounts:
            balEm = discord.Embed(title = f"{ctx.author.name}' s balance")
            balEm.add_field(name = "Wallet", value = "{}".format(amounts[id]))
            await ctx.send(embed = balEm)
        else:
            await ctx.send("You do not have an account! Please use `<prefix>register`")
            
    @commands.command()
    async def register(self, ctx):
        id = str(ctx.message.author.id)
        if id not in amounts:
            amounts[id] = 100
            await ctx.send("You are now registered")
            _save()
        else:
            await ctx.send("You already have an account!")
            
    @commands.command()
    async def transfer(self, ctx, amount: int, other: discord.Member):
        primary_id = str(ctx.message.author.id)
        other_id = str(other.id)
        if primary_id not in amounts:
            await ctx.send("You do not have an account! Please use `<prefix>register`")
        elif other_id not in amounts:
            await ctx.send("The other party does not have an account")
        elif amounts[primary_id] < amount:
            await ctx.send("You cannot afford this transfer")
        elif amounts[primary_id] <= 0:
            await ctx.send("You have to add money first")
        else:
            amounts[primary_id] -= amount
            amounts[other_id] += amount
            transferEm = discord.Embed(title = "Successful transfer!", description = f"Transfer between {ctx.author.mention} and {other.mention}!")
            transferEm.add_field(name = "\u200b", value = f"{ctx.author.name} gave {other.name} **{amount} coins!**")
            await ctx.send("Transaction complete")
        _save()
            
def _save():
    with open('amounts.json', 'w+') as f:
        json.dump(amounts, f)
        
def setup(bot):
    bot.add_cog(Events(bot))
