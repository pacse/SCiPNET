"""
Helpers for display functions

Included in *:
- printc()
- print_lines()
- clear()
- timestamp()
- f_id()

Excluded from *:
- all imports
"""

from .config import SIZE

from os import name, system
from datetime import datetime

def f_id(id: int) -> str:
    """
    Formats a file id to be 3 digits with leading zeros
    """
    return f'{id:03}'

# helpers
def printc(
           string: str,
           end: str = '\n',
           flush: bool = False
          ) -> None:
  """
  prints {string} centered to the terminal size
  """
  print(string.center(SIZE), end=end, flush=flush)

def print_lines(
                lines: list[str]
               ) -> None:
    """
    printc's all lines provided
    """
    for line in lines:
        if line == '':
            print()
        else:
            printc(line)


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

__all__ = [
    'printc',
    'print_lines',
    'clear',
    'timestamp',
    'f_id'
]
