import aiohttp
import typing
import discord

from discord.ext import commands
from discord import app_commands
from bot import Unreal

class Fun(commands.Cog):
    bot: Unreal
    session: aiohttp.ClientSession

    api_urls = {
        "plane": "https://planeapi.apiworks.tech",
        "rock": "https://rockapi.apiworks.tech"
    }

    def __init__(self, bot: Unreal):
        self.bot = bot

    async def cog_load(self):
        self.session = self.bot.session

    @app_commands.command(name = "getrock")
    @app_commands.help_desc(
        {
            "name": "getrock",
            "description": "Get a rock from the Rock API(by Conos). Search for one or get a random rock.",
            "cog": "fun",
            "syntax": "/getrock <rock>",
            "example": "/getrock glow rock"
        }
    )
    @app_commands.describe(
        query = "The rock to search for!"
    )
    async def get_rock(
        self,
        i: discord.Interaction,
        query: typing.Optional[str] = None,
    ):
        """Get rocks from the rock api!
        """
        await i.response.defer()
        async with self.session.get(
            self.api_urls['rock'] + '/rock/' + str(query or 'random')
        ) as d:
            if d.status == 400:
                return await i.edit_original_message(content = "The rock doesn't exist!")
            elif d.status != 200:
                return await i.edit_original_message(content = "Uh oh! An error occured!")
            rok = await d.json()
            em = discord.Embed(
                title = rok['name'],
                description = rok['description']
            )
            em.set_image(url = rok['image'])
            em.set_footer(text = 'With ❤️, Rock API')
            await i.edit_original_message(embed = em)

    @app_commands.command(name = "getplane")
    @app_commands.help_desc(
        {
            "name": "getplane",
            "description": "Get a random plane from the Plane API(by Lexionas)",
            "cog": "fun",
            "syntax": "/getplane", "example": "/syntax"
        }
    )
    async def get_plane(
        self,
        i: discord.Interaction
    ):
        """Get planes from the plane api!
        """
        await i.response.defer()
        async with self.session.get(
            self.api_urls['plane'] + '/planes/random'
        ) as d:
            if d.status != 200:
                return await i.edit_original_message(content = f"Uh oh! PlaneAPI responded with status {d.status}. Please wait while this endpoint is fixed!")
            plane = await d.json()
            em = discord.Embed(
                title = f'#{plane["ids"]} {plane["name"]}',
                description = plane['description'],
                colour = discord.Colour.blue(),
            )
            em.add_field(name = 'Price', value = plane['price'])
            em.add_field(name = 'MTOW', value = plane['mtow'])
            em.add_field(name = 'Length', value = plane['length'])
            em.add_field(name = 'Wingspan', value = plane['wingspan'])
            em.set_image(url = plane['image'])
            em.set_footer(text = 'With ❤️, Plane API')
            await i.edit_original_message(embed = em)

async def setup(bot: Unreal):
    await bot.add_cog(Fun(bot))
