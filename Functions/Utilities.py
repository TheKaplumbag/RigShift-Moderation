import requests
import json

def IsValidID(offenderID: int) -> bool:
  RBXapi = f"https://users.roblox.com/v1/users/{offenderID}"
  response = requests.get(RBXapi)
  if response.status_code == 200:
    return True
  else:
    return False

def GetRBXUserData(offenderID: int) -> bool:
  RBXapi = f"https://users.roblox.com/v1/users/{offenderID}"
  response = requests.get(RBXapi)
  if response.status_code == 200:
    data = response.json()
    return data
  else:
    return False 


def GetProfileLink(offenderID: int) -> str:
  isValid = IsValidID(offenderID=offenderID)
  if isValid:
    RBXprofileLink = f"https://roblox.com/users/{offenderID}/profile"
    return RBXprofileLink
  else:
    return f"**{offenderID}** is NOT valid roblox user!"