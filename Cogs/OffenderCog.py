from aiohttp.log import internal_logger
import discord
from discord import app_commands
from discord.ext import commands
from Functions.Database import GetOffenderStat, RegisterOffender
from config import StaffRoles, TestServerRoles, BotEmojis
from Functions.Utilities import IsValidID, GetProfileLink, GetRBXUserData
import os
import sqlite3 as sql
from dotenv import load_dotenv

load_dotenv()

class OffenderCommands(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  offender_group = app_commands.Group(name="offender", description="offender commands")


  async def offender_autocomplete(
    self,
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[int]]: 
    with sql.connect(database="RigShift.db") as con:
        cursor: Cursor = con.cursor()
        
        # Filter choices based on user input and cap results at 25
        cursor.execute(
            "SELECT RBXuserID FROM OffenderStats WHERE CAST(RBXuserID AS TEXT) LIKE ? LIMIT 25",
            (f"{current}%",)
        )
        db_results = cursor.fetchall()

    return [
        app_commands.Choice(name=str(who[0]), value=who[0])
        for who in db_results
    ]

  @offender_group.command(name="stats", description="check offenders ban stats")
  @app_commands.autocomplete(who=offender_autocomplete)
  @app_commands.checks.cooldown(rate=3, per=60.0, key=lambda i: i.user.id)
  @app_commands.checks.has_any_role(*TestServerRoles)
  @app_commands.choices(which_stat=[
    app_commands.Choice(name="Permanentban Count", value="PermabanCount"),
    app_commands.Choice(name="Temporaryban Count", value="TempbanCount"),
    app_commands.Choice(name="Serverban Count", value="ServerbanCount"),
    app_commands.Choice(name="All", value="*")
  ])
  async def OffenderBanStats(
    self, 
    interaction: discord.Interaction, 
    who: int, 
    which_stat: app_commands.Choice[str]
  ):
    await interaction.response.defer(thinking=True)
    if IsValidID(who) == False:
      return 0
    else:
      offender_data = GetRBXUserData(who)
      isRegistered, data = await GetOffenderStat(OffenderID=who, Stat=which_stat.value)
      formatted = ""
      if len(data) > 1:
          formatted = f"Offender Name: {offender_data.get("name")}\n Temporaryban Count: {data[0]}\n Permanentban Count: {data[1]}\n Serverban Count: {data[2]} "
      else:
        formatted = f"Offender Name: {offender_data.get("name")}\n  {which_stat.name}: {data[0]}"
      if not isRegistered:
        await RegisterOffender(OffenderID=who)
        await interaction.followup.send("Offender was not registered. Registered now, please run the command again!")
      else:
        await interaction.followup.send(f"Stats:\n\n {formatted}")

  @OffenderBanStats.error
  async def OffenderBanStats_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
  if isinstance(error, app_commands.MissingAnyRole):
    denyEmojiID = BotEmojis.get("rejected")
    await interaction.response.send_message(
      f"<a:rejected:{denyEmojiID}> You don't have the required roles to use this command.", 
      ephemeral=True
    )
  elif isinstance(error, app_commands.CommandOnCooldown):
    await interaction.response.send_message(
      f"⏳ Please wait {error.retry_after:.1f} seconds before using this command again.", 
      ephemeral=True
    )













async def setup(bot: commands.Bot):
  await bot.add_cog(OffenderCommands(bot))