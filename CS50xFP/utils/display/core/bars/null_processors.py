"""
Helpers to process null values for bar templates
"""
from ....sql.models import Models
from ...config import CLEAR_LVL_COLOURS

from dataclasses import dataclass


# dataclasses for processed data
class ProcessedData:
    @dataclass
    class SCP:
        site_resp: str
        mtf_name: str
        secondary_class: str

        disrupt_class: str
        disrupt_class_hex: str | None

        risk_class: str
        risk_class_hex: str | None


def scp(
        info: Models.SCP
       ) -> ProcessedData.SCP:

    if info.site_responsible_id:
        site_resp = f'Site-{info.site_responsible_id:03d}'
    else:
        site_resp = '[DATA EXPUNGED]'

    if info.mtf:
        mtf_name = (f"{info.mtf.name} '{info.mtf.nickname}'"
                    f' (ID: {info.mtf.id:03d})')
    else:
        mtf_name = 'None'

    if info.secondary_class:
        scnd_class = info.secondary_class.name
    else:
        scnd_class = 'None'

    if info.disruption_class:
        disrupt_class = info.disruption_class.name
        disrupt_class_hex = CLEAR_LVL_COLOURS[info.disruption_class.id]
    else:
        disrupt_class = '[DATA EXPUNGED]'
        disrupt_class_hex = None

    if info.risk_class:
        risk_class = info.risk_class.name
        risk_class_hex = CLEAR_LVL_COLOURS[info.risk_class.id]
    else:
        risk_class = '[DATA EXPUNGED]'
        risk_class_hex = None

    return ProcessedData.SCP(
        site_resp=site_resp,
        mtf_name=mtf_name,
        secondary_class=scnd_class,
        disrupt_class=disrupt_class,
        disrupt_class_hex=disrupt_class_hex,
        risk_class=risk_class,
        risk_class_hex=risk_class_hex
    )


__all__ = [
           'scp'
           # more as implemented
        ]
