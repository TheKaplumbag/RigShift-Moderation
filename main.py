import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import sqlite3 as sql

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

  async def setup_hook(self):
    await self.load_extension("Cogs.MainCog")

    
    await self.tree.sync()
    print("Synced global commands")
    
    if DEV_GUILD and DEV_GUILD.isdigit():
      guild = discord.Object(id=int(DEV_GUILD))

      self.tree.copy_global_to(guild=guild)
      await self.tree.sync(guild=guild)
      
      print(f"Synced commands to DEV_GUILD={DEV_GUILD}")

if __name__=="__main__":
  if not TOKEN:
    raise SystemExit("NO TOKEN FOUND INSIDE .env!")

  bot = Bot()
  bot.run(TOKEN)