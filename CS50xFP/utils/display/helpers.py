from os import name, system
from datetime import datetime
def clear() -> None:
    '''
    Clear the screen
    '''
    # OS is windows
    if name == 'nt':
        system("cls")
    # OS is mac or linux (or any other I guess, it's an else statement...)
    else:
        system("clear")


def timestamp() -> str:
  '''
  Gets the current timestamp

  Format: YYYY/MM/DD - HH/MM/SS
  '''
  curr_dt = datetime.now()
  return curr_dt.strftime("%Y/%m/%d - %H/%M/%S")
