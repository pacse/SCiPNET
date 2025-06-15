# Login
import socket
import sys
from time import sleep as sp
from time import time as tm
from random import uniform as uf
from utils import clear, printc, timestamp

# redacted message
def redacted(file: str) -> None:
  '''
  prints a message saying {file} is above your clearance
  art by ChatGPT
  '''
  lines = [
      "╔══════════════════════════════╗",
      "║        ACCESS DENIED         ║",
      "╚══════════════════════════════╝",
      "",
      f"FILE_REF: {file} ACCESS DENIED",
      "CLEARANCE LEVEL 6 - COSMIC TOP SECRET REQUIRED",
      "(YOU ARE CLEARANCE LEVEL 5 - TOP SECRET)",
      f"Logged to Overwatch Command at {timestamp()}",
  ]

  [printc(line) for line in lines]

# data expunged message
def expunged(file: str) -> None:
  '''
  prints a message saying {file} has been expunged
  art by ChatGPT
  '''
  lines = [
      "╔══════════════════════════════╗",
      "║        DATA EXPUNGED         ║",
      "╚══════════════════════════════╝",
      "",
      f"FILE_REF: {file} NOT FOUND",
      f"Logged to Overwatch Command at {timestamp()}",
  ]

  [printc(line) for line in lines]

# access granted message
def granted(file: str) -> None:
  '''
  prints a message saying access has been granted to a file
  art by ChatGPT
  '''
  lines = [
      "╔══════════════════════════════╗",
      "║        ACCESS GRANTED        ║",
      "╚══════════════════════════════╝",
      "",
      f"FILE_REF: {file} ACCESS GRANTED",
      f"Logged to Overwatch Command at {timestamp()}",
  ]

  [printc(line) for line in lines]

def auth_usr(id: int, password: str) -> bool:
  # TODO: Implement authentication logic
  return True

def invalid() -> None:
  printc("INVALID ID OR PASSWORD")
  sys.exit()

def conn_deepwell():
  # TODO: implement deepwell connection
  # connect to server
  # get connection to deepwell.db and return
  pass

def login(name: str, title: str, clearance: int) -> None:
  clearances = {
      1: "Unrestricted",
      2: "Restricted",
      3: "Classified",
      4: "Secret",
      5: "Top Secret",
      6: "COSMIC Top Secret",
  }
  reused1 = "/" * 4 + " " * 112 + "/" * 4
  reused2 = "/" * 120

  if title == "O5":
    lines = [
        reused2,
        reused1,
        "////" + f"{'<< O5 AUTHORIZATION VERIFIED >>':^112}" + "////",
        reused1,
        "////" + f"{'CLEARANCE LEVEL: 6 - COSMIC TOP SECRET':^112}" + "////",
        reused1,
        "////" + f"{f'Welcome back, {name}.':^112}" + "////",
        "////" + f"{f'This session is being logged by CoreNode Zero.':^112}" + "////",
        reused1,
        "////" + f"{'SYSTEM STATUS: OPERATIONAL | DEEPWELL CHANNEL ENCRYPTED':^112}" + "////",
        reused1,
        reused2,
    ]

  elif title == "Site Director":
    lines = [
        reused2,
        reused1,
        "////" + f"{'<< DIRECTOR AUTHORIZATION VERIFIED >>':^112}" + "////",
        reused1,
        "////" + f"{'CLEARANCE LEVEL: 5 - TOP SECRET':^112}" + "////",
        reused1,
        "////" + f"{f'Welcome back, {name}.':^112}" + "////",
        "////" + f"{'All actions are recorded and reviewed by O5 Liaison - Node Black':^112}" + "////",
        reused1,
        "////" + f"{'SYSTEM STATUS: OPERATIONAL | DEEPWELL CHANNEL ENCRYPTED':^112}" + "////",
        reused1,
        reused2,
    ]

  elif title == "Aministrator":
    lines = [
        reused2,
        reused1,
        "////" + f"{'<< ADMINISTRATOR AUTHORIZATION VERIFIED >>':^112}" + "////",
        reused1,
        "////" + f"{'CLEARANCE LEVEL: UNBOUNDED | OVERRIDE: UNIVERSAL | LOGGING: DISABLED':^112}" + "////",
        reused1,
        "////" + f"{'Welcome, Administrator. All systems stand by for your instruction.':^112}" + "////",
        "////" + f"{'There are no restrictions. There are no records.':^112}" + "////",
        reused1,
        "////" + f"{'SYSTEM STATUS: OPERATIONAL | ENCLAVE MODE ACTIVE':^112}" + "////",
        reused1,
        reused2,
    ]

  else:
    lines = [
        f"Welcome back, {title} {name}",
        f"(Clearance Level {clearance} - {clearances[clearance]})"
    ]

  [printc(line) for line in lines]


if __name__ == "__main__":

  # prompt for login
  print(f"Please enter your credentials")
  #id = int(input("ID >>> "))
  id = print("ID >>> ECP390623")
  #password = input("Password >>> ")
  password = print("Password >>> inSAne")

  usr_name = "Evren Cæl Packard"
  usr_title = "O5"
  usr_clearance = 5
  #sp(uf(0, 1))
  print()
  login(usr_name, usr_title, usr_clearance)
  print()

  # user actions
  file_name = "SCP-001"
  print(f">>> Access {file_name}")
  printc(f"Accessing file {file_name}. . .")
  print()
  #sp(uf(0, 1))
  expunged(file_name)
  print(">>> Override Alpha Omega Gamma 7")
  printc("Overriding. . .")
  print()
  #sp(uf(0, 1))
  redacted(file_name)
  print(">>> Override Episilon Lambda Chi 4")
  printc("Overriding. . .")
  granted(file_name)