from rich.console import Console
from typing import Literal

from .lines import print_piped_line
from ...config import SIZE, MIN_TERM_WIDTH

from ....sql.exceptions import FieldError


class BarTemplate:
    """
    Template for rendering user/site/SCP/MTF display bars

    Args:
        console (Console | None): Console to print to
        has_center_column (bool): does the bar has a center column
        width (int): Total width of the bar
        is_acs (bool): is this the acs bar
    """

    def __init__(self,
                 console: Console | None = None,
                 has_center_column: bool = False,
                 width: int = MIN_TERM_WIDTH,
                 is_acs: bool = False
                ) -> None:

        # === Init basic self vars ===
        self.is_acs = is_acs                                    # is this the acs bar
        self.width = width                                      # total width of bar
        self.console = console if console else Console()        # Console to print to
        self.left_align = ' ' * ((SIZE - MIN_TERM_WIDTH) // 2)  # spaces to left align
        self.cols = 3 if has_center_column else 2               # number of columns


        # === Handle length calculation ===
        col_len = (width - 2) // self.cols

        if (col_len * self.cols) + 2 != width:
            raise FieldError(
                             'width', width,
                             f'a multiple of {self.cols} plus 2'
                            )

        self.length = col_len
        rept = '═' * col_len


        # === Handle column stuff ===
        if has_center_column:
            self.sides = ['l', 'c', 'r']
            self.sep = {
                        't':f'╔{rept}╦{rept}╦{rept}╗',
                        'm':f'╠{rept}╬{rept}╬{rept}╣',
                        'b':f'╚{rept}╩{rept}╩{rept}╝'
                       }

            if not is_acs: # ACS is slightly different
                self.sep['t']  = f'╔{rept}═{rept}═{rept}╗'
                self.sep['m'] = f'╠{rept}╦{rept}╦{rept}╣'
        else:
            self.sides = ['l', 'r']
            self.sep = {
                        't':f'╔{rept}╗╔{rept}╗',
                        'm':f'╠{rept}╣╠{rept}╣',
                        'b':f'╚{rept}╝╚{rept}╝'
                       }

            if not is_acs: # ACS is slightly different
                self.sep['t']  = f'╔{rept}══{rept}╗'
                self.sep['m'] = f'╠{rept}╗╔{rept}╣'


        # type annotate self.sides
        self.sides: list[Literal['l', 'r', 'c']]


    # === Helper Method ===
    def _render_sep(self,
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
            raise FieldError('pos', pos, "'t', 'm', or 'b'")


    # === Main Method ===
    def render_lines(self,
                    texts: list[str],
                    hex_colours: list[str | None],
                    default_colourings: list[bool],
                   ) -> None:
        """
        Renders lines with provided texts and colourings
        using print_piped_line from ./lines.py

        Args:
            texts (list[str]): Texts to display
            hex_colours (list[str | None]): Hex colours for each text
            default_colourings (list[bool]): Whether to use default colouring for each text
        """

        # === Input Validation ===
        if len(texts) % self.cols != 0:
            raise FieldError(
                             'texts', texts,
                             f'a multiple of {self.cols}'
                            )

        if not len(texts) == len(hex_colours) == len(default_colourings):
            raise ValueError('All argument lists must be of equal length')


        # === Render ===
        for i in range(len(texts)):
            print_piped_line(
                             console=self.console,
                             string=texts[i],
                             side=self.sides[i % len(self.sides)],
                             hex_colour=hex_colours[i],
                             width=self.length,
                             default_colouring=default_colourings[i],
                             cols=self.cols,
                            )
