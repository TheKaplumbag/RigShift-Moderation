import discord
import sqlite3 as sql
from discord import app_commands
from discord.ext import commands
from Functions.Database import AddBan,IncreaseStaffStat,DecreaseStaffStat,RegisterStaff,GetStaffStat, IncreaseOffenderStat,DecreaseOffenderStat, RegisterOffender, GetOffenderStat
from config import TestSpecialRoles, SpecialRoles, BotEmojis, TestServerRoles, StaffRoles
from Functions.Utilities import IsValidID, GetProfileLink, GetRBXUserData

approveID = BotEmojis.get("approved")
rejectID = BotEmojis.get("rejected")

class AdminCommands(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  admin_group = app_commands.Group(name="admin", description="admin+ commands")

  # STAFF MANAGEMENT COMMANDS
  @admin_group.command(name="add-staffstat", description="add stat to staff")
  @app_commands.checks.cooldown(rate=2, per=35.5, key=lambda i: i.user.id)
  @app_commands.checks.has_any_role(*SpecialRoles)
  @app_commands.choices(stat_type=[
    app_commands.Choice(name="Permanentban Count", value="PermabanCount"),
    app_commands.Choice(name="Temporaryban Count", value="TempbanCount"),
    app_commands.Choice(name="Serverban Count", value="ServerbanCount")
  ])
  async def Add_StaffStat(
    self, 
    interaction: discord.Interaction,
    who: discord.Member,
    stat_type: app_commands.Choice[str]
  ):
    await interaction.response.defer(thinking=True)
    
    isReg, data = await GetStaffStat(who.id, "*")
    if isReg == False:
      await interaction.followup.send(f"<a:rejected:{rejectID}> Staff is not registered!", ephemeral=True)
      return
    success = await IncreaseStaffStat(who.id, stat_type.value)
    if success:
      await interaction.followup.send(content=f"<a:approved:{approveID}> successfully added **1** to **{who}**'s **{stat_type.name}**!")
      owner= await self.bot.fetch_user(self.bot.owner_id)
      await owner.send(f"{interaction.user.name} added 1 to {who.name}'s {stat_type.name}\n\n Server: {interaction.guild}")
    else:
      await interaction.followup.send("Faced with an error while increasing stat!")

  @Add_StaffStat.error
  async def Add_StaffStat_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingAnyRole):
      await interaction.response.send_message(
        f"<a:rejected:{denyEmojiID}> You don't have the required roles to use this command.", 
        ephemeral=True
      )
    elif isinstance(error, app_commands.CommandOnCooldown):
      await interaction.response.send_message(
        f"⏳ Please wait {error.retry_after:.1f} seconds before using this command again.", 
        ephemeral=True
      )

  @admin_group.command(name="remove-staffstat", description="remove stat from staff")
  @app_commands.checks.cooldown(rate=2, per=35.5, key=lambda i: i.user.id)
  @app_commands.checks.has_any_role(*SpecialRoles)
  @app_commands.choices(stat_type=[
    app_commands.Choice(name="Permanentban Count", value="PermabanCount"),
    app_commands.Choice(name="Temporaryban Count", value="TempbanCount"),
    app_commands.Choice(name="Serverban Count", value="ServerbanCount")
  ])
  async def Remove_StaffStat(
    self, 
    interaction: discord.Interaction,
    who: discord.Member,
    stat_type: app_commands.Choice[str]
  ):
    await interaction.response.defer(thinking=True)
    
    isReg, data = await GetStaffStat(who.id, "*")
    if isReg == False:
      await interaction.followup.send(f"<a:rejected:{rejectID}> Staff is not registered!", ephemeral=True)
      return
    success = await DecreaseStaffStat(who.id, stat_type.value)
    if success:
      await interaction.followup.send(content=f"<a:approved:{approveID}> successfully removed **1** from **{who}**'s **{stat_type.name}**!")
      owner= await self.bot.fetch_user(self.bot.owner_id)
      await owner.send(f"{interaction.user.name} removed 1 from {who.name}'s {stat_type.name}\n\n Server: {interaction.guild}")
    else:
      await interaction.followup.send("Faced with an error while decreasing stat!")
  @Remove_StaffStat.error
  async def Remove_StaffStat_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingAnyRole):
      await interaction.response.send_message(
        f"<a:rejected:{denyEmojiID}> You don't have the required roles to use this command.", 
        ephemeral=True
      )
    elif isinstance(error, app_commands.CommandOnCooldown):
      await interaction.response.send_message(
        f"⏳ Please wait {error.retry_after:.1f} seconds before using this command again.", 
        ephemeral=True
      )
      
  # OFFENDER MANAGEMENT COMMANDS
  
  async def offender_autocomplete(
    self,
    interaction: discord.Interaction,
    current: str,
  ) -> list[app_commands.Choice[int]]:
    with sql.connect(database="RigShift.db") as con:
      cursor: Cursor = con.cursor()
      cursor.execute(
        "SELECT RBXuserID FROM OffenderStats WHERE CAST(RBXuserID AS TEXT) LIKE ? LIMIT 25",
        (f"{current}%",)
      )
      db_results = cursor.fetchall()

    choices = []
    for row in db_results:
      user_id = row[0]
      rbxinfo = await GetRBXUserData(offenderID=user_id, session=self.bot.session)
      username = rbxinfo.get("name", f"User {user_id}")
    
      choices.append(
        app_commands.Choice(name=str(username), value=user_id)
      )

    return choices

  @admin_group.command(name="add-offenderstat", description="add stat to offender")
  @app_commands.checks.cooldown(rate=2, per=35.5, key=lambda i: i.user.id)
  @app_commands.describe(
    who = "Offender Roblox ID"
  )
  @app_commands.autocomplete(who=offender_autocomplete)
  @app_commands.checks.has_any_role(*SpecialRoles)
  @app_commands.choices(stat_type=[
    app_commands.Choice(name="Permanentban Count", value="PermabanCount"),
    app_commands.Choice(name="Temporaryban Count", value="TempbanCount"),
    app_commands.Choice(name="Serverban Count", value="ServerbanCount")
  ])
  async def Add_OffenderStat(
    self, 
    interaction: discord.Interaction,
    who: int,
    stat_type: app_commands.Choice[str]
  ):
    await interaction.response.defer(thinking=True)
    offenderRBXinfo = await GetRBXUserData(who, self.bot.session)
    isReg, data = await GetOffenderStat(who, "*")
    if isReg == False:
      await interaction.followup.send(f"<a:rejected:{rejectID}> Offender is not registered!", ephemeral=True)
      return
    success = await IncreaseOffenderStat(who, stat_type.value)
    if success:
      await interaction.followup.send(content=f"<a:approved:{approveID}> successfully added **1** to **{offenderRBXinfo.get("name")}**'s **{stat_type.name}**!")
      owner= await self.bot.fetch_user(self.bot.owner_id)
      await owner.send(f"{interaction.user.name} added 1 to {offenderRBXinfo.get("name")}'s {stat_type.name}\n\n Server: {interaction.guild}")
    else:
      await interaction.followup.send("Faced with an error while increasing stat!")
      
  @Add_OffenderStat.error
  async def Add_OffenderStat_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingAnyRole):
      await interaction.response.send_message(
        f"<a:rejected:{denyEmojiID}> You don't have the required roles to use this command.", 
        ephemeral=True
      )
    elif isinstance(error, app_commands.CommandOnCooldown):
      await interaction.response.send_message(
        f"⏳ Please wait {error.retry_after:.1f} seconds before using this command again.", 
        ephemeral=True
      )  
  
  @admin_group.command(name="remove-offenderstat", description="add stat to offender")
  @app_commands.checks.cooldown(rate=2, per=35.5, key=lambda i: i.user.id)
  @app_commands.describe(
    who = "Offender Roblox ID"
  )
  @app_commands.autocomplete(who=offender_autocomplete)
  @app_commands.checks.has_any_role(*SpecialRoles)
  @app_commands.choices(stat_type=[
    app_commands.Choice(name="Permanentban Count", value="PermabanCount"),
    app_commands.Choice(name="Temporaryban Count", value="TempbanCount"),
    app_commands.Choice(name="Serverban Count", value="ServerbanCount")
  ])
  async def Remove_OffenderStat(
    self, 
    interaction: discord.Interaction,
    who: int,
    stat_type: app_commands.Choice[str]
  ):
    await interaction.response.defer(thinking=True)
    offenderRBXinfo = await GetRBXUserData(who, self.bot.session)
    isReg, data = await GetOffenderStat(who, "*")
    if isReg == False:
      await interaction.followup.send(f"<a:rejected:{rejectID}> Offender is not registered!", ephemeral=True)
      return
    success = await DecreaseOffenderStat(who, stat_type.value)
    if success:
      await interaction.followup.send(content=f"<a:approved:{approveID}> successfully removed **1** from **{offenderRBXinfo.get("name")}**'s **{stat_type.name}**!\n Offender ID: `{who}`")
      owner= await self.bot.fetch_user(self.bot.owner_id)
      await owner.send(f"{interaction.user.name} removed 1 from {offenderRBXinfo.get("name")}'s {stat_type.name}\n Offender ID: `{who}` \n\n Server: {interaction.guild}")
    else:
      await interaction.followup.send("Faced with an error while increasing stat!")

  @Remove_OffenderStat.error
  async def Remove_OffenderStat_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingAnyRole):
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
  await bot.add_cog(AdminCommands(bot))
