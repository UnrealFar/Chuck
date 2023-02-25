import os

try:
    import bot
except ModuleNotFoundError:
    os.system("python3.9 -m pip install -r requirements.txt")
finally:
    import bot
    import discord
    import utils

if __name__ == "__main__":
    if not discord.opus.is_loaded():
        discord.opus.load_opus("./libopus.so.0.8.0")
    bot.run()
