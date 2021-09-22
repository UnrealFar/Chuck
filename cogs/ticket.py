import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
import json
import asyncio

class Tickets(commands.Cog):
    """Commands for the ticket system!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def new(self, ctx, *, args = None):
        if args == None:
            message_content = "Please wait, we will be with you shortly!"
        else:
            message_content = "".join(args)
        with open("data.json") as f:
            data = json.load(f)
        ticket_number = int(data["ticket-counter"])
        ticket_number += 1
        ticket_channel = await ctx.guild.create_text_channel("ticket-{}".format(ticket_number))
        await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)
        for role_id in data["valid-roles"]:
            role = ctx.guild.get_role(role_id)
            await ticket_channel.set_permissions(role, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
        await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
        em = discord.Embed(title="New ticket from {}#{}".format(ctx.author.name, ctx.author.discriminator), description= "{}".format(message_content), color=0x00a8ff)
        await ticket_channel.send(embed=em)
        pinged_msg_content = ""
        non_mentionable_roles = []
        if data["pinged-roles"] != []:
            for role_id in data["pinged-roles"]:
                role = ctx.guild.get_role(role_id)
                pinged_msg_content += role.mention
                pinged_msg_content += " "
                if role.mentionable:
                    pass
                else:
                    await role.edit(mentionable=True)
                    non_mentionable_roles.append(role)
            await ticket_channel.send(pinged_msg_content)
            for role in non_mentionable_roles:
                await role.edit(mentionable=False)
        data["ticket-channel-ids"].append(ticket_channel.id)
        data["ticket-counter"] = int(ticket_number)
        with open("data.json", 'w') as f:
            json.dump(data, f)
        created_em = discord.Embed(title="Ticket Created!", description="Your ticket has been created at {}".format(ticket_channel.mention), color=0x00a8ff)
        await ctx.send(embed=created_em)

    @commands.command()
    async def close(self, ctx):
        with open('data.json') as f:
            data = json.load(f)
        if ctx.channel.id in data["ticket-channel-ids"]:
            channel_id = ctx.channel.id
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() == "close"
            try:
                em = discord.Embed(title="Closing ticket!", description="Are you sure you want to close this ticket? Reply with `close` if you are sure.", color=0x00a8ff)
                await ctx.send(embed=em)
                await self.bot.wait_for('message', check=check, timeout=60)
                await ctx.channel.delete()
                index = data["ticket-channel-ids"].index(channel_id)
                del data["ticket-channel-ids"][index]
                with open('data.json', 'w') as f:
                    json.dump(data, f)
            except asyncio.TimeoutError:
                em = discord.Embed(title="Ticket not closed!", description="You have run out of time to close this ticket. Please run the command again.", color=0x00a8ff)
                await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Tickets(bot))
