
import discord
import typing
import functools
from discord import app_commands

HELP_INFO: typing.Dict[str, typing.Dict[str, str]] = {}

def help_desc(info: typing.Dict):
    if info['cog'] in HELP_INFO:
        HELP_INFO[info.pop('cog')][info.pop('name')] = info
    else:
        HELP_INFO[info.pop('cog')] = {info.pop('name'): info}
    return lambda func: func

app_commands.help_desc = help_desc


def update_readme_commands():
    cas = '# Chuck\n<p align="center">\n  <img alt="Our Bot!" src="https://cdn.discordapp.com/emojis/861955812854202378.png">\n</p>\n\n## About ツ>\n- Chuck is a bot developed by [Farrr](https://github.com/unrealfar), using [Discord.py](https://discord.gg/dpy) library in Python!\n- Chuck was developed in order to make Discord a lot more fun, with various features unique features.\n- Chuck is as of now in v3.0.0\n- We hope to add a lot more features to the bot in the upcoming future!\n- Stay safe!\n- Chuck has completely migrated to slashed commands.\n\n## Commands:\n'
    for c, cmds in HELP_INFO.items():
        cs = '### ' + c.capitalize() + '\n'
        for name, cmd in cmds.items():
            cs += f"- **{name}**: {cmd['description']}\n    - Syntax: `{cmd['syntax']}`\n    - Usage: `{cmd['example']}`\n"
        cas += cs + '\n'
    with open("README.md", 'w') as rf:
        rf.write(cas)
