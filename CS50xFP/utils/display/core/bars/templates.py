"""
Functions and classes for rendering bars (eg. ACS)
"""

from rich.console import Console

from .lines import *
from . import null_processors

from ...config import (CLEAR_LVL_COLOURS, SIZE,
                       CONT_CLASS_COLOURS)
                       CONT_CLASS_COLOURS, MIN_TERM_WIDTH)
from ....sql.models import Models

from typing import cast

# ACS et al. bar template
class BarTemplate:
    """
    Template for bars used in user/site/SCP/MTF display
    """

    def __init__(self,
                 has_center_column: bool = False,
                 width: int = MIN_TERMINAL_WIDTH,
                 console: Console | None = None
                ) -> None:
        self.has_center_column = has_center_column
        self.width = width
        self.console = console if console else Console()
        self.left_align = ' ' * ((SIZE - MIN_TERMINAL_WIDTH) // 2)

        if has_center_column:
            tmp = 3 # 3 columns
        else:
            tmp = 2 # 2 columns

        length = (width - 2) // tmp
        if (length * tmp) + 2 != width:
            raise FieldError(
                             'width',
                             width,
                             f'a multiple of {tmp} plus 2'
                            )

        rept = '═' * length

        self.length = length
        self.cols = tmp

        if has_center_column:
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
        """
        try:
            self.console.print(f'{self.left_align}{self.sep[pos]}')
        except KeyError:
            raise FieldError(
                'pos', pos,
                "'t', 'm', or 'b'"
            )


    def render_line(self,
                    # most complicated type you'll ever see :)
                    # (args for print_piped line)
                    texts: list[str],
                    hex_colours: list[str | None],
                    default_colourings: list[bool],
                    cols: int,
                    sides: list[Literal['l', 'c', 'r']] | None = None
                   ) -> None:

        # set default
        if sides is None and not self.has_center_column:
            # alternate left and right
            sides = ['l', 'r'] * (len(texts) // 2) # type: ignore
        elif sides is None and self.has_center_column:
            # alternate left, center, right
            sides = ['l', 'c', 'r'] * (len(texts) // 3) # type: ignore

        # update type
        sides = cast(list[Literal['l', 'c', 'r']], sides)

        # input validation
        if self.has_center_column and (n := len(texts)) != 3:
            raise ValueError(f'Expected 3 columns, got {n}')


        if not len(texts) == len(sides) == len(hex_colours)\
                == len(default_colourings):
            raise ValueError('All argument lists must be of equal length')


        # print each line
        for i in range(len(texts)):
            print_piped_line(
                             console=self.console,
                             string=texts[i],
                             side=sides[i],
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
    Displays a SCP after requested by user
    """

    base = BarTemplate(console = out_console)

    # === Process null values ===
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
                       CLEAR_LVL_COLOURS[5],
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
