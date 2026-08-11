from typing import Any
import aiohttp

async def IsValidID(offenderID, session=None) -> bool:
  RBXapi = f"https://users.roblox.com/v1/users/{offenderID}"
  
  close_session = False
  if session is None:
    session = aiohttp.ClientSession()
    close_session = True
      
  try:
    async with session.get(RBXapi) as response:
      return response.status == 200
      
  finally:
    if close_session:
      await session.close()


async def GetRBXUserData(offenderID, session=None) -> dict[str, Any]:
  RBXapi = f"https://users.roblox.com/v1/users/{offenderID}"
  
  close_session = False
  if session is None:
    session = aiohttp.ClientSession()
    close_session = True
      
  try:
    async with session.get(RBXapi) as response:
      if response.status == 200:
        data = await response.json()
        return data
      return False
  finally:
    if close_session:
      await session.close()


async def GetProfileLink(offenderID, session=None) -> str:
  isValid = await IsValidID(offenderID=offenderID, session=session)
  
  if isValid:
    RBXprofileLink = f"https://www.roblox.com/users/{offenderID}/profile"
    return RBXprofileLink
  else:
    return f"**{offenderID}** is NOT valid roblox user!"