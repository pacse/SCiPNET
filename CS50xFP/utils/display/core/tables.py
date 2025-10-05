"""
Helpers for printing tables
"""

from tabulate import tabulate
from ...sql import models as Models


def print_table(data: list[dict[str,str]]) -> None:

    # Generate table with tabulate
    table_str = tabulate(
        data,
        headers='keys',
        tablefmt='fancy_grid',
        stralign='center'
    )

    # format table
    table_str = (
                table_str
                .replace('│','║').replace('╡','╣')
                .replace('╞','╠').replace('├','╟')
                .replace('┤','╢').replace('╪','╬')
                .replace('┼','╫').replace('╛','╝')
                .replace('╘','╚').replace('╧','╩')
                .replace('╕','╗').replace('╒','╔')
                .replace('╤','╦').split('\n')
                )

    # print
    for line in table_str:
        print(line)


def print_table_users(data: list[Models.User]) -> None:
    dict_data = []

    # format user (we don't need all data)
    for usr in data:
        dict_data.append({
            'ID': f'{usr.id:03d}',
            'Name': f'{usr.title.name} {usr.name}',
            'Clearance': usr.clearance_lvl.name,
            'MTF Operative': 'Yes' if usr.mtf else 'No',
            'Active': 'Yes' if usr.is_active else 'No'
        })

    # render table
    print_table(dict_data)


def print_table_scp(data: list[Models.SCP]) -> None:
    dict_data = []

    # format scp (we don't need all data)
    for scp in data:
        if scp.secondary_class:
            scnd_clss = scp.secondary_class.name
        else:
            scnd_clss = 'None'

        if scp.risk_class:
            risk_clss = scp.risk_class.name
        else:
            risk_clss = '[DATA EXPUNGED]'

        if scp.disruption_class:
            disruption_clss = scp.disruption_class.name
        else:
            disruption_clss = '[DATA EXPUNGED]'

        if scp.mtf:
            mtf_name = (f'{scp.mtf.name} '
                        f'{scp.mtf.nickname!r}'
                        f'(ID: {scp.mtf.id:03d})')
        else:
            mtf_name = 'None'

        dict_data.append({
            'ID': f'SCP-{scp.id:03d}',
            'Classification Level': scp.clearance_lvl.name,
            'Containment Class': f'{scp.containment_class.name}',
            'Secondary Class': scnd_clss,
            'Risk Class': risk_clss,
            'Disruption Class': disruption_clss,
            'Assigned MTF': mtf_name,
        })

    # render table
    print_table(dict_data)


def print_table_mtfs(data: list[Models.MTF]) -> None:
    dict_data = []

    # format mtf (we don't need all data)
    for mtf in data:
        dict_data.append({
            'ID': f'{mtf.id:03d}',
            'Name': f"{mtf.name} '{mtf.nickname}'",
            'Active': 'Yes' if mtf.active else 'No',
        })

    # render table
    print_table(dict_data)
