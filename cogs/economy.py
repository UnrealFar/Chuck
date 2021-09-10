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
    async def balance(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        id = str(member.id)
        if id in amounts:
            balEm = discord.Embed(title = f"{member.name}' s balance")
            balEm.add_field(name = "Wallet", value = f"{amounts[id]}")
            await ctx.send(embed = balEm)
        else:
            await ctx.send("Account doesn't! Please use `<prefix>register`!")

    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Chill mate! You're on a cooldown for this command!")
            
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

    @register.error
    async def register_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            pass
            
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def transfer(self, ctx, other: discord.Member = None, amount: int = None):
        primary_id = str(ctx.message.author.id)
        other_id = str(other.id)
        if other_id == None:
            await ctx.send("You can't transfer money into thin air!")
        if amount == None:
            await ctx.send("Add money first!")
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

    @transfer.error
    async def transfer_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Transferring twice in 10 seconds??? You don't wanna go broke, do you?")
            
    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def beg(self, ctx):
        earnings = random.randrange(-100, 1001)
        userid = str(ctx.author.id)
        amounts[f"{userid}"] += earnings
        if userid not in amounts:
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

    @beg.error
    async def beg_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Eyy you greedy fellow, you can't beg more than once in a minute mate!")

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        salary = random.randrange(-10001, 10001)
        userid = str(ctx.author.id)
        amounts[f"{userid}"] += salary
        if userid not in amounts:
            await ctx.send("Please register first with <prefix>register")
        if salary <= 0:
            responses = [f"You spill milkshake on your boss's new shirt while working as a waiter at a fancy restaurant! Your boss fires you and makes you pay **{-salary}** coins for the shirt!", f"You accidentally hit your leg on the table on fall on your boss's cat while working as a maid and end up hurting the cat's paw! Your boss immediately fires you and makes you pay **{-salary}** coins for hurting his cat"]
        if 0 < salary < 100:
            responses = [f"You work as a maid at a rich guy's house for 100 coins, but he didn't like that you were singing during your work hour, and only gives you **{salary}**"]
        if salary >= 100:
            responses = [f"You work as an accountant at a bank and earn **{salary}** coins!", f"You upload a video of you playing Fortnite and it gets popular and you earn **{salary}** coins from it!"]
        response = random.choice(responses)
        workingEm = discord.Embed(title = "Working...")
        working = await ctx.send(embed = workingEm)
        await asyncio.sleep(3)
        await working.delete()
        workEm = discord.Embed(title = "You have finished working!", description = f"{response}")
        await ctx.send(embed = workEm)
        _save()

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("You can only work once an hour! You don't wanna exhaust yourself, do you?")

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def gamble(self, ctx, money: int):
        userid = str(ctx.author.id)
        gAmt = 1
        if userid not in amounts:
            await ctx.send("Please register yourself with `<prefix>register`!")
            return
        if amounts[userid] < money:
            await ctx.send("You can't afford to gamble this amount!")
            return
        if money > 10000:
            await ctx.send("You can't gamble that much! The limit is 10k!")
            return
        if 0 >= money:
            await ctx.send("You can't gamble thin air!")
        randNum = random.randrange(0, 11)
        if 0 < randNum <= 3:
            gAmt = money
            response = f"{ctx.author.mention} has won! Added {gAmt} to his balance!"
        if 3 < randNum <= 10:
            gAmt = -money
            response = f"{ctx.author.mention} has lost! He lost {-gAmt} coins!"
        procEm = discord.Embed(title = "Gambling...")
        proc = await ctx.send(embed = procEm)
        await asyncio.sleep(3)
        await proc.delete()
        amounts[userid] += gAmt
        gambleEm = discord.Embed(title = "Gambled!", description = f"{ctx.author} has finished gambling")
        gambleEm.add_field(name = "Results", value = response)
        await ctx.send(embed = gambleEm)
        _save()

    @gamble.error
    async def gamble_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("The guard at the casino kicked you out! **'Get lost idiot, u aint allowed to gamble more than once in a minute'**!")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Well u gotta add some money to gamble ¯\_(ツ)_/¯")

    @commands.command()
    @commands.is_owner()
    async def addmoney(self, ctx, member: discord.Member, amt: int):
        id = str(member.id)
        amounts[id] += amt
        _save()
        await ctx.send(f"Added {amt} to {member}'s balance!")

def _save():
    with open('amounts.json', 'w+') as f:
        json.dump(amounts, f)
        
def setup(bot):
    bot.add_cog(Economy(bot))
