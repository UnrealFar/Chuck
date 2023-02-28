from discord.ext import commands
from discord import app_commands
import discord
import utils

select_options = [discord.SelectOption(label='Home')] + [
    discord.SelectOption(label=cog.capitalize()) for cog in utils.HELP_INFO
    ]

class HelpMenu(discord.ui.View):
    def __init__(self, cmd):
        super().__init__(timeout=100)
        self.cmd = cmd


    @discord.ui.select(
        placeholder = "Select Command Category",
        min_values = 1, max_values = 1,
        options = select_options,
    )
    async def callback(self, interaction, select):
        cog = select.values[0]
        await self.cmd.update_page(interaction, cog.lower())
        await interaction.response.edit_message(embed = self.cmd.embed, view = self)

class HelpCommand:
    cache = utils.HELP_INFO

    def __init__(
        self,
        bot: commands.Bot,
        interaction: discord.Interaction
    ):
        self.bot = bot
        self.interaction = interaction
        self._mp = None
        self.view = HelpMenu(self)
        self.embed = em = discord.Embed(
            title = "Help Menu [Home]",
            description = self.main_page()
        )
        em.set_author(name = f"Requested by {interaction.user}", icon_url = interaction.user.display_avatar.url)
        em.set_thumbnail(url = bot.user.avatar.url)

    async def update_page(self, i, cog):
        if cog != 'home':
            desc = ""
            self.embed.title = f'Help Menu [{cog.capitalize()}]'
            for n, cmd in utils.HELP_INFO[cog].items():
                desc += f"**{n.upper()}**\n> {cmd['description']}\n> __Syntax__: `{cmd['syntax']}`\n\n"
        else:
            desc = self.main_page()
        self.embed.description = desc


    def main_page(self):
        if self._mp:
            return self._mp
        return """
        Welcome to the Help Menu!

        Use the dropdown menu below to select the category of the command you wish to get help for.
        """


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.name = "Help"

    @app_commands.command(name = "help")
    async def help_cmd(self, i: discord.Interaction):
        h = HelpCommand(self.bot, i)
        await i.response.send_message(embed = h.embed, view = h.view)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))

