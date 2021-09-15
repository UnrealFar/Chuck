import discord
import os

from discord.ext import commands
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MongoURI = os.getenv("MongoURI")
cluster = MongoClient(MongoURI)
levelling = cluster["USERDATA"]["levels"]

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        stats = levelling.find_one({"id":message.author.id})
        if not message.author.bot:
            if stats == None:
                newuser = {"id":message.author.id, "xp":100}
                levelling.insert_one(newuser)
            else:
                xp = stats["xp"] + 1
                levelling.update_one({"id":message.author.id}, {"$set":{"xp":xp}})
                lvl = 0
                while True:
                    if xp < ((50*(lvl**2))+(50*(lvl-1))):
                        break
                    lvl += 1
                xp -= ((50*((lvl-1)**2))+(50*(lvl-1)))
                if xp == 0:
                    lvlEm = discord.Embed(colour = message.author.colour)
                    lvlEm.add_field(name = "Level up!", value = f"{message.author.mention} has levelled up to **{lvl}**!")
                    try:
                        await message.channel.send(f"Well done {message.author.mention}!")
                        await message.channel.send(embed = lvlEm)
                    except:
                        pass

    @commands.command(aliases = ["level"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rank(self, ctx):
        """Shows your rank card!"""
        stats = levelling.find_one({"id":ctx.author.id})
        if stats is None:
            await ctx.send(f"Send some messages first {ctx.author.mention}")
            return
        else:
            xp = stats["xp"]
            lvl = 0
            rank = 0
            while True:
                if xp < ((50*(lvl**2))+(50*(lvl-1))):
                    break
                lvl += 1
            xp -= ((50*((lvl-1)**2))+(50*(lvl-1)))
            boxes = int((xp/(200*((1/2)*lvl)))*20)
            rankings = levelling.find().sort("xp",-1)
            for x in rankings:
                rank += 1
                if stats["id"] == x["id"]:
                    break
            rankEm = discord.Embed(title = f"RANK CARD", colour = ctx.author.colour)
            rankEm.add_field(name = "Name", value = f"{ctx.author}", inline = True)
            rankEm.add_field(name = "XP", value = f"{xp}/{int(200*((1/2)*lvl))}", inline = True)
            rankEm.add_field(name = "Rank", value = f"#{rank}", inline = True)
            rankEm.add_field(name = "Progress Bar", value = boxes * ":blue_square:" + (20-boxes) * ":red_square:", inline = False)
            rankEm.set_thumbnail(url = ctx.author.display_avatar.url)
            await ctx.send(embed = rankEm)

    @commands.command(aliases = ["lb"])
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def leaderboard(self, ctx):
        """Shows the XP leaderboard of the guild!"""
        rankings = levelling.find().sort("xp",-1)
        i = 1
        lbEm = discord.Embed(title = f"XP Leaderboard of {ctx.guild.name}")
        for x in rankings:
            try:
                temp = ctx.guild.get_member(x["id"])
                tempxp = x["xp"]
                lbEm.add_field(name = f"{i}: {temp.name}", value = f"Total XP: **{tempxp}**", inline = False)
                i += 1
            except:
                pass
            if i == 11:
                break
        try:
            lbEm.set_thumbnail(url = ctx.guild.icon.url)
        except:
            pass
        lbEm.set_footer(text = f"Requsted by {ctx.author}", icon_url = ctx.author.display_avatar.url)
        await ctx.send(embed = lbEm)

def setup(bot):
    bot.add_cog(Leveling(bot))