"""
Helpers for printing piped lines and `print_piped_line()`
"""

from rich.console import Console
from rich.text import Text

from ...config import SIZE, HEX_CODE_REGEX, MIN_TERM_WIDTH
from ....sql.exceptions import FieldError

from typing import Literal

from re import fullmatch


def ne_print(string: str) -> None:
    """
    prints a string without a newline
    """
    print(string, end='')



def calc_line_spacing(string: str,
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


def handle_spacing(outer_space: int,
                    inner_space: int,
                    use_extra: bool,
                    side: Literal['l', 'r', 'c'] = 'l',
                    is_first: bool = True,
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
    if is_first:
        if side == 'l':
            # we need outer space
            ne_print(f'{' ' * outer_space}║{' ' * inner_space}')


        else:
            # no outer space
            ne_print(f'{col_sep}{' ' * inner_space}')


        if use_extra or (side == 'c' and use_extra):
            ne_print(' ')
            use_extra = not use_extra


    # right of the text
    else:
        ne_print(f'{' ' * inner_space}{' ' if use_extra else ''}')

        if side == 'r':
            # move to a newline
            print('║')


    return use_extra



def print_str(console: Console,
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
            'Error [lines.py, print_str] Cannot use hex_code with default_colouring = True'
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


def print_formatted_text(console: Console,
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
    if len(split_string) != 2:
        raise ValueError((
                          'ERROR WITH _print_formatted_text: Invalid '
                          f'string {string!r}. Must contain a colon (:).'
                        ))

    # first string is bold
    ne_print(f'{split_string[0]}:')

    # now second string
    print_str(console, split_string[1], hex_colour, bold = True, default_colouring = default_colouring)


# bring it all together
def print_piped_line(console: Console,
                     string: str,
                     side: Literal['l','r','c'],
                     hex_colour: str | None = None,
                     width: int = 58,
                     outer_space: int | None = None,
                     default_colouring: bool = False,
                     cols: int = 2
                    ) -> None:

    # quick input validation
    if side not in ['l', 'r', 'c']:
        raise ValueError(
            f"Invalid side choice {side!r}. Must be 'l', 'r', or 'c'."
        )


    # calculate spacing
    outer_space, inner_space, use_extra = calc_line_spacing(
                                                string, width, outer_space
                                            )

    # handle spacing on left side of line
    use_extra = handle_spacing(
                    outer_space, inner_space,
                    use_extra, side, True, cols
                )

    # print line
    print_formatted_text(
                         console,
                         string,
                         hex_colour,
                         default_colouring
                        )

    # print right space
    use_extra = handle_spacing(
                    outer_space, inner_space,
                    use_extra, side, False, cols
                )



__all__ = [
    'print_piped_line', 'Literal', 'FieldError',
    'MIN_TERM_WIDTH'
]
