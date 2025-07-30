'''
Low level functions and vars
'''
from typing import TypeAlias, Any
from os import name, system
from datetime import datetime as dt

Unknown: TypeAlias = Any
'''temp type for incomplete type annotations'''


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
  gets the current timestamp
  
  format: Day/Month/Year - Hour/Minute/Second
  '''
  return dt.now().strftime("%d/%m/%Y - %H:%M:%S")