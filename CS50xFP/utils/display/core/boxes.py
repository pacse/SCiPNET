"""
`basic_box()` and `basic_box_with_text()` for most error and info messages
"""
from ..helpers import *
from ..config import BOX_SIZE


def basic_box(lines: list[str], size: int = BOX_SIZE) -> None:
    """
    Prints a formatted box with the provided lines centered inside
    """
    # calculate box width
    box_width = size - 2

    # reused strs
    TOP_BOTTOM = '═' * box_width
    EMPTY = f'║{' ' * box_width}║'


    # generate box
    box = ['', f'╔{TOP_BOTTOM}╗', EMPTY]

    for line in lines:
        box.append(f'║{line.center(box_width)}║')

    box.append(EMPTY)
    box.append(f'╚{TOP_BOTTOM}╝')
    box.append('')

    # print box
    print_lines(box)


def basic_box_with_text(text: list[str],
                        box_text: list[str],
                        box_size: int = BOX_SIZE,
                        RAISA_log: bool = True
                       ) -> None:
    """
    Prints a formatted box with `box_text` centered
    inside followed by `text` centered below the box

    If RAISA_log is True, says the action was logged
    to RAISA @ the current timestamp
    """

    basic_box(box_text, box_size)
    print_lines(text)
    if RAISA_log:
        printc(f'Logged to RAISA at {timestamp()}')

    print()
