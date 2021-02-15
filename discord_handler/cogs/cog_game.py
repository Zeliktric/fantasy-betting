from discord.ext.commands import Bot, command, Context

from discord_handler.base.cog_interface import ICog, AuthorState
from db.models import DBUser, BetHistory
import discord

from discord.utils import get
from datetime import datetime, timedelta
from asyncio import sleep as s

import http.client
import json
import os
import sys
from django.utils import timezone

from discord_handler.helper import choose_option, get_response, yes_no, CustCtx

async def sys_out(out_data):
  if sys.version_info >= (3,):
    return (out_data.encode('utf8').decode(sys.stdout.encoding))
  else:
    return (out_data.encode('utf8'))




class Game(ICog):
    """
    Game commands.
    """

    def __init__(self, bot: Bot):
        super().__init__(bot, AuthorState.User)
    

    async def update(bot):
      lst = ["PL", "FL1", "PD", "PL", "SA"]
      while True:
        for code in lst:
          with open(f"Competitions/{code}.json", "r") as f:
            response = json.load(f)
          for r in range(10):
            if r == 9:
              u = (response["matches"][r]["utcDate"])
          d = datetime.fromisoformat(f'{u}'[:-1])
          e = datetime.now()
          b = timedelta(seconds=0)
          t = d-e
          if b <= t:
            pass
          else:
            with open(f"Bets/{code}.json", "r") as f:
              data = json.load(f)
            
            for x, y in data.items():
              if y == 0:
                continue
              userid = x
              betamount = y[0]
              betwho = y[1]
              potentialp = y[2]
              betodd = y[3]
              pb = ""
              with open(f"Competitions/{code}.json", "r") as f:
                data = json.load(f)
              for r in range(10):
                ht = data["matches"][r]["homeTeam"]["name"]
                at = data["matches"][r]["awayTeam"]["name"]
                winner = data["matches"][r]["score"]["winner"]
                if ht in betwho or at in betwho:
                  if "draw" in betwho:
                    pb = "DRAW"
                    break
                  elif ht in betwho:
                    pb = "HOME_TEAM"
                    break
                  elif at in betwho:
                    pb = "AWAY_TEAM"
                  break
              user = await bot.fetch_user(userid)
              obj = DBUser.objects.get(g_id=783384319711379456, u_id=user.id)
              field_object = DBUser._meta.get_field("u_bal")
              u_bal = field_object.value_from_object(obj)

              field_object = DBUser._meta.get_field("upl")
              upl = field_object.value_from_object(obj)

              field_object = DBUser._meta.get_field("sbs")
              sbs = field_object.value_from_object(obj)

              field_object = DBUser._meta.get_field("ubs")
              ubs = field_object.value_from_object(obj)
              if winner == pb:
                obj.u_bal = int(u_bal) + int(potentialp)
                obj.save()
                obj.upl = int(upl) + int(potentialp)
                obj.save()
                obj.sbs = int(sbs) + 1
                obj.save()
                msg = f"You won your bet! You have received {potentialp}!"
                profit = potentialp
              else:
                msg = f"You lost your bet! You have lost {betamount}!"
                obj.upl = int(upl) - int(betamount)
                obj.save()
                obj.ubs = int(ubs) + 1
                obj.save()
                profit = 0 - int(betamount)
              channel = await user.create_dm()
              try:
                await channel.send(msg)
              except:
                pass
              BetHistory(
                u_id=user.id,
                amount=betamount,
                team=betwho,
                profit=profit,
                odds=betodd,
                code=code,
                timestamp=timezone.now()
              ).save()
              with open(f"Bets/{code}.json", "r") as f:
                data = json.load(f)
              data.pop(str(user.id))
              with open(f"Bets/{code.upper()}.json", "w") as f:
                json.dump(data, f, indent=4)

            gw = (response["filters"]["matchday"])
            gw = int(gw) + 1
            connection = http.client.HTTPConnection('api.football-data.org')
            headers = { 'X-Auth-Token': '' }
            connection.request('GET', f'/v2/competitions/{code}/matches?matchday={gw}', None, headers )
            response = json.loads(connection.getresponse().read().decode())
            with open(f"Competitions/{code}.json", "w") as f:
              json.dump(response, f, indent=4)
            channel = bot.get_channel(808769018546094103)
            await channel.send(f"Updated {code} | {datetime.utcnow()}")
        await s(60)













    @command(
      name="get_team",
      brief="Get the team name based on a query!",
      help="Gives you the team name based on the user's query, if it can."
    )
    async def team(self, ctx: Context, code: str, *, query: str):
      lst = ["BL1", "FL1", "PD", "PL", "SA"]
      if code.upper() not in lst:
        return await ctx.send(f"`{code}` is an invalid league code! Use `*leagues` to get them!")
      n = {"BL1": "Bundesliga", "FL1": "France Ligue 1", "PD": "La Liga", "PL": "Premier League", "SA": "Serie A"}
      name = n.get(code.upper())
      if name == "Bundesliga":
        l = """
RB Leipzig
FC Augsburg
Borussia Dortmund
TSG 1899 Hoffenheim
VfB Stuttgart
Hertha BSC
SV Werder Bremen
SC Freiburg
Bayer 04 Leverkusen
1. FSV Mainz 05
1. FC Union Berlin
FC Schalke 04
Eintracht Frankfurt
1. FC Köln
VfL Wolfsburg 
Borussia Mönchengladbach
FC Bayern München
DSC Arminia Bielefeld
        """
      elif name == "France Ligue 1":
        l = """
Paris Saint-Germain FC
OGC Nice
Stade de Reims
Racing Club de Lens
Olympique Lyonnais
Montpellier HSC
AS Monaco FC
FC Lorient
Stade Rennais FC 1901
AS Saint-Étienne
Angers SCO
FC Nantes
Dijon Football Côte d'Or
Nîmes Olympique
FC Metz
RC Strasbourg Alsace
Lille OSC
Stade Brestois 29
FC Girondins de Bordeaux
Olympique de Marseille
        """
      elif name == "La Liga":
        l = """
RC Celta de Vigo
Elche CF
Granada CF
Club Atlético de Madrid
Sevilla FC
SD Huesca
SD Eibar
Real Valladolid CF
FC Barcelona
Deportivo Alavés
Getafe CF
Real Sociedad de Fútbol
Real Madrid CF
Valencia CF
Levante UD
CA Osasuna
Villarreal CF
Real Betis Balompié
Cádiz CF
Athletic Club
        """
      else:
        with open(f"Competitions/{code.upper()}.txt", "r") as f:
          l = f.read()
      listt = l.split("\n")
      fi = False
      tt = []
      for each in listt:
        if query.lower() in each.lower():
          tt.append(each.strip())
          fi = True
      if fi == True:
        o = "\n".join(tt)
        embed = discord.Embed(
          title = f"Teams with query of: `{query}`",
          description = o,
          colour = discord.Colour.green(),
          timestamp = datetime.utcnow()
        )
        embed.set_footer(
          text = "Fantasy Betting Bot"
        )
        return await ctx.send(content=ctx.message.author.mention, embed=embed)
      else:
        return await ctx.send(f"I could not find a team with the query of: `{query}` in the `{name}`!")

#     @command(
#       name="teams",
#       brief="Get the team names to use to bet!",
#       help="Shows you the team names that are required for the bet command"
#     )
#     async def teams(self, ctx: Context, code: str):
#       lst = ["BL1", "FL1", "PD", "PL", "SA"]
#       if code.upper() not in lst:
#         return await ctx.send(f"`{code}` is an invalid league code! Use `*leagues` to get them!")
#       n = {"BL1": "Bundesliga", "FL1": "France Ligue 1", "PD": "La Liga", "PL": "Premier League", "SA": "Serie A"}
#       name = n.get(code.upper())
#       if name == "Bundesliga":
#         embed = discord.Embed(
#           title = f"{name}'s team names",
#           description = """
# RB Leipzig
# FC Augsburg
# Borussia Dortmund
# TSG 1899 Hoffenheim
# VfB Stuttgart
# Hertha BSC
# SV Werder Bremen
# SC Freiburg
# Bayer 04 Leverkusen
# 1. FSV Mainz 05
# 1. FC Union Berlin
# FC Schalke 04
# Eintracht Frankfurt
# 1. FC Köln
# VfL Wolfsburg 
# Borussia Mönchengladbach
# FC Bayern München
# DSC Arminia Bielefeld
#           """,
#           colour = discord.Colour.green(),
#           timestamp = datetime.utcnow()
#         )
#         embed.set_footer(
#           text = "Fantasy Betting Bot"
#         )
#         return await ctx.send(content=ctx.message.author.mention, embed=embed)
#       elif name == "France Ligue 1":
#         embed = discord.Embed(
#           title = f"{name}'s team names",
#           description = """
# Paris Saint-Germain FC
# OGC Nice
# Stade de Reims
# Racing Club de Lens
# Olympique Lyonnais
# Montpellier HSC
# AS Monaco FC
# FC Lorient
# Stade Rennais FC 1901
# AS Saint-Étienne
# Angers SCO
# FC Nantes
# Dijon Football Côte d'Or
# Nîmes Olympique
# FC Metz
# RC Strasbourg Alsace
# Lille OSC
# Stade Brestois 29
# FC Girondins de Bordeaux
# Olympique de Marseille
#           """,
#           colour = discord.Colour.green(),
#           timestamp = datetime.utcnow()
#         )
#         embed.set_footer(
#           text = "Fantasy Betting Bot"
#         )
#         return await ctx.send(content=ctx.message.author.mention, embed=embed)
#       elif name == "La Liga":
#         embed = discord.Embed(
#           title = f"{name}'s team names",
#           description = """
# RC Celta de Vigo
# Elche CF
# Granada CF
# Club Atlético de Madrid
# Sevilla FC
# SD Huesca
# SD Eibar
# Real Valladolid CF
# FC Barcelona
# Deportivo Alavés
# Getafe CF
# Real Sociedad de Fútbol
# Real Madrid CF
# Valencia CF
# Levante UD
# CA Osasuna
# Villarreal CF
# Real Betis Balompié
# Cádiz CF
# Athletic Club
#           """,
#           colour = discord.Colour.green(),
#           timestamp = datetime.utcnow()
#         )
#         embed.set_footer(
#           text = "Fantasy Betting Bot"
#         )
#         return await ctx.send(content=ctx.message.author.mention, embed=embed)
#       with open(f"Competitions/{code.upper()}.txt", "r") as f:
#         t = f.read()
#       teams = []
#       t = t.split("\n")
#       for each in t:
#         teams.append(each)
#       teams = "\n".join(teams)
#       embed = discord.Embed(
#         title = f"{name}'s team names",
#         description = teams,
#         colour = discord.Colour.green(),
#         tiemstamp = datetime.utcnow()
#       )
#       embed.set_footer(
#         text = "Fantasy Betting Bot"
#       )
#       await ctx.send(content=ctx.message.author.mention, embed=embed)


    @command(
      name="bet",
      brief="Bet on a fixture!",
      help="Use this command to bet on a fixture of your choice!"
    )
    async def bet(self, ctx: Context):
      await ctx.send("Lets bet in DMs!")
      channel = await CustCtx.from_member_dm(ctx.message.author, self.bot)
      await channel.send("--------------------------------------------")
      lst = ["Bundesliga", "France Ligue 1", "La Liga", "Premier League", "Serie A"]
      league = await choose_option(channel, f"**Choose a league to bet on! (1 bet per league per week)**", lst)

      n = {"Bundesliga": "BL1", "France Ligue 1": "FL1", "La Liga": "PD", "Premier League": "PL", "Serie A": "SA"}
      code = n.get(league)
      with open(f"Competitions/{code.upper()}.json", "r") as f:
        response = json.load(f)

      m = []
      for r in range(10):
        try:
          winner = response["matches"][r]["score"]["winner"]
          y = response["matches"][r]["score"]["fullTime"]
          homes = y["homeTeam"]
          aways = y["awayTeam"]
          e = response["matches"][r]["homeTeam"]
          hteam = e["name"]
          o = response["matches"][r]["awayTeam"]
          ateam = o["name"]
          if r == 9:
            u = (response["matches"][r]["utcDate"])

          m.append(f"{hteam} VS {ateam}\n")
        except:
          pass
      gw = (response["filters"]["matchday"])

      team = await choose_option(channel, f"**Which fixture are you betting on in the {league}?**", m)

      fi = False
      for r in range(10):
        try:
          winner = response["matches"][r]["score"]["winner"]
          y = response["matches"][r]["score"]["fullTime"]
          homes = y["homeTeam"]
          aways = y["awayTeam"]
          e = response["matches"][r]["homeTeam"]
          hteam = e["name"]
          o = response["matches"][r]["awayTeam"]
          ateam = o["name"]
          if r == 9:
            u = (response["matches"][r]["utcDate"])
          if hteam.lower() in team.lower():
            fi = True
            break
          elif ateam.lower() in team.lower():
            fi = None
            break
        except:
          pass
      if fi == False:
        return await channel.send(f"I could not find a team in the `{league}` with the team name of `{team}`!")
      hwin = (response["matches"][r]["odds"]["homeWin"])
      awin = (response["matches"][r]["odds"]["awayWin"])
      draw = (response["matches"][r]["odds"]["draw"])
      lstt = [f"Home Win `1/{hwin}` ({hteam} wins)", f"󠁁󠁁Away Win `1/{awin}` ({ateam} wins)", f"Draw `1/{draw}` (no one wins)\n?"]
      choice = await choose_option(channel, f"**Are you betting on a:**", lstt)
      if "Home" in choice:
        teamm = f"{hteam} win"
      elif "Away" in choice:
        teamm = f"{ateam} win"
      else:
        teamm = f"draw ({hteam} vs {hteam})"

      bet = await get_response(channel, f"**How much are you betting on {teamm}?**")
      try:
        bet = float(bet[0])
      except:
        return await channel.send(f"You can only bet numbers!")
      if bet < 0:
        return await channel.send(f"You can only bet positive numbers!")
      if "Home" in choice:
        teamm = f"{hteam} win"
        odd = hwin
        wins = bet * hwin
      elif "Away" in choice:
        teamm = f"{ateam} win"
        odd = awin
        wins = bet * awin
      else:
        teamm = f"draw ({hteam} vs {hteam})"
        odd = draw
        wins = bet * draw
      obj = DBUser.objects.get(g_id=ctx.message.guild.id, u_id=ctx.message.author.id)
      field_object = DBUser._meta.get_field("u_bal")
      u_bal = field_object.value_from_object(obj)
      if int(u_bal) < bet:
        return await channel.send(f"You cannot bet `{bet}` as you only have `{u_bal}` in your account!")
      embed = discord.Embed(
        title = "Confirm New Bet",
        description = f"""
**Your {league} bet**
Amount bet: `{bet}`
Team bet on: `{teamm}`
Potential profit: `{round(wins, 2)}`
Betting odds: `1/{odd}`
        """,
        colour = discord.Colour.green(),
        timestamp = datetime.utcnow()
      )
      r = await yes_no("", channel, embed=embed)
      if r:
        with open(f"Bets/{code.upper()}.json", "r") as f:
          data = json.load(f)
        nnn = data.get(str(ctx.message.author.id))
        if nnn == None:
          data[str(ctx.message.author.id)] = [bet, teamm, wins, odd]
          with open(f"Bets/{code.upper()}.json", "w") as f:
            json.dump(data, f, indent=4)
          await channel.send(f"Bet successfully placed!")
          self.u.u_bal = u_bal - bet
          self.u.save()
        else:
          await channel.send(f"You already have a bet in the {code}! Delete it to create a new one!")

    # @command(
    #   name="bet",
    #   brief="Bet on a fixture!",
    #   help="Use this command to bet on a fixture of your choice!"
    # )
    # async def bet(self, ctx: Context, code: str, bet: float, *, team: str):
    #   lst = ["BL1", "FL1", "PD", "PL", "SA"]
    #   if code.upper() not in lst:
    #     return await ctx.send(f"`{code}` is an invalid league code! Use `*leagues` to get them!")
    #   with open(f"Competitions/{code.upper()}.json", "r") as f:
    #     response = json.load(f)
    #   m = []
    #   n = {"BL1": "Bundesliga", "FL1": "France Ligue 1", "PD": "La Liga", "PL": "Premier League", "SA": "Serie A"}
    #   name = n.get(code.upper())
    #   obj = DBUser.objects.get(g_id=ctx.message.guild.id, u_id=ctx.message.author.id)
    #   field_object = DBUser._meta.get_field("u_bal")
    #   u_bal = field_object.value_from_object(obj)
    #   if int(u_bal) < bet:
    #     return await ctx.send(f"You cannot bet `{bet}` as you only have `{u_bal}` in your account!")
    #   fi = False
    #   for r in range(10):
    #     try:
    #       winner = response["matches"][r]["score"]["winner"]
    #       y = response["matches"][r]["score"]["fullTime"]
    #       homes = y["homeTeam"]
    #       aways = y["awayTeam"]
    #       e = response["matches"][r]["homeTeam"]
    #       hteam = e["name"]
    #       o = response["matches"][r]["awayTeam"]
    #       ateam = o["name"]
    #       if r == 9:
    #         u = (response["matches"][r]["utcDate"])
    #       if team.lower() in hteam.lower():
    #         fi = True
    #         break
    #       elif team.lower() in ateam.lower():
    #         fi = None
    #         break
    #     except:
    #       pass
    #   if fi == False:
    #     return await ctx.send(f"I could not find a team in the `{code}` with the team name of `{team}`!")
    #   hwin = (response["matches"][r]["odds"]["homeWin"])
    #   awin = (response["matches"][r]["odds"]["awayWin"])
    #   draw = (response["matches"][r]["odds"]["draw"])
    #   msg = await ctx.send(f"{ctx.message.author.mention}\nAre you betting on a:\n🇭 - Home Win `1/{hwin}` ({hteam} wins)\n󠁁󠁁🇦 - Away Win `1/{awin}` ({ateam} wins)\n🇩 - Draw `1/{draw}` (no one wins)\n?")
    #   await msg.add_reaction("🇭")
    #   await msg.add_reaction("🇦")
    #   await msg.add_reaction("🇩")
    #   def check(reaction, user):
    #     l = ["🇭", "🇦", "🇩"]
    #     return user == ctx.message.author and str(reaction.emoji) in l
    #   try:
    #     reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
    #   except asyncio.TimeoutError:
    #     await msg.delete()
    #     return await ctx.send("Timeout. Please start the process again.", delete_after=5)
    #   else:
    #     emoji = str(reaction.emoji)
    #     if emoji == "🇭":
    #       teamm = f"{hteam} win"
    #       odd = hwin
    #       wins = bet * hwin
    #     elif emoji == "🇦":
    #       teamm = f"{ateam} win"
    #       odd = awin
    #       wins = bet * awin
    #     else:
    #       teamm = f"draw ({hteam} vs {hteam})"
    #       odd = draw
    #       wins = bet * draw
    #   msgg = await ctx.send(f"{ctx.message.author.mention}\nYou want to bet **`{bet}`** on a **{teamm}** with a potential profit of `{round(wins-bet, 2)}`?")
    #   await msgg.add_reaction("✅")
    #   await msgg.add_reaction("❎")
    #   def check(reaction, user):
    #     l = ["✅", "❎"]
    #     return user == ctx.message.author and str(reaction.emoji) in l
    #   try:
    #     reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
    #   except asyncio.TimeoutError:
    #     await msg.delete()
    #     await msgg.delete()
    #     return await ctx.send("Timeout. Please start the process again.", delete_after=5)
    #   else:
    #     emoji = str(reaction.emoji)
    #     if emoji == "❎":
    #       await msg.delete()
    #       await msgg.delete()
    #       return await ctx.send("Process cancelled.", delete_after=5)
    #     else:
    #       with open(f"Bets/{code.upper()}.json", "r") as f:
    #         data = json.load(f)
    #       nnn = data.get(str(ctx.message.author.id))
    #       if nnn == None:
    #         data[str(ctx.message.author.id)] = [bet, teamm, wins, odd]
    #         with open(f"Bets/{code.upper()}.json", "w") as f:
    #           json.dump(data, f, indent=4)
    #         await ctx.send(f"{ctx.message.author.mention}\nBet successfully placed!")
    #         await s(4.5)
    #         await msg.delete()
    #         await msgg.delete()
    #         self.u.u_bal = u_bal - bet
    #         self.u.save()
    #       else:
    #         await ctx.send(f"{ctx.message.author.mention}\nYou already have a bet in the {code}! Delete it to create a new one!")
    #         await s(4.5)
    #         await msg.delete()
    #         await msgg.delete()

    @command(
      name="delete_bet",
      brief="Delete a bet that you have made.",
      help="Use this command to delete a bet from a league."
    )
    async def delete_bet(self, ctx: Context, code: str):
      obj = DBUser.objects.get(g_id=ctx.message.guild.id, u_id=ctx.message.author.id)
      field_object = DBUser._meta.get_field("u_bal")
      u_bal = field_object.value_from_object(obj)
      lst = ["BL1", "FL1", "PD", "PL", "SA"]
      if code.upper() not in lst:
        return await ctx.send(f"`{code}` is an invalid league code! Use `*leagues` to get them!")
      with open(f"Bets/{code.upper()}.json", "r") as f:
        data = json.load(f)
      nnn = data.get(str(ctx.message.author.id))
      n = {"BL1": "Bundesliga", "FL1": "France Ligue 1", "PD": "La Liga", "PL": "Premier League", "SA": "Serie A"}
      name = n.get(code.upper())
      if nnn == None:
        return await ctx.send(f"{ctx.message.author.mention}\nYou do not have any current bets in the `{name}`!")
      betamount = nnn[0]
      betteam = nnn[1]
      betwins = round(nnn[2], 2)
      betodds = nnn[3]
      o = f"""
**Your {code.upper()} bet**
Amount bet: `{betamount}`
Team bet on: `{betteam}`
Potential profit: `{betwins}`
Betting odds: `1/{betodds}`
      """
      embed = discord.Embed(
        title = "Delete a bet",
        description = o,
        colour = discord.Colour.green(),
        timestamp = datetime.utcnow()
      )
      embed.set_footer(
        text = "Fantasy Betting Bot"
      )
      msgg = await ctx.send(content=ctx.message.author.mention, embed=embed)
      await msgg.add_reaction("✅")
      await msgg.add_reaction("❎")
      def check(reaction, user):
        l = ["✅", "❎"]
        return user == ctx.message.author and str(reaction.emoji) in l
      try:
        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
      except asyncio.TimeoutError:
        return await ctx.send("Timeout. Please start the process again.", delete_after=5)
      else:
        emoji = str(reaction.emoji)
        if emoji == "❎":
          await msgg.delete()
          return await ctx.send("Process cancelled")
        self.u.u_bal = int(u_bal) + int(betamount)
        self.u.save()
        data.pop(str(ctx.message.author.id))
        with open(f"Bets/{code.upper()}.json", "w") as f:
          json.dump(data, f, indent=4)
        await ctx.send(f"{ctx.message.author.mention}\nBet successfully deleted!")
        await s(4.5)
        await msgg.delete()
        

    @command(
      name="my_bets",
      brief="Shows you your current bets.",
      help="Shows you your current bets in the five leagues if you have any."
    )   
    async def my_bets(self, ctx: Context):
      x = []
      lst = ["BL1", "FL1", "PD", "PL", "SA"]
      for each in lst:
        with open(f"Bets/{each}.json", "r") as f:
          data = json.load(f)
        thedata = data.get(str(ctx.message.author.id))
        if thedata == None:
          pass
        else:
          betamount = thedata[0]
          betteam = thedata[1]
          betwins = round(thedata[2], 2)
          betodds = thedata[3]
          o = f"""
**Your {each} bet**
Amount bet: `{betamount}`
Team bet on: `{betteam}`
Potential profit: `{betwins}`
Betting odds: `1/{betodds}`
          """
          x.append(o)
      u = "".join(x)
      embed = discord.Embed(
        title = f"Current bets",
        description = "No current bets" if u == "" else u,
        colour = discord.Colour.green(),
        timestamp = datetime.utcnow()
      )
      embed.set_footer(
        text = "Fantasy Betting Bot"
      )
      await ctx.send(content=ctx.message.author.mention, embed=embed)


    @command(
      name="get_match",
      brief="Gives you the match details.",
      help="Gives you the teams playing and their odds."
    )
    async def match(self, ctx: Context, code: str, *, team: str):
      lst = ["BL1", "FL1", "PD", "PL", "SA"]
      if code.upper() not in lst:
        return await ctx.send(f"`{code}` is an invalid league code! Use `*leagues` to get them!")
      with open(f"Competitions/{code.upper()}.json", "r") as f:
        response = json.load(f)
      m = []
      n = {"BL1": "Bundesliga", "FL1": "France Ligue 1", "PD": "La Liga", "PL": "Premier League", "SA": "Serie A"}
      name = n.get(code.upper())
      fi = False
      for r in range(10):
        try:
          winner = response["matches"][r]["score"]["winner"]
          y = response["matches"][r]["score"]["fullTime"]
          homes = y["homeTeam"]
          aways = y["awayTeam"]
          e = response["matches"][r]["homeTeam"]
          hteam = e["name"]
          o = response["matches"][r]["awayTeam"]
          ateam = o["name"]
          if r == 9:
            u = (response["matches"][r]["utcDate"])
          if team.lower() in hteam.lower() or team.lower() in ateam.lower():
            fi = True
            break
        except:
          pass
      if fi == False:
        return await ctx.send(f"I could not find a team in the `{code}` with the team name of `{team}`!")
      hwin = (response["matches"][r]["odds"]["homeWin"])
      awin = (response["matches"][r]["odds"]["awayWin"])
      draw = (response["matches"][r]["odds"]["draw"])
      e = f"""
      __**Teams**__
**{hteam} VS {ateam}**

__**Odds**__
{hteam} win: 1/**{hwin}**
{ateam} win: 1/**{awin}**
Draw: 1/**{draw}**

      """
      embed = discord.Embed(
        title = f"{hteam} VS {ateam}",
        description = e.strip(),
        colour = discord.Colour.green(),
        timestamp = datetime.utcnow()
      )
      embed.set_footer(
        text = "Fantasy Betting Bot"
      )
      await ctx.send(content=ctx.message.author.mention, embed=embed)


    @command(
      name="matches",
      brief="Gives you the current matches and the GW.",
      help="Shows you the current matches that you can bet on!"
    )
    async def matches(self, ctx: Context, code: str):
      lst = ["BL1", "FL1", "PD", "PL", "SA"]
      if code.upper() not in lst:
        return await ctx.send(f"`{code}` is an invalid league code! Use `*leagues` to get them!")
      with open(f"Competitions/{code.upper()}.json", "r") as f:
        response = json.load(f)
      m = []
      n = {"BL1": "Bundesliga", "FL1": "France Ligue 1", "PD": "La Liga", "PL": "Premier League", "SA": "Serie A"}
      name = n.get(code.upper())
      for r in range(10):
        try:
          winner = response["matches"][r]["score"]["winner"]
          y = response["matches"][r]["score"]["fullTime"]
          homes = y["homeTeam"]
          aways = y["awayTeam"]
          e = response["matches"][r]["homeTeam"]
          hteam = e["name"]
          o = response["matches"][r]["awayTeam"]
          ateam = o["name"]
          if r == 9:
            u = (response["matches"][r]["utcDate"])

          m.append(f"**{hteam} VS {ateam}**\n")
        except:
          pass
      gw = (response["filters"]["matchday"])
      o = "\n".join(m)
      embed = discord.Embed(
        title = f"{name}'s GameWeek {gw} matches",
        description = f"** **\n{o}",
        colour = discord.Colour.green(),
        timestamp = datetime.utcnow()
      )
      embed.set_footer(
        text = "Fantasy Betting Bot"
      )
      try:
        f = os.path.abspath(f"C:/Users/Admin/Pictures/zbp/{code.upper()}.png")
        file = discord.File(f, filename=f)
        embed.set_thumbnail(url=f"attachment://{code.upper()}.png")
      except:
        f = os.path.abspath(f"C:/Users/Admin/Pictures/zbp/{code.upper()}.jpg")
        file = discord.File(f, filename=f)
        embed.set_thumbnail(url=f"attachment://{code.upper()}.jpg")
      await ctx.send(content=ctx.message.author.mention, embed=embed, file=file)

    @command(
      name="leagues",
      brief="Gives you the current leagues and their codes.",
      help="Shows you the current leagues supported and their two-character code to use to bet."
    )
    async def leagues(self, ctx: Context):
      embed = discord.Embed(
        title = "Current leagues + league codes",
        description = """
        **League Code**\t|\t**League Name**
BL1 | Bundesliga
FL1 | France Ligue 1
PD | La Liga
PL | Premier League
SA | Serie A
        """,
        colour = discord.Colour.green(),
        timestamp = datetime.utcnow()
      )
      embed.set_footer(
        text = "Fantasy Betting Bot"
      )

      await ctx.send(content=ctx.message.author.mention, embed=embed)

    @command(
      name="bet_history",
      brief="Shows you your betting history",
      help="Shows you your betting history. Use the time to show more detailed statistics"
    )
    async def bet_history(self, ctx: Context, *, time_stamp=None):
      #self.u.
      obj = BetHistory.objects.filter(u_id=ctx.message.author.id).values_list('timestamp', flat=True)
      if str(obj) == "<QuerySet []>":
        return await ctx.send(f"{ctx.message.author.mention}\nYou don't have any bet history!")
      if time_stamp == None:
        ts = obj[0]
        embed = discord.Embed(
          title = "Bet History Timestamps",
          description = str(ts),
          colour = discord.Colour.green(),
          timestamp = datetime.utcnow()
        )
        embed.set_footer(
          text = "Fantasy Betting Bot | Use *bet_history <timestamp> for detailed statistics"
        )
        return await ctx.send(content=ctx.message.author.mention, embed=embed)
      obj = BetHistory.objects.get(timestamp=time_stamp)
      fo = BetHistory._meta.get_field("timestamp")
      ts = fo.value_from_object(obj)
      fo = BetHistory._meta.get_field("code")
      code = fo.value_from_object(obj)
      fo = BetHistory._meta.get_field("amount")
      amount = fo.value_from_object(obj)
      fo = BetHistory._meta.get_field("team")
      team = fo.value_from_object(obj)
      fo = BetHistory._meta.get_field("profit")
      profit = fo.value_from_object(obj)
      fo = BetHistory._meta.get_field("odds")
      odds = fo.value_from_object(obj)
      fo = BetHistory._meta.get_field("code")
      code = fo.value_from_object(obj)
      n = {"BL1": "Bundesliga", "FL1": "France Ligue 1", "PD": "La Liga", "PL": "Premier League", "SA": "Serie A"}
      name = n.get(code.upper())
      if int(profit) < 0:
        wins = "Loss"
      else:
        wins = "Profit"
      o = f"""
**Your {name} bet**
Amount bet: `{amount}`
Team bet on: `{team}`
{wins}: `{profit}`
Betting odds: `1/{odds}`
      """
      embed = discord.Embed(
        title = f"Bet on {ts}",
        description = o,
        colour = discord.Colour.green(),
        timestamp = datetime.utcnow()
      )
      embed.set_footer(
        text = "Fantasy Betting Bot | Use *bet_history to get a list of timestamps!"
      )
      await ctx.send(content=ctx.message.author.mention, embed=embed)


    @command(
        name='account',
        brief='Shows you your account.',
        help='Shows you your account details including: money, total profit/loss, successful & unsuccessful bids.'
    )
    async def account(self, ctx: Context):
        obj = DBUser.objects.get(g_id=ctx.message.guild.id, u_id=ctx.message.author.id)
        field_object = DBUser._meta.get_field("u_bal")
        u_bal = field_object.value_from_object(obj)

        field_object = DBUser._meta.get_field("sbs")
        sbs = field_object.value_from_object(obj)

        field_object = DBUser._meta.get_field("ubs")
        ubs = field_object.value_from_object(obj)

        field_object = DBUser._meta.get_field("upl")
        upl = field_object.value_from_object(obj)

        if upl < 0:
          pol = "Loss"
          upl = upl.replace("-", "")
        else:
          pol = "Profit"

        embed = discord.Embed(
          title = f"{ctx.message.author.name}'s account",
          description = f"Balance: `{u_bal}`\nTotal {pol}: `{upl}`\n\nSuccessful bets: `{sbs}`\nUnsuccessful bets: `{ubs}`",
          colour = discord.Colour.green(),
          timestamp = datetime.utcnow()
        )
        embed.set_footer(
          text = "Fantasy Betting Bot"
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.loop.create_task(Game.update(bot))
    bot.add_cog(Game(bot))

