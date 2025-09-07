'''
Where the BaseModels to store information
provided by the deepwell are stored
'''
from pydantic import BaseModel, Field

class User(BaseModel):
    '''
    A BaseModel to store user information
    after getting their data from the deepwell
    '''
    u_id: int
    name: str
    password: str
    clearance_level_id: int
    clearance_level_name: str
    title_id: int
    title_name: str
    site_id: int
    ip: str # the ip that the user has connected from
    override_phrase: str | None = Field(None, description="Not required for lower level personnel")

# TODO: Remake
def init_usr(info: dict[str, str | int | None]) -> User:
    pass
    """
    '''
    Creates a user BaseModel from
    the user's deepwell info
    '''

    return User(
        u_id = cast(int, info["id"]),
        name = cast(str, info["name"]),
        password = cast(str, info["password"]),
        clearance_level_id = cast(int, info["clearance_level_id"]),
        clearance_level_name = get_name("clearance_levels", cast(int, info["clearance_level_id"])),
        title_id = cast(int, info["title_id"]),
        title_name = get_name("titles", cast(int, info["title_id"])),
        site_id = cast(int, info["site_id"]),
        override_phrase = cast(str | None, info["override_phrase"])
      )
"""

class SCP_Colours(BaseModel):
    '''
    BaseModel to store hex colour codes
    (as ints) for the display of an SCP
    '''
    class_lvl: int
    cont_clss: int
    disrupt_clss: int
    rsk_clss: int

# TODO: Remake
"""def init_colours(classification_level: int, containment_class: int,
                disruption_class: int, risk_class: int) -> SCP_Colours:
        '''
        Creates a SCP_COLOURS dataclass from
        deepwell values
        '''
        return SCP_Colours(
            class_lvl = get_colour(classification_level),
            cont_clss = get_cc_colour(containment_class),
            disrupt_clss = get_colour(disruption_class),
            rsk_clss = get_colour(risk_class)
        )
"""

class SCP(BaseModel):
    '''
    A dataclass to store a SCP's information
    after getting its data from the deepwell
    '''
    scp_id: int
    classification_level: str
    containment_class: str
    secondary_class: str | None = None
    disruption_class: str
    risk_class: str
    site_responsible_id: int | None = None
    assigned_task_force_name: str | None = None
    colours: SCP_Colours

# TODO: Remake
def init_scp(info: dict[str, str | int | None]) -> SCP:
    pass
    """
    # TODO!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # handle null values properly you lazy cabrone (╯°□°）╯︵ ┻━┻
    '''
    Creates a scp dataclass from
    the scp's deepwell info
    '''

    # get proper names from deepwell
    classification_level = get_name("clearance_levels",
                                    cast(int, info["classification_level_id"]))

    containment_class = get_name("containment_classes",
                                 cast(int, info["containment_class_id"]))


    secondary_class = get_name("secondary_classes",
                                cast(int, info["secondary_class_id"]))

    disruption_class = get_name('disruption_classes', cast(int, info['disruption_class_id']))

    risk_class = get_name("risk_classes", cast(int, info["risk_class_id"]))

    if info["assigned_task_force_id"]:
        atf_name = get_name("mtfs", cast(int, info["assigned_task_force_id"]))
        atf_nickname = get_nickname(cast(int, info["assigned_task_force_id"]))
        assigned_task_force_name = f"{atf_name} (*{atf_nickname}*)"
    else:
        assigned_task_force_name = None


    return SCP(
        id=cast(int, info["id"]),
        classification_level = classification_level,
        containment_class = containment_class,
        secondary_class = secondary_class,
        disruption_class = disruption_class,
        risk_class = risk_class,
        site_responsible_id = cast((int | None), info["site_responsible_id"]),
        assigned_task_force_name = assigned_task_force_name,

        colours = init_colours(
            classification_level = cast(int, info["classification_level_id"]),
            containment_class = cast(int, info["containment_class_id"]),
            disruption_class = cast(int, info["disruption_class_id"]),
            risk_class = cast(int, info["risk_class_id"]),
        )
    )
"""

class Site:
    s_id: int
    name: str
    director: str | None = None

# TODO: Remake
def init_site(info: dict[str, str | int | None]) -> Site:
    pass
    """
    # format director
    director: str | None = f"{info['director_id']} - {info['director_name']}" if info["director_id"] is not None else "[REDACTED]"

    return Site(
        s_id = cast(int,info["site_id"]),
        name = cast(str, info["site_name"]),
        director = director
    )
"""

class MTF:
    mtf_id: int
    name: str
    nickname: str
    leader_id: int | None = None
    leader_name: str | None = None
    site_id: int | None = None
    active: bool

# TODO: Remake
def init_mtf(info: dict[str, str | int | None]) -> MTF:
    pass
    """
    return MTF(
        id = cast(int, info["mtf_id"]),
        name = cast(str, info["mtf_name"]),
        nickname = cast(str, info["mtf_nickname"]),
        leader_id = cast(int | None, info["leader_id"]),
        leader_name = cast(str | None, info["leader_name"]),
        site_id = cast(int | None, info["mtf_site_id"]),
        active = cast(bool, info["mtf_active"])
    )"""
