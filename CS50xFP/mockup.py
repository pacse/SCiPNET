# Login
from utils import printc

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
  #expunged(file_name)
  print(">>> Override Alpha Omega Gamma 7")
  printc("Overriding. . .")
  print()
  #sp(uf(0, 1))
  #redacted(file_name)
  print(">>> Override Episilon Lambda Chi 4")
  printc("Overriding. . .")
  #granted(file_name)