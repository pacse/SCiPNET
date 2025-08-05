from rich.console import Console
from os import get_terminal_size as gts

# TODO: Control auto text colouring
# TODO: proper box widths, add space on right for 
# left box, add space of left for right box
# TODO: Seperate boxes
# TODO: make readable
# TODO: usr funcs for repeated processes

console = Console()

SIZE = gts().columns if gts().columns % 2 == 0 else gts().columns-1

scp_id = 2
clss_lvl = f"Level {str(6)} - COSMIC Top Secret"

cnt_clss = f"Uncontained"
scnd_clss = f"Thaumeal"

dsrpt_clss = f"Level {str(2)} - Vlam"
rsk_clss = f"Level {str(1)} - Notice"

site_resp = f"Site-{str(120)}" # not site name, just "Site-{site_id}"
#site_resp = f"Research and Containment Site-{str(12)}"

a_mtf = f"Epsilon-11 ('Nine-Tailed Fox')"

def printc(string: str) -> None:
  '''
  prints {string} centered to the terminal size
  '''
  print(f"{string:^{SIZE}}")


# long string we'll use a lot
repeated = "─" * 118
ctr_spacing = " " * ((SIZE - 120) // 2)

# printing the ACS bar
print()
printc(f"┌{repeated}┐") # top box line

# === first row ===

# spacings
item_num_len = len(f"Item #: SCP-{scp_id:03}")
item_num_spacing = " " * round((58 - item_num_len) / 2)

cl_len = len(f"Classification Level: {clss_lvl}")
cl_spacing = " " * round((58 - cl_len) / 2)



# item #: SCP-XXXX
console.print(f"{ctr_spacing}|{item_num_spacing}Item #: [bold]SCP-{scp_id:03}[/bold]",end="")

# item # spacing and clearance lvl spacing
print(f"{item_num_spacing}||{cl_spacing}", end="")

# Classification Level: Level X - COSMIC Top Secret
console.print(f"Classification Level: [#850005 bold]{clss_lvl}[/]{cl_spacing}|")


# seperating line
printc(f"├{repeated}┤")

# === second row ===

# spacings
cnt_clss_len = len(f"Containment Class: {cnt_clss}")
cc_spacing = " " * round((58 - cnt_clss_len) / 2)

scnd_clss_len = len(f"Secondary Class: {scnd_clss}")
sc_spacing = " " * round((58 - scnd_clss_len) / 2)

rsk_clss_len = len(f"Risk Class: {rsk_clss}")
rc_spacing = " " * round((58 - rsk_clss_len) / 2)

dsrpt_clss_len = len(f"Disruption Class: {dsrpt_clss}")
dc_spacing = " " * round((58 - dsrpt_clss_len) / 2)

# first line: | Containment Class: X || Disruption Class: X |
console.print(f"{ctr_spacing}|{cc_spacing}Containment Class: [#C00233 bold]{cnt_clss}[/]",end="")

# spacing and mid break
print(f"{cc_spacing}||{dc_spacing}", end="")

# print DC
console.print(f"Disruption Class: [#0087bd bold]{dsrpt_clss}[/]{dc_spacing}|")


# second line: Secondary Class: | X || Risk Class: Level X - X |

# print SC
console.print(f"{ctr_spacing}|{sc_spacing}Secondary Class: [#009f6b bold]{scnd_clss}[/]", end=" ")

# spacing and mid break
print(f"{sc_spacing}||{rc_spacing}", end="")

# print RC
console.print(f"Risk Class: [#ff6f00 bold]{rsk_clss}[/]{rc_spacing}|")

# seperating line
printc(f"├{repeated}┤")

# final row: | Site Responsible: Site-X | Assigned MTF: MTF Epsilon-6 "Village Idiots" |

# spacing
site_resp_len = len(f"Site Responsible: {site_resp}")
sr_spacing = " " * round((58 - site_resp_len) / 2)

atf_len = len(f"Assigned MTF: {a_mtf}")
atf_spacing = " " * round((58 - atf_len) / 2)

console.print(f"{ctr_spacing}|{sr_spacing}Site Responsible: [bold]{site_resp}[/]{sr_spacing}||", end="") # use rick.text.Text for no code colouring

console.print(f"{atf_spacing}Assigned MTF: [bold]{a_mtf}[/]{atf_spacing}|")

# end line
printc(f"└{repeated}┘") # top box line

print(" ")