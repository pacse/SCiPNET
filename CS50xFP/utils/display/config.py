"""
Display configuration settings and constants

Included in *:
- MIN_TERMINAL_WIDTH
- BAR_WIDTH
- BOX_SIZE
- SIZE
- CLEAR_LVL_COLOURS
- CONT_CLASS_COLOURS

Excluded from *:
- all imports
- HEX_CODE_REGEX
- OTHER_CONT_CLASS
"""

from collections import defaultdict

# disable markdown_it logging
import logging
logging.getLogger('markdown_it').setLevel(logging.WARNING)

# Mayuk numbers
MIN_TERMINAL_WIDTH = 120
"""Minimum terminal width required for proper display"""

BAR_WIDTH = 58
"""Width of bars used in user/site/SCP/MTF display"""

BOX_SIZE = 35 # fits most messages nicely
"""Default box size for boxed messages"""


"""Validate terminal size"""
try:
    from os import get_terminal_size

    SIZE = get_terminal_size().columns
    SIZE = SIZE if SIZE % 2 == 0 else SIZE-1  # type: ignore

except OSError:
    raise Exception('Could not get terminal size')
except ImportError:
    raise Exception(
        'Thou does not have files pertaining to the OS module.'
        ' Thou art a magician. HOW!'
    )

if SIZE < MIN_TERMINAL_WIDTH:
    raise Exception(
        f'Requires terminal size of {MIN_TERMINAL_WIDTH}'
        f' columns (current size {SIZE})'
        )


HEX_CODE_REGEX = r'#[0-9A-F]{6}'



CLEAR_LVL_COLOURS = [
    '',
    '#009F6B',
    '#0087BD',
    '#FFD300',
    '#FF6D00',
    '#C40233',
    '#850005'
]
"""
Hex colour codes used in clearance level rendering

index is level
(eg, COLOURS[1] is used for clearance level 1)
"""

OTHER_CONT_CLASS = '#6A6A6A'  # grey for all containment classes
"""Hex colour code used for containment classes not in CONT_CLASS_COLOURS"""

CONT_CLASS_COLOURS = defaultdict(
    lambda: OTHER_CONT_CLASS,
    {
        'Safe': CLEAR_LVL_COLOURS[1],
        'Euclid': CLEAR_LVL_COLOURS[3],
        'Keter': CLEAR_LVL_COLOURS[5],
    }
)

"""
Hex colour codes used in containment class rendering

ALWAYS USE `.get()` TO ACCESS THIS DICT

keys are containment classes
(eg, CONT_CLASS_COLOURS.get('Safe') is used for Safe class)
"""


# what's importable
__all__ = [
    'MIN_TERMINAL_WIDTH',
    'BAR_WIDTH',
    'BOX_SIZE',
    'SIZE',
    'CLEAR_LVL_COLOURS',
    'CONT_CLASS_COLOURS'
]
