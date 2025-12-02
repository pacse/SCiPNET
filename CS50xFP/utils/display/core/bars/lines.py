"""
Helpers for printing piped lines and `print_piped_line()`
"""


from ...config import HEX_CODE_REGEX, SIZE, MIN_TERM_WIDTH
from ....sql.exceptions import FieldError

from rich.console import Console
from rich.text import Text
from typing import Literal
from re import fullmatch



# === Helpers ===

def _ne_print(string: str) -> None:
    """ prints string without a newline """
    print(string, end='')


def _calc_line_space(
                    string: str,
                    line_width: int,
                    bar_width: int | None = None
                   ) -> tuple[int, int, bool]:
    """
    Calculate outer & inner spacing for piped lines
    as well as whether or not an extra space is needed
    for centering

    returns (outer_space, inner_space, use_extra)
    """
    outer_space = bar_width if bar_width else (SIZE - MIN_TERM_WIDTH) // 2

    inner_space = (line_width - len(string)) // 2

    # do we need extra space?
    if inner_space * 2 != (line_width - len(string)):
        use_extra = True
    else:
        use_extra = False

    return outer_space, inner_space, use_extra

def _handle_space(
                 outer_space: int,
                 inner_space: int,
                 use_extra: bool,
                 side: Literal['l', 'r', 'c'] = 'l',
                 is_left: bool = True,
                 cols: int = 2
                ) -> bool:

    """
    Handles line spacing logic
    """
    # input validation
    if side not in ['l', 'r', 'c']:
        raise FieldError(
            'side', side, "'l', 'r', or 'c'"
        )

    if cols not in [2, 3]:
        raise FieldError(
            'columns', cols, '2 or 3'
        )


    # column seperator to use
    col_sep = {2:'║║', 3:'║'}[cols]

    # left of the text
    if is_left:
        if side == 'l':
            # we need outer space
            _ne_print(f'{' ' * outer_space}║{' ' * inner_space}')


        else:
            # no outer space
            _ne_print(f'{col_sep}{' ' * inner_space}')


        if use_extra or (side == 'c' and use_extra):
            _ne_print(' ')
            use_extra = not use_extra


    # right of the text
    else:
        _ne_print(f'{' ' * inner_space}{' ' if use_extra else ''}')

        if side == 'r':
            # move to a newline
            print('║')


    return use_extra


def _print_str(
               console: Console,
               string: str,

               hex_code: str | None = None,
               bold: bool = True,
               default_colouring: bool = False,

               end: str = ''
              ) -> None:
    """
    prints `string` to `console` with
    optional `hex_code` colouring.

    Overrides default markdown colouring if `hex_code` is provided
    """
    # validate hex_code
    if hex_code and not fullmatch(HEX_CODE_REGEX, hex_code):
        raise ValueError(f'Invalid hex code {hex_code!r}')

    # other validation
    if hex_code and default_colouring:
        raise ValueError(
            'Cannot use hex_code with default_colouring = True'
        )


    # build style string
    if hex_code:
        style_str = f'{hex_code} bold'

    elif bold:
        style_str = 'bold'

    elif not default_colouring:
        style_str = None



    # print
    if not default_colouring:
        console.print(Text(string), style = style_str, end = end)
    else:
        console.print(string, style = style_str, end = end)


def _print_formatted_text(
                         console: Console,
                         string: str,
                         hex_colour: str | None = None,
                         default_colouring: bool = False
                        ) -> None:
    """
    Formats text for piped line printing
    """
    # formatting only applies after the colon
    split_string = string.split(':', 1)

    # input validation
    if len(split_string) != 2 or ':' in split_string[1]:
        raise ValueError((
                          'ERROR WITH _print_formatted_text: Invalid string'
                          f' {string!r}. Must contain a single colon (:).'
                        ))

    # first string is bold
    _ne_print(f'{split_string[0]}:')

    # now second string
    _print_str(
               console, split_string[1], hex_colour,
               True, default_colouring
              )



# === Main Function ===

def print_piped_line(console: Console,
                     string: str,
                     side: Literal['l', 'r', 'c'],
                     hex_colour: str | None = None,
                     width: int = 58,
                     outer_space: int | None = None,
                     default_colouring: bool = False,
                     cols: int = 2
                    ) -> None:
    """
    Renders a piped line to the console

    eg "  ║    Example: Text Here    ║   "

    Args:
        console: Console to print to
        string: Text to print
        side: Side to align text to ('l', 'r', 'c')
        hex_colour: Optional hex colour code for text
        width: Width of the line (default 58)
        outer_space: Optional outer spacing (default calculated)
        default_colouring: Whether or not to use default console colouring
        cols: Number of columns (2 or 3)
    """

    # input validation
    if side not in ['l', 'r', 'c']:
        raise ValueError(
            f"Invalid side choice {side!r}. Must be 'l', 'r', or 'c'."
        )


    # calculate spacing
    outer_space, inner_space, use_extra = _calc_line_space(
                                                string, width, outer_space
                                            )

    # handle spacing on left side of line
    use_extra = _handle_space(
                    outer_space, inner_space,
                    use_extra, side, True, cols
                )

    # print line
    _print_formatted_text(
                         console,
                         string,
                         hex_colour,
                         default_colouring
                        )

    # print right space
    use_extra = _handle_space(
                    outer_space, inner_space,
                    use_extra, side, False, cols
                )
