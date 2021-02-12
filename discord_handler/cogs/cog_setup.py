from discord.ext.commands import Bot, command, Context

from discord_handler.base.cog_interface import ICog, AuthorState
from discord.ext.commands import command, Context, Bot
from discord import Role, Member, Embed
from discord.utils import get
import re
from typing import Union, Tuple
import os
from asyncio import sleep as s

from db.models import DBUser
from discord_handler.base.cog_interface import ICog, AuthorState
from discord_handler.helper import get_user

path = os.path.dirname(os.path.realpath(__file__)) + "/../../"



class Setup(ICog):
    """
    Setup commands.
    """

    def __init__(self, bot: Bot):
        super().__init__(bot, AuthorState.Owner)

    @command(
        name='setup',
        brief='Starts the setup process for Fantasy Betting Bot',
        help='Starts the setup process. Only to be used if you want the bot to give a role when a member reacts.'
    )
    async def setup(self, ctx: Context):
        await ctx.send("Thank you for inviting the Fantasy Betting Bot to your server!")
        await s(1.5)
        await ctx.send("We will now go through the setup process :)")
        await s(1.5)
        if f"{self.g.cnnid}" != "None":
            ms = await ctx.send(
                f"Your current channel ID is <#{self.g.cnnid}>\n\nPlease enter the channel ID of the message in which you want people to be able to react to get a role.\nType `0` to keep and `1` to end")
        else:
            ms = await ctx.send(
                f"Please enter the channel ID of the message in which you want people to be able to react to get a role.\nType `0` for none and `1` to end")

        def check(m):
            return m.author.id == ctx.message.author.id

        try:
            message = await self.bot.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Timeout. Please start the process again.")

        else:
            channelid = message.content
            guild = message.guild
            if channelid == "0" and f"{self.g.cnnid}" != "None":
                cic = self.g.cnnid
                m = self.bot.get_channel(int(cic))
            elif channelid == "0":
                cic = None
            elif channelid == "1":
                return await ctx.send("Process ended")
            else:
                try:
                    if not isinstance(int(channelid), int):
                        return await ctx.send(f"{channelid} is an invalid channel ID!\nPlease start again.")
                except:
                    return await ctx.send(f"{channelid} is an invalid channel ID!\nPlease start again.")
                cic = channelid
                m = self.bot.get_channel(int(cic))
                if m == None:
                    return await ctx.send(f"{cic} is an invalid channel ID!\nPlease start again.")
            if f"{self.g.msgid}" != "None":
                ms = await ctx.send(
                    f"Your current message is: <https://discord.com/channels/{guild.id}/{m.id}/{self.g.msgid}\n\nPlease enter the message ID of the message in <#{m.id}> in which you want people to be able to react to get a role.\nType `0` to keep and `1` to end")
            else:
                ms = await ctx.send(
                    f"Please enter the message ID of the message in <#{m.id}> in which you want people to be able to react to get a role.\nType `0` for none and `1` to end")

            def check(m):
                return m.author.id == ctx.message.author.id

            try:
                message = await self.bot.wait_for("message", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("Timeout. Please start the process again.")

            else:
                messageid = message.content

                if messageid == "0" and f"{self.g.msgid}" != "None":
                    cic = self.g.msgid
                    c = await m.fetch_message(int(cic))
                elif messageid == "0":
                    cic = None
                elif messageid == "1":
                    return await ctx.send("Process ended")
                else:
                    try:
                        if not isinstance(int(messageid), int):
                            return await ctx.send(f"{messageid} is an invalid message ID!\nPlease start again.")
                    except:
                        return await ctx.send(f"{messageid} is an invalid message ID!\nPlease start again.")
                    cic = messageid
                    c = await m.fetch_message(int(cic))
                    if c == None:
                        return await ctx.send(f"{cic} is an invalid message ID!\nPlease start again.")
                if f"{self.g.rolid}" != "None":
                    ms = await ctx.send(
                        f"Your current role is <@&{self.g.rolid}>\n\nPlease enter the role ID in which you want people to get when reacting in <#{m.id}>\nType `0` to keep and `1` to end")
                else:
                    ms = await ctx.send(
                        f"Please enter the role ID in which you want people to get when reacting in <#{m.id}>\nType `0` for none and `1` to end")

                def check(m):
                    return m.author.id == ctx.message.author.id

                try:
                    message = await self.bot.wait_for("message", timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("Timeout. Please start the process again.")

                else:
                    roleid = message.content

                    if roleid == "0" and f"{self.g.rolid}" != "None":
                        cic = self.g.rolid
                        r = get(guild.roles, id=int(cic))
                    elif roleid == "0":
                        cic = None
                    elif roleid == "1":
                        return await ctx.send("Process ended")
                    else:
                        try:
                            if not isinstance(int(roleid), int):
                                return await ctx.send(f"{roleid} is an invalid role ID!\nPlease start again.")
                        except:
                            return await ctx.send(f"{roleid} is an invalid role ID!\nPlease start again.")
                        cic = roleid
                        r = get(guild.roles, id=int(cic))
                        if r == None:
                            return await ctx.send(f"{cic} is an invalid role ID!\nPlease start again.")
                    fm = await ctx.send(
                        f"Are these details correct?\n\nMessage: <https://discord.com/channels/{guild.id}/{m.id}/{c.id}>\nChannel: <#{m.id}>\nRole: <@&{r.id}>\n\n`yes` if they are correct")

                    def check(reaction, user):
                        print(reaction in ["✅", "❎"] and user.id == ctx.message.author.id)
                        return reaction in ["✅", "❎"] and user.id == ctx.message.author.id

                    def check(m):
                        return m.author.id == ctx.message.author.id

                    try:
                        message = await self.bot.wait_for("message", timeout=30.0, check=check)
                    except asyncio.TimeoutError:
                        return await ctx.send("Timeout. Please start the process again.")
                    else:
                        msg = message.content
                        if msg.lower() != "yes":
                            await ctx.send("Process ended")
                            return
                        else:
                            e = await m.fetch_message(int(c.id))
                            await e.add_reaction("💸")
                            await ctx.send(f"{ctx.message.author.mention}\nSetup finished")
                            self.g.msgid = c.id
                            self.g.cnnid = m.id
                            self.g.rolid = r.id
                            self.g.save()


def setup(bot):
    bot.add_cog(Setup(bot))
