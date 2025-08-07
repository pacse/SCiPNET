from rich.console import Console
from rich.text import Text

from os import get_terminal_size as gts

console = Console()

SIZE = gts().columns if gts().columns % 2 == 0 else gts().columns-1

scp_id = 2
clss_lvl = f"Level {str(6)} - COSMIC Top Secret"

cnt_clss = f"Uncontained"
scnd_clss = f"Thaumeal"

dsrpt_clss = f"Level {str(2)} - Vlam"
rsk_clss = f"Level {str(1)} - Notice"

site_resp = f"Site-{str(120)}" # not site name, just "Site-{site_id}"

a_mtf = f"Epsilon-11 ('Nine-Tailed Fox')"

def printc(string: str) -> None:
    '''
    prints *{string}* centered to the terminal size
    '''
    print(f"{string:^{SIZE}}")

def print_piped_line(console: Console, 
                     string: str, 
                     side: str,
                     hex_colour: int | None = None,
                     width: int = 58,
                     outer_space: int = (SIZE - 120) // 2,
                     default_colouring: bool = True) -> None:
    
    # quick input validation
    assert side in ["l", "r"], f"Invalid side choice {side!r}. Must be 'l' or 'r'"

    # calculate inner space
    inner_space = (width - len(string)) // 2
    
    # do we need extra space?
    if inner_space * 2 != (width - len(string)):
        use_extra = True
    else:
        use_extra = False
    
    # print left space
    print(f"{(' ' * outer_space) if side == 'l' else ''}│{' ' * inner_space}", end="")

    # extra space for centring
    if use_extra and side == "l":
        print(" ",end="")
        # flip use extra (saves time later)
        use_extra = not use_extra

    # start printing main line
    split_string = string.split(":") # we only format after the colon
    print(f"{split_string[0]}:", end="")
    
    # now's the hard part, format

    # first get everything we want to format
    f_string = "".join(split_string[1:])
    
    # if we're not using default colouring, 
    # just print bold f_string
    if not default_colouring:
        f_string = Text(f_string)
        console.print(f_string, style = "bold", end="")
    
    # disable normal colouring if we have a hex_code
    elif hex_colour:
        f_string = Text(f_string)
        console.print(f_string, style = f"#{hex_colour:06x} bold", end="")
    
    # otherwise just bold
    else:
        console.print(f_string, style = "bold",end="")
    
    # ╰(*°▽°*)╯ yeye that wasn't that hard ╰(*°▽°*)╯
    # now rest of line
    
    # print right space
    print(f"{' ' * inner_space}{' ' if use_extra else ''}│", end="")
    
    # now do we move to a newline?
    if side == "r":
        print()

# plz work
# praise be the omnisire
# Later: it worked :))

repeated = "─" * 58

print()
printc(f"┌{repeated}┐┌{repeated}┐")
print_piped_line(console, "Item #: SCP-002", "l", None, default_colouring=False)
print_piped_line(console, "Classification Level: Level 6 - COSMIC Top Secret", "r", 0x850005)
printc(f"│{repeated}┤├{repeated}│")
print_piped_line(console, "Containment Class: Uncontained", "l", 0xC00233)
print_piped_line(console, "Disruption Class: Level 2 - Vlam", "r", 0x0087bd)
print_piped_line(console, "Secondary Class: Thaumeal", "l", 0x009f6b)
print_piped_line(console, "Risk Class: Level 1 - Notice", "r", 0xff6f00)
printc(f"│{repeated}┤├{repeated}│")
print_piped_line(console, "Site Responsible: Site-110", "l", None, default_colouring=False)
print_piped_line(console, "Assigned MTF: Epsilon-11 ('Nine-Tailed Fox')", "r", None, default_colouring=False)
printc(f"└{repeated}┘└{repeated}┘")
print(".")