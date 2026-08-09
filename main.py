import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from config import Status_list
import sqlite3 as sql
import random

# INITIALIZING DATABASE
con = sql.connect("RigShift.db")
cursor = con.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS StaffStats(
  userID INTEGER PRIMARY KEY,
   TempbanCount INTEGER DEFAULT 0,
   PermabanCount INTEGER DEFAULT 0,
   ServerbanCount INTEGER DEFAULT 0
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS OffenderStats(
  RBXuserID INTEGER PRIMARY KEY,
   TempbanCount INTEGER DEFAULT 0,
   PermabanCount INTEGER DEFAULT 0,
   ServerbanCount INTEGER DEFAULT 0
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS Bans(
  BanID INTEGER PRIMARY KEY AUTOINCREMENT,
  OffenderID  INTEGER,
  ModeratorID INTEGER,
  BanType TEXT DEFAULT 'N/A',
  BanReason TEXT DEFAULT 'N/A',
  BanDuration TEXT DEFAULT 'N/A'
)""")


con.commit()
con.close()


load_dotenv()
TOKEN : str = os.getenv(key="BOT_TOKEN")
DEV_GUILD : str = os.getenv(key="DEV_GUILD")
PROXY : str = os.getenv("PROXY")

class Bot(commands.Bot):
  def __init__(self):
    Intents = discord.Intents.all()
    Intents.guilds = True

    super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=Intents,
    help_command=None,
    activity=discord.Game(name = "Staff tools") , proxy=PROXY)


  
  
  @tasks.loop(seconds=15.0)
  async def change_status(self):
    new_status : str = random.choice(*Status_list)
    await self.change_presence(
      status=discord.Status.online,
      activity=discord.CustomActivity(name=new_status),
    )


  async def setup_hook(self):
    self.change_status.start()

    await self.load_extension("Cogs.StaffCog")
    await self.load_extension("Cogs.OffenderCog")
    await self.load_extension("Cogs.AdminCog")

    try:
      if DEV_GUILD and DEV_GUILD.isdigit():
        guild = discord.Object(id=int(DEV_GUILD))
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print(f"Synced commands to DEV_GUILD={DEV_GUILD}")
      else:
        await self.tree.sync()
        print("Synced global commands")
    except discord.HTTPException as e:
      print(f"Failed to sync commands: {e}")

  @change_status.before_loop
  async def before_change_status(self):
    await self.wait_until_ready()
    

if __name__=="__main__":
  if not TOKEN:
    raise SystemExit("NO TOKEN FOUND INSIDE .env!")

  bot = Bot()
  bot.run(TOKEN)