
import discord
import typing
import functools
from discord import app_commands

HELP_INFO = {}

def help_desc(info: typing.Dict):
    if info['cog'] in HELP_INFO:
        HELP_INFO[info.pop('cog')][info.pop('name')] = info
    else:
        HELP_INFO[info.pop('cog')] = {info.pop('name'): info}
    return lambda func: func

app_commands.help_desc = help_desc


