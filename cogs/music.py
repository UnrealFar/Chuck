from __future__ import annotations

import typing
import asyncio

import jishaku
import discord
import os
import aiosqlite
import urllib.parse
from discord.ext import commands
from discord import app_commands
from bot import Unreal

class MusicEmbed(discord.Embed):
    def __init__(
        self,
        song: Song,
        _type: int,
    ):
        if _type == 0:
            title = "Now Playing!"
        elif _type == 1:
            title = "Song Added To Queue"
        super().__init__(
            title = title,
            description=f"""
            **Song: [`{song.title}`]({song.url})**
            **Duration**: `{song.duration//60}:{song.duration%60}`
            **Artists**: `{song.artist}`
            """
        )
        self.set_thumbnail(url = song.thumbnail)

class Song:
    def __init__(self, source, url, title, duration, thumbnail, artist):
        self.source = source
        self.url = url
        self.title = title
        self.artist = artist
        self.title = title
        self.duration = int(duration)
        self.thumbnail = thumbnail

class Player:
    base_url = os.environ['music_base_url']

    def __init__(self, **kwargs):
        self.vc: discord.VoiceClient = kwargs.get('vc')
        self.cog = kwargs['cog']
        self.queue = []
        self.playing: bool = False

    async def on_stop(self):
        self.queue = self.queue[1:]
        if len(self.queue) == 0:
            async def dscn():
                await asyncio.sleep(120)
                if len(self.queue) != 0:
                    if not self.playing:
                        self.play()
                else:
                    await self.cog.destroy_player(self)
            await dscn()
        else:
            self.play()

    def dp_event(
        self,
        dp_ev_name: str,
        *args,
        **kwargs
    ):
        c = getattr(self.cog, dp_ev_name, None)
        if c:
            asyncio.ensure_future(c(*args, **kwargs))

    async def fetch_song(self, song: str):
        async with self.cog.session.get(
            f"{self.base_url}/search/songs?query={urllib.parse.quote(song.replace(' ','+'))}&page=1&limit=1"
        ) as resp:
            data = (await resp.json())['data']['results'][0]
        source = data['downloadUrl'][-2]['link']
        title = data["name"]
        duration = data["duration"]
        thumbnail = data["image"][-1]['link']
        fa = (', ' + data['featuredArtists']) if len(data['featuredArtists']) > 1 else ''
        artist = urllib.parse.unquote(data['primaryArtists'] + fa)
        ret = Song(
            source = source,
            url = data['url'],
            title = title,
            duration = duration,
            thumbnail = thumbnail,
            artist = artist
        )
        return ret

    def play(self) -> Song:
        song = self.queue[0]
        src = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                song.source,
                options= "-vn -loglevel panic",
                before_options = "-nostdin"
            ))
        self.vc.play(
            src,
            after = lambda _: self.dp_event("stop")
        )
        self.playing = True
        return song

    def skip(self) -> Song:
        self.queue = self.queue[1:]
        self.vc.stop()
        self.play()


class Music(commands.Cog):
    bot: Unreal
    db: aiosqlite.Connection

    def __init__(self, bot: Unreal) -> None:
        self.bot = bot
        self.ready = False
        self.name = "Music"
        self.players = {}

    async def cog_load(self) -> None:
        self.session = self.bot.session
        async with aiosqlite.connect(
            "db/music.sqlite"
        ) as self.db:
            async with self.db.execute(
                """CREATE TABLE IF NOT EXISTS playlists
                (pn TEXT, pid TEXT, owner TEXT, sn LONGTEXT)
                """
            ):
                await self.db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        for vc in self.bot.voice_clients:
            await vc.disconnect()
    
    async def create_player(self, i, vc: typing.Optional[discord.VoiceClient] = None) -> Player:
        if i.guild_id in self.players:
            return self.players[i.guild_id]
        if vc:
            player = Player(
                g_id = i.guild_id,
                vc = vc,
                cog = self,
            )
            self.players[i.guild_id] = player
            return player

    @app_commands.command(name = "play")
    @app_commands.describe(
        vc = "The text channel to join!",
    )
    async def play_command(
        self,
        interaction: discord.Interaction,
        song: str,
        vc: typing.Optional[discord.VoiceChannel] = None
    ) -> None:
        """Plays music in a channel"""
        if not interaction.guild_id:
            return await interaction.response.send_message(
                "You must be in a guild to use this command!"
            )
        if not vc:
            try:
                vc = interaction.user.voice.channel
                
            except:
                return await interaction.response.send_message(
                    "Please join a voice channel or specify one!"
                )
        try:
            vc = await vc.connect(self_deaf = True)
        except:
            pass
        player = await self.create_player(interaction, vc = vc)

        await interaction.response.defer()

        try:
            s = await player.fetch_song(song)
        except Exception as e:
            return await interaction.followup.send(str(e))

        player.queue.append(s)
        if not player.playing:
            player.play()
            em = MusicEmbed(s, 0)
            await interaction.followup.send(embed = em)
        else:
            em = MusicEmbed(s, 1)
            await interaction.followup.send(embed = em)

    @app_commands.command(name="skip")
    async def skip_command(
        self,
        i: discord.Interaction
    ):
        """Skip the current playing song.
        """
        player = await self.create_player(i)
        if not player:
            return await i.response.send_message("Please start playing some music first!")
        if i.user.id not in player.vc.channel.voice_states:
            return await i.response.send_message("Please join a voice channel first!")
        if player.playing:
            player.skip()
            s = player.queue[0]
            em = MusicEmbed(s, 0)
            await i.response.send_message(embed = em)

    @app_commands.command(name="queue")
    async def qcmd(
        self,
        i: discord.Interaction,
    ):
        """Get all songs that are to played from the queue!
        """
        player = await self.create_player(i)
        if player is None:
            return await i.response.send_message(
                "Please create a music session in this guild first!"
            )
        pag = commands.Paginator(prefix = "", suffix = "", max_size = 200)
        for s in range(len(player.queue)):
            trt = player.queue[s].title
            if len(trt) > 20:
                trt = trt[:len(trt)-20] + "..."
            pag.add_line(f"> #{s+1}: **{trt}**")
        emb = discord.Embed(
            title = "Song Queue",
            description = (pag.pages[0] if len(pag)>1 else "No songs in queue!"),
            colour = discord.Colour.gold(),
        )
        emb.set_footer(text = f"Requested by {i.user}", icon_url = i.user.display_avatar.url)
        embp = jishaku.paginators.PaginatorEmbedInterface(
            self.bot,
            pag,
            embed = emb,
            owner = i.user,
        )
        await i.response.send_message(embed = emb, view = embp)

async def setup(bot: Unreal):
    await bot.add_cog(Music(bot))
