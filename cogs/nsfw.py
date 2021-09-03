from discord.ext import commands, tasks
import discord
import random
import asyncio
import aiohttp

class Nsfw(commands.Cog):
    """Nsfw commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.is_nsfw()
    async def nsfw(self, ctx):
        embed = discord.Embed(title="Here you go!", colour = discord.Colour.red())  
        async with aiohttp.ClientSession() as cs:
            links = ['https://www.reddit.com/r/nsfw/new.json?sort=hot', 'https://www.reddit.com/r/NSFW_GIF/new.json?sort=hot']
            link = random.choice(links)
            async with cs.get(link) as r:
                res = await r.json()
                embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
                embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)
                await ctx.send(embed=embed)
                
    @commands.command(pass_context=True)
    @commands.is_nsfw()
    async def boobs(self, ctx):
        """Shows some boobs."""
        async with aiohttp.ClientSession() as session:
            search = f"http://api.oboobs.ru/boobs/{random.randint(0, 10394)}"
            async with session.get(search) as resp:
                result = await resp.json()
                boob = random.choice(result)
                boob = "http://media.oboobs.ru/{}".format(boob["preview"])
                embed = discord.Embed(title = "Boob!")
                embed.set_image(url = boob)
                embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.display_avatar.url)
                await ctx.send(embed = embed)

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    @commands.is_nsfw()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def autonsfw(self, ctx):
        await ctx.send("Auto NSFW has been enabled in this channel")
        while True:
            async with aiohttp.ClientSession() as session:
                search = [f"http://api.oboobs.ru/boobs/{random.randint(0, 10394)}", f"http://api.obutts.ru/butts/{random.randint(0, 4378)}"]
                search = random.choice(search)
                async with session.get(search) as resp:
                    result = await resp.json()
                    img = random.choice(result)
                    img = "http://media.oboobs.ru/{}".format(img["preview"])
                    embed = discord.Embed(colour = discord.Colour.green())
                    embed.set_image(url = img)
                    embed.set_footer(text = "From the Hidden API")
                    await ctx.send(embed = embed)
                    await asyncio.sleep(10)

def setup(bot):
    bot.add_cog(Nsfw(bot))
