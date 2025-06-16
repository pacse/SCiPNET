# Login
from utils import printc

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