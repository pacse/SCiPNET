"""
Functions and classes for rendering bars (eg. ACS)

Contains:
- BarTemplate: Template for user/site/SCP/MTF display bars
- scp_bar: Renders an ACS bar
"""


from . import null_processors
from .template import BarTemplate
from ...config import CLEAR_LVL_COLOURS, CONT_CLASS_COLOURS
from ....sql.models import Models

from rich.console import Console

# === Bar Implementations ===

def acs_bar(
            info: Models.SCP,
            console: Console | None = None
           ) -> None:
    """
    Displays an ACS-style bar for provided SCP info

    Args:
        info (Models.SCP): SCP info to display
        console (Console | None): Console to print to
    """

    # init base render class
    base = BarTemplate(console)

    # process null values
    processed = null_processors.scp(info)


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
                       f'Containment Class: {info.containment_class.name}',
                       f'Disruption Class: {processed.disrupt_class}',
                       f'Secondary Class: {processed.secondary_class}',
                       f'Risk Class: {processed.risk_class}'
                      ],
                      [
                       CONT_CLASS_COLOURS.get(info.containment_class.name),
                       processed.disrupt_class_hex,
                       CONT_CLASS_COLOURS.get(processed.secondary_class),
                       processed.risk_class_hex
                      ],
                      [False] * 4,
    )

    base._render_sep('m')

    base.render_lines(
        texts = [
                 f'Site Responsible: {processed.site_resp}',
                 f'Assigned MTF: {processed.mtf_name}'
                ],
        hex_colours = [None] * 2,
        default_colourings = [True] * 2,
    )

    base._render_sep('b')


def site_bar(
            info: Models.Site,
            console: Console | None = None
           ) -> None:
    """
    Displays a bar for provided Site info
    Args:
        info (Models.Site): Site info to display
        console (Console | None): Console to print to
    """

    # init base render class
    base = BarTemplate(console)

    # 

    # === Render ===

