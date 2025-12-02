"""
Functions and classes for rendering bars (eg. ACS)

Contains:
- BarTemplate: Template for user/site/SCP/MTF display bars
- scp_bar: Renders an ACS bar
"""


from .null_processors import ProcessedData as PD
from .template import BarTemplate
from ...config import CLEAR_LVL_COLOURS, CONT_CLASS_COLOURS
from ...helpers import printc
from ....sql.models import Models

from rich.console import Console

# === Bar Implementations ===

def acs_bar(
            info: PD.SCP,
            console: Console | None = None
           ) -> None:
    """
    Displays an ACS-style bar for provided SCP info

    Args:
        info (ProcessedData.SCP): SCP info to display
        console (Console | None): Console to print to
    """

    # init base render class
    base = BarTemplate(console, is_acs = True)

    # === Render ===

    base._render_sep('t')

    base.render_lines(
                      [
                       f'Item #: SCP-{info.id:03d}',
                       f'Classification Level: {info.clearance_lvl.name}'
                      ],
                      [None, CLEAR_LVL_COLOURS[info.clearance_lvl.id]],
                      [True, False],
                     )

    base._render_sep('m')

    base.render_lines(
                      [
                       f'Containment Class: {info.containment_class}',
                       f'Disruption Class: {info.disrupt_class}',
                       f'Secondary Class: {info.secondary_class}',
                       f'Risk Class: {info.risk_class}'
                      ],
                      [
                       CONT_CLASS_COLOURS.get(info.containment_class),
                       processed.disrupt_class_hex,
                       CONT_CLASS_COLOURS.get(info.secondary_class),
                       processed.risk_class_hex
                      ],
                      [False] * 4,
    )

    base._render_sep('m')

    base.render_lines(
        texts = [
                 f'Site Responsible: {info.site_resp}',
                 f'Assigned MTF: {info.mtf_name}'
                ],
        hex_colours = [None] * 2,
        default_colourings = [True] * 2,
    )

    base._render_sep('b')


def site_bar(
            info: PD.Site,
            loc: str,
            console: Console | None = None
           ) -> None:
    """
    Displays a bar for provided Site info
    Args:
        info (ProcessedData.Site): Site info to display
        loc (str): Location of the site
        console (Console | None): Console to print to
    """

    # init base render class
    base = BarTemplate(console, has_center_column=True)

    # === Render ===
    base._render_sep('t')
    printc(f'║{info.name:^{base.width}}║')
    base._render_sep('m')
    base.render_lines(
                      [
                       f'ID: Site-{info.id:03d}',
                       f'Director: {info.director_str}',
                       f'Location: {loc}'
                      ],
                      [None] * 3,
                      [True] * 3,
                     )
    base._render_sep('b')


def mtf_bar(
            info: PD.MTF,
            console: Console | None = None
           ) -> None:
    """
    Displays a bar for provided MTF info
    Args:
        info (ProcessedData.MTF): MTF info to display
        console (Console | None): Console to print to
    """

    # init base render class
    base = BarTemplate(console, has_center_column=True)

    # === Render ===
    base._render_sep('t')
    printc(f'║{info.name_str:^{base.width}}║')
    base._render_sep('m')
    base.render_lines(
                      [
                       f'Assigned Site: {info.site}',
                       f'Leader: {info.leader_str}',
                       f'Active: {info.active}'
                      ],
                      [None] * 3,
                      [True] * 3,
                     )
    base._render_sep('b')


def user_bar(
             info: PD.User,
             console: Console | None = None
            ) -> None:
    """
    Displays a bar for provided User info
    Args:
        info (ProcessedData.User): User info to display
        console (Console | None): Console to print to
    """

    # init base render class
    base = BarTemplate(console)

    # === Render ===
    base._render_sep('t')
    printc(f'║{info.name_str:^{base.width}}║')
    base._render_sep('m')
    base.render_lines(
                      [
                       f'Assigned Site: {info.site}',
                       f'Clearance Level: {info.clearance}'
                      ],
                      [None] * 2,
                      [True] * 2,
                     )
    base._render_sep('b')
