import sqlite3 as sql

async def RegisterStaff(StaffID: int) -> bool:
  with sql.connect("RigShift.db") as con:
    cursor = con.cursor()

    cursor.execute(
      "INSERT INTO StaffStats (userID) VALUES (?)", (StaffID,)
    )
    con.commit()
    return True
  

async def GetStaffStat(StaffID: int, Stat: str) -> bool | tuple:
  with sql.connect("RigShift.db") as con:
    cursor = con.cursor()

    query_stat = "TempbanCount, PermabanCount, ServerbanCount" if Stat == "*" else Stat
    cursor.execute(
      f"SELECT {query_stat} from StaffStats WHERE userID = ?",(StaffID,)
    )
    data = cursor.fetchone()
    
    if not data:
      return False, (0,0,0)
    return True, data
       

async def AddBan(
  OffenderId: int, 
  ModeratorId: int, 
  Type: str, Reason: str, Duration: str = "N/A") -> bool:
  with sql.connect("RigShift.db") as con:
    cursor = con.cursor()
    cursor.execute("INSERT INTO Bans (OffenderID, ModeratorID, BanType, BanReason, BanDuration) VALUES (?,?,?,?,?)", (OffenderId,ModeratorId,Type,Reason,Duration))
    con.commit()
    return True

async def IncreaseStaffStat(StaffID: int, Stat: str) -> bool:
  with sql.connect("RigShift.db") as con:
    cursor = con.cursor()
    
    cursor.execute(
      f"UPDATE StaffStats SET {Stat} = {Stat} + 1 WHERE userID = ? ", (StaffID,)
    )
    con.commit()

# OFFENDER SECTION

async def RegisterOffender(OffenderID: int) -> bool:
  with sql.connect("RigShift.db") as con:
    cursor = con.cursor()

    cursor.execute(
      "INSERT INTO OffenderStats (RBXuserID) VALUES (?)", (OffenderID,)
    )
    con.commit()
    return True

async def IncreaseOffenderStat(OffenderID: int, Stat: str) -> bool:
  with sql.connect("RigShift.db") as con:
    cursor = con.cursor()
    
    cursor.execute(
      f"UPDATE OffenderStats SET {Stat} = {Stat} + 1 WHERE RBXuserID = ? ", (OffenderID,)
    )
    con.commit()

async def GetOffenderStat(OffenderID: int, Stat: str) -> bool | tuple:
  with sql.connect("RigShift.db") as con:
    cursor = con.cursor()

    query_stat = "TempbanCount, PermabanCount, ServerbanCount" if Stat == "*" else Stat
    cursor.execute(
      f"SELECT {query_stat} from OffenderStats WHERE RBXuserID = ?",(OffenderID,)
    )
    data = cursor.fetchone()
    
    if not data:
      return False, (0,0,0)
    return True, data