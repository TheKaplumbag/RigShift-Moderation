import discord
from discord import app_commands
from discord.ext import commands
from Functions.Database import AddBan,IncreaseStaffStat,RegisterStaff,GetStaffStat, IncreaseOffenderStat, RegisterOffender, GetOffenderStat
from config import StaffRoles, BotEmojis
from Functions.Utilities import IsValidID, GetProfileLink, GetRBXUserData
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

denyEmojiID = BotEmojis.get("rejected")
approveEmojiID = BotEmojis.get("approved")
loadingID = BotEmojis.get("loading")

class StaffCommands(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  staff_group = app_commands.Group(name="staff", description="staff only commands")

  
  @staff_group.command(name="ban-log", description="Log ban")
  @app_commands.checks.has_any_role(*StaffRoles)
  @app_commands.checks.cooldown(rate=3, per=60.0, key=lambda i: i.user.id)
  @app_commands.choices(ban_type=[
    app_commands.Choice(name="Permanent", value="Permaban"),
    app_commands.Choice(name="Temporary", value="Tempban"),
    app_commands.Choice(name="Server", value="Serverban")
  ])
  @app_commands.describe(
    ban_duration = "Duration of ban",
    offender_id = "Roblox ID of offender",
    ticket_number = "Enter the ticket number leave if its not from ticket"
  )
  async def BanLog(
    self,
    interaction: discord.Interaction,
    offender_id: int,
    ban_type: app_commands.Choice[str],
    ban_reason: str,
    ban_duration: str = "N/A",
    ticket_number: str = "N/A",
    attach_evidence: discord.Attachment = None,
    attach_evidence_two: discord.Attachment = None,
    link_evidence: str = None
  ):
    await interaction.response.defer(thinking=True)

    try:
      if ban_type.value == "Tempban" and ban_duration == "N/A":
        await interaction.followup.send(content=f"<a:rejected:{denyEmojiID}> YOU CAN'T LOG Temporary Ban without specifying a duration!")
        return

      if attach_evidence is None and link_evidence is None and attach_evidence_two is None:
        await interaction.followup.send(content=f"<a:rejected:{denyEmojiID}> YOU MUST AT LEAST PROVIDE ONE EVIDENCE", ephemeral=True)
        return

      isvalid : bool = await IsValidID(offenderID=offender_id, session=self.bot.session)
      if isvalid:
        RBXProfile : str = await GetProfileLink(offenderID=offender_id, session=self.bot.session)

        response: bool = await AddBan(
          OffenderId=offender_id,
          ModeratorId=interaction.user.id,
          Type=ban_type.value,
          Reason=ban_reason,
          Duration=ban_duration
        )

        stat : str = ban_type.value + "Count"
        isStaffRegistered, staffStat = await GetStaffStat(StaffID=interaction.user.id, Stat =stat)
        isOffenderReg, offenderStat = await GetOffenderStat(OffenderID=offender_id, Stat = stat)

        if isOffenderReg == False:
          await RegisterOffender(OffenderID=offender_id)
          await IncreaseOffenderStat(OffenderID=offender_id, Stat = stat)
        else:
          await IncreaseOffenderStat(OffenderID=offender_id, Stat = stat)

        if isStaffRegistered == False:
          await RegisterStaff(StaffID=interaction.user.id)
          await IncreaseStaffStat(StaffID=interaction.user.id, Stat = stat)
        else:
          await IncreaseStaffStat(StaffID=interaction.user.id, Stat = stat)

        if response == True:
          log_channelId = int(os.getenv(key=ban_type.value + "logChannel"))
          log_channel = self.bot.get_channel(log_channelId) or await self.bot.fetch_channel(log_channelId)

          embed = discord.Embed(
            title="🔨 RIG SHIFT BAN LOG",
            description="A new ban log has been sent!",
            color=discord.Color.red(),
            timestamp= datetime.now()
          )

          data = await GetRBXUserData(offenderID=offender_id, session=self.bot.session)
          offender_name = data.get('name', 'Unknown') if isinstance(data, dict) else "Unknown"
          offender_display = data.get('displayname', 'Unknown') if isinstance(data, dict) else "Unknown"
          if offender_display == "Unknown":
            embed.add_field(name="Offender Name", value=f"[{offender_name} @{offender_name}]({RBXProfile})")
          else:
            embed.add_field(name="Offender Name", value=f"[{offender_name} @{offender_display}]({RBXProfile})")
          embed.add_field(name="Offender ID", value=f"`{offender_id}`", inline=True)
          embed.add_field(name="Ban Type", value=ban_type.name, inline=True)
          if ticket_number == "N/A":
            embed.add_field(name="Ticket Number", value=f"{ticket_number}", inline=True)
          else:
            embed.add_field(name="Ticket Number", value=f"Ticket-{ticket_number}", inline=True)
          embed.add_field(name="Duration", value=ban_duration, inline=True)
          embed.add_field(name="Reason", value=ban_reason, inline=False)

          if attach_evidence:
            embed.add_field(name="Evidence", value=attach_evidence.url, inline=False)
          if attach_evidence_two:
            embed.add_field(name="Second Evidence", value=attach_evidence_two.url, inline=False)
          if link_evidence:
            embed.add_field(name="Link evidence", value=link_evidence, inline=False)

          embed.set_footer(text=f"Logged by {interaction.user}", icon_url=interaction.user.display_avatar.url)


          files = []

          if attach_evidence:
            if attach_evidence.content_type and attach_evidence.content_type.startswith("image/"):
              embed.set_image(url=attach_evidence.url)
            else:
              files.append(await attach_evidence.to_file())

          if attach_evidence_two:
            if attach_evidence_two.content_type and attach_evidence_two.content_type.startswith("image/") and not embed.image:
              embed.set_image(url=attach_evidence_two.url)
            else:
              files.append(await attach_evidence_two.to_file())

          if files:
            await log_channel.send(
              content="<@1135915813346492468>",
              embed=embed
            )
            await log_channel.send(files=files)
          else:
            await log_channel.send(
              content="<@1135915813346492468>",
              embed=embed
            )

          await interaction.followup.send(content=f"<a:approved:{approveEmojiID}> Success!", ephemeral=True)
        else:
          await interaction.followup.send(content="PROVIDED ID DOES NOT BELONG TO ANY ROBLOX USER!", ephemeral=True)
      else:
        await interaction.followup.send(content="PROVIDED ID DOES NOT BELONG TO ANY ROBLOX USER! 2", ephemeral=True)

    except Exception as e:
      print(f"BanLog Command Error: {e}")
      await interaction.followup.send(content=f"<a:rejected:{denyEmojiID}> An error occurred while executing the command: `{e}`", ephemeral=True)
      
  @BanLog.error
  async def BanLog_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingAnyRole):
      await interaction.response.send_message(
        f"<a:rejected:{denyEmojiID}> You don't have the required roles to use this command.", 
        ephemeral=True
      )
    elif isinstance(error, app_commands.CommandOnCooldown):
      await interaction.response.send_message(
        f"<a:loading:{loadingID}> Please wait {error.retry_after:.1f} seconds before using this command again.", 
        ephemeral=True
      )
    

  @staff_group.command(name="stats", description="check your ban stats")
  @app_commands.checks.has_any_role(*StaffRoles)
  @app_commands.checks.cooldown(rate=3, per=60.0, key=lambda i: i.user.id)
  @app_commands.choices(which_stat=[
    app_commands.Choice(name="Permanentban Count", value="PermabanCount"),
    app_commands.Choice(name="Temporaryban Count", value="TempbanCount"),
    app_commands.Choice(name="Serverban Count", value="ServerbanCount"),
    app_commands.Choice(name="All", value="*")
  ])
  async def StaffBanStats(
    self, 
    interaction: discord.Interaction, 
    who: discord.Member, 
    which_stat: app_commands.Choice[str]
  ):
    await interaction.response.defer(thinking=True)
  
    if who.top_role.id in StaffRoles:
      isRegistered, data = await GetStaffStat(StaffID=who.id, Stat=which_stat.value)
      formatted = ""
      if len(data) > 1:
        formatted = f"Staff Name: {who.mention}\n Staff Rank: {who.top_role} \n Temporaryban Count: {data[0]}\n Permanentban Count: {data[1]}\n Serverban Count: {data[2]} "
      else:
        formatted = f"Staff Name: {who.mention}\n Staff Rank: {who.top_role} \n  {which_stat.name}: {data[0]}"
      if not isRegistered:
        await RegisterStaff(StaffID=who.id)
        await interaction.followup.send("Staff member was not registered. Registered now, please run the command again!")
      else:
        await interaction.followup.send(f"Stats:\n\n {formatted}")
    else:
      await interaction.followup.send("This user does not have required staff roles.")

  @StaffBanStats.error
  async def OffenderBanStats_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingAnyRole):
      denyEmojiID: int = BotEmojis.get("rejected")
      await interaction.response.send_message(
        f"<a:rejected:{denyEmojiID}> You don't have the required roles to use this command.", 
        ephemeral=True
      )
    elif isinstance(error, app_commands.CommandOnCooldown):
      await interaction.response.send_message(
        f"<a:loading:{loadingID}> Please wait {error.retry_after:.1f} seconds before using this command again.", 
        ephemeral=True
      )












async def setup(bot: commands.Bot):
  await bot.add_cog(StaffCommands(bot))