"""
Functions and classes for rendering bars (eg. ACS)

Contains:
- BarTemplate: Template for user/site/SCP/MTF display bars
- scp_bar: Renders an ACS bar
"""

from rich.console import Console

from .lines import print_piped_line
from . import null_processors

from ...config import (CLEAR_LVL_COLOURS, SIZE,
                       CONT_CLASS_COLOURS, MIN_TERM_WIDTH)
from ....sql.models import Models
from ....sql.exceptions import FieldError

from typing import Literal


# ACS et al. bar template
class BarTemplate:
    """
    Template for rendering user/site/SCP/MTF display bars

    Args:
        has_center_column (bool): Whether the bar has a center column
        width (int): Total width of the bar
        console (Console | None): Console to print to
    """

    def __init__(self,
                 has_center_column: bool = False,
                 width: int = MIN_TERM_WIDTH,
                 console: Console | None = None
                ) -> None:


        # === Init self variables ===
        self.cols: Literal[2, 3] = 3 if has_center_column else 2  # number of columns
        self.width = width                                        # total width of bar
        self.console = console if console else Console()          # Console to print to
        self.left_align = ' ' * ((SIZE - MIN_TERM_WIDTH) // 2)    # spaces to left align


        # === Handle length calculation ===
        length = (width - 2) // self.cols

        if (length * self.cols) + 2 != width:
            raise FieldError(
                             'width',
                             width,
                             f'a multiple of {self.cols} plus 2'
                            )

        self.length = length


        # === Prepare separator lines ===
        rept = '═' * length

        if self.cols == 3:
            self.sep = {
                        't':f'╔{rept}╦{rept}╦{rept}╗',
                        'm':f'╠{rept}╬{rept}╬{rept}╣',
                        'b':f'╚{rept}╩{rept}╩{rept}╝'
                       }
        else:
            self.sep = {
                        't':f'╔{rept}╗╔{rept}╗',
                        'm':f'╠{rept}╣╠{rept}╣',
                        'b':f'╚{rept}╝╚{rept}╝'
                       }



    def render_sep(self,
                   pos: Literal['t', 'm', 'b']
                  ) -> None:
        """
        Renders a separator line

        Args:
            pos ('t', 'm', 'b'): Position of separator
        """
        try:
            self.console.print(f'{self.left_align}{self.sep[pos]}')

        except KeyError:
            raise FieldError(
                'pos', pos,
                "'t', 'm', or 'b'"
            )


    def render_line(self,
                    texts: list[str],
                    hex_colours: list[str | None],
                    default_colourings: list[bool],
                    cols: int,
                    sides: list[Literal['l', 'c', 'r']] | None = None
                   ) -> None:
        """
        Renders a line with given texts and colourings
        (Utilises print_piped_line from ./lines.py)
        """

        # set default
        if sides is None:
            if self.cols == 2:
                # left and right
                sides = ['l', 'r']
            else:
                # left, center, right
                sides = ['l', 'c', 'r']


        # input validation
        if len(texts) % self.cols != 0:
            raise FieldError(
                'texts',
                texts,
                f'a multiple of {self.cols}'
            )

        if not len(texts) == len(sides) == len(hex_colours)\
                == len(default_colourings):
            raise ValueError('All argument lists must be of equal length')


        # print each line
        for i in range(len(texts)):
            print_piped_line(
                             console=self.console,
                             string=texts[i],
                             side=sides[i % len(sides)],
                             hex_colour=hex_colours[i],
                             width=self.length,
                             default_colouring=default_colourings[i],
                             cols=cols,
                            )



# bar implementations
def scp_bar(
            info: Models.SCP,
            out_console: Console | None = None
           ) -> None:
    """
    Displays an ACS-style SCP bar for provided SCP info
    """

    # init base render class
    base = BarTemplate(console = out_console)


    # process null values
    processed = null_processors.scp(info)


    # === Render ===

    base.render_sep('t')

    base.render_line(
        texts = [
                 f'Item #: SCP-{info.id:03d}',
                 f'Classification Level: {info.clearance_lvl.name}'
                ],
        hex_colours = [None, CLEAR_LVL_COLOURS[info.clearance_lvl.id]],
        default_colourings = [True, False],
        cols = base.cols
    )

    base.render_sep('m')

    base.render_line(
        texts = [
                 f'Containment Class: {info.containment_class.name}',
                 f'Disruption Class: {processed.disrupt_class}',
                 f'Secondary Class: {processed.secondary_class}',
                 f'Risk Class: {processed.risk_class}'
                ],
        hex_colours = [
                       CONT_CLASS_COLOURS.get(info.containment_class.name),
                       processed.disrupt_class_hex,
                       CONT_CLASS_COLOURS.get(processed.secondary_class),
                       processed.risk_class_hex
                      ],
        default_colourings = [False] * 4,
        cols = base.cols
    )

    base.render_sep('m')

    base.render_line(
        texts = [
                 f'Site Responsible: {processed.site_resp}',
                 f'Assigned MTF: {processed.mtf_name}'
                ],
        hex_colours = [None] * 2,
        default_colourings = [True] * 2,
        cols = base.cols
    )

    base.render_sep('b')



__all__ = [
           'scp_bar'
           # more as implemented
          ]
