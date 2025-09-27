"""
BaseModels to store used information
(by client) provided by the deepwell
"""
from pydantic import BaseModel as Base


class ORMBase(Base):
    """
    BaseModel for all ORM models
    (Allows generation from SQLAlchemy models)
    """

    model_config = {
        "from_attributes": True
    }

class IDandName(ORMBase):
    """
    BaseModel to store an id and name pair
    """
    id: int
    name: str

class User(ORMBase):
    """
    BaseModel to store user information
    """
    id: int
    name: str
    clearance_level: IDandName
    title: IDandName
    site_id: int

class Site(ORMBase):
    id: int
    name: str
    director: User | None = None



class MTF(ORMBase):
    id: int
    name: str
    nickname: str
    leader: User | None = None
    site: Site | None = None
    active: bool


class SCP_Colours(Base):
    """
    BaseModel to store hex colour
    codes for the display of an SCP
    """
    class_lvl: str
    cont_clss: str
    disrupt_clss: str
    rsk_clss: str


class SCP(ORMBase):
    """
    A dataclass to store a SCP's information
    after getting its data from the deepwell
    """
    id: int
    clearance_level: IDandName
    containment_class: IDandName
    secondary_class: IDandName | None = None
    disruption_class: IDandName | None = None
    risk_class: IDandName | None = None
    site_responsible_id: int | None = None
    mtf: MTF | None = None
