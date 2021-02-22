import os

from discord.ext.commands import Bot
from discord_handler.base.cog_interface import ICog, AuthorState
from discord.ext.commands import Bot, command, Context

from discord_handler.base.cog_interface import ICog, AuthorState
from db.models import DBUser
import discord

from discord.utils import get
from datetime import datetime, timedelta
from asyncio import sleep as s

from discord_handler.helper import get_user

import http.client
import json
import os
import sys

path = os.path.dirname(os.path.realpath(__file__)) + "/../../"


class Mod(ICog):
    """
    All commands related to moderation of discord servers.
    """

    def __init__(self, bot: Bot):
        super().__init__(bot, AuthorState.Mod)

    @command(
        name="all_bets",
        brief="Get all the bets of users in a particular league",
        help="Shows you some bet information from each user that has bet in a league"
    )
    async def all_bets(self, ctx: Context, code: str):
        lst = ["BL1", "FL1", "PD", "PL", "SA"]
        if code.upper() not in lst:
            return await ctx.send(f"`{code}` is an invalid league code! Use `*leagues` to get them!")
        n = {"BL1": "Bundesliga", "FL1": "France Ligue 1", "PD": "La Liga", "PL": "Premier League", "SA": "Serie A"}
        name = n.get(code.upper())
        with open(f"Bets/{code.upper()}.json", "r") as f:
            data = json.load(f)
        u = []
        for x, y in data.items():
            thedata = data.get(str(x))
            if thedata == None:
                continue
            elif y == 0:
                continue
            else:
                betamount = thedata[0]
                betteam = thedata[1]
                betwins = round(thedata[2], 2)
                betodds = thedata[3]
                user = await self.bot.fetch_user(int(x))
                o = f"""
**{user}'s bet**
Amount bet: `{betamount}`
Team bet on: `{betteam}`
Potential profit: `{betwins}`
Betting odds: `1/{betodds}`
                """
                u.append(o)
        uu = "".join(u)
        embed = discord.Embed(
            title = f"Current bets",
            description = "No current bets" if uu == "" else uu,
            colour = discord.Colour.green(),
            timestamp = datetime.utcnow()
        )
        embed.set_footer(
            text = "Fantasy Betting Bot"
        )
        await ctx.send(content=ctx.message.author.mention, embed=embed)

    @command(
        name="add_money",
        brief="Add money to a user.",
        help="Add money to a user for a reason."
    )
    async def add_money(self, ctx: Context, user: discord.Member, money: int, *, reason):
        obj = DBUser.objects.get(g_id=ctx.message.guild.id, u_id=user.id)
        field_object = DBUser._meta.get_field("u_bal")
        u_bal = field_object.value_from_object(obj)
        pm = int(u_bal) + money
        obj.u_bal = pm
        obj.save()
        await ctx.send(f"Successfully added {money} to {user}! They now have {pm}.")
        channel = self.bot.get_channel(808769018546094103)
        await channel.send(f"{ctx.message.author} has added {money} to {user} for a total of {pm}.\nReason:\n```{reason}```")

    @command(
        name="remove_money",
        brief="Remove money from a user.",
        help="Remove money from a user for a reason."
    )
    async def remove_money(self, ctx: Context, user: discord.Member, money: int, *, reason):
        obj = DBUser.objects.get(g_id=ctx.message.guild.id, u_id=user.id)
        field_object = DBUser._meta.get_field("u_bal")
        u_bal = field_object.value_from_object(obj)
        pm = int(u_bal) - money
        obj.u_bal = pm
        obj.save()
        await ctx.send(f"Successfully removed {money} to {user}! They now have {pm}.")
        channel = self.bot.get_channel(808769018546094103)
        await channel.send(f"{ctx.message.author} has removed {money} from {user} for a total of {pm}.\nReason:\n```{reason}```")


def setup(bot):
    bot.add_cog(Mod(bot))
