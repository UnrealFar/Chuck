import discord
import typing
import functools
from discord import app_commands

HELP_INFO: typing.Dict[str, typing.Dict[str, str]] = {}


def help_desc(info: typing.Dict):
    if info["cog"] in HELP_INFO:
        HELP_INFO[info.pop("cog")][info.pop("name")] = info
    else:
        HELP_INFO[info.pop("cog")] = {info.pop("name"): info}

__appcmdfunc = app_commands.command
__grpappcmdfunc = app_commands.Group.command

def app_command(*args, **kwargs):
    def wrapper(func) -> app_commands.AppCommand:
        info = {}
        example = kwargs.pop('example', None)
        if kwargs.pop("group", False):
            ret = __grpappcmdfunc(*args, **kwargs)(func)
        else:
            ret = __appcmdfunc(*args, **kwargs)(func)
        info['cog'] = func.__qualname__.split('.')[0].lower().replace('cog', '')
        info['description'] = ret.description
        params = ''
        for param in ret.parameters:
            default = '=' + str(param.default) if param.default else ''
            p = f' [{param.display_name}{default}]'
            params += p
        info['name'] = ret.name
        info['syntax'] = syntax = f"/{ret.qualified_name}{params}"
        info['example'] = example or syntax
        help_desc(info)
        return ret
    return wrapper

def group_app_command(*args, **kwargs):
    kwargs['group'] = True
    return app_command(*args, **kwargs)

app_commands.command = app_command
app_commands.Group.command = group_app_command


def update_readme_commands():
    cas = '# Chuck\n<p align="center">\n  <img alt="Our Bot!" src="https://cdn.discordapp.com/emojis/861955812854202378.png">\n</p>\n\n## About Chuck\n- Chuck is a bot developed by [Farrr](https://github.com/unrealfar), using [Discord.py](https://discord.gg/dpy) library in Python!\n- Chuck was developed in order to make Discord a lot more fun, with various features unique features.\n- As of now, Chuck is in v3.0.0b\n- We hope to add a lot more features to the bot in the upcoming future!\n- Stay safe!\n- Chuck has completely migrated to slash commands.\n\n## Commands:\n'
    for c, cmds in HELP_INFO.items():
        cs = "### " + c.capitalize() + "\n"
        for name, cmd in cmds.items():
            cs += f"- **{name}**: {cmd['description']}\n    - Syntax: `{cmd['syntax']}`\n    - Usage: `{cmd['example']}`\n"
        cas += cs + "\n"
    with open("README.md", "w") as rf:
        rf.write(cas)
        print("Updated README.md!")
