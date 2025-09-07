'''
A collection of SQLAlchemy table
definitions for SCiPnet.db
'''
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base

from ..basic import timestamp


Base = declarative_base()


# ease of life shortenings
def col_int_pk():
    return Column(Integer, primary_key=True, autoincrement=True)

def col_int_fk(ref: str, nullable=False):
    '''ref: <table_name>.<column_name>'''
    return Column(Integer, ForeignKey(ref), nullable=nullable)


def col_str(length: int, nullable=True):
    return Column(String(length), nullable=nullable)


def wk_hash(nullable=True):
    return col_str(162, nullable)


def rel(to: str, back_populates: str, foreign_keys: list):
    return relationship(to,
                        back_populates=back_populates,
                        foreign_keys=foreign_keys)

def SCP_rel(t_name: str):
    return rel("SCP", t_name, [])

def User_rel(t_name: str):
    return rel("User", t_name, [])

# ease of life Mixins
class TimestampMixin:
    created_at = Column(DateTime, default=timestamp, nullable=False)
    updated_at = Column(DateTime, default=timestamp, onupdate=timestamp,
                        nullable=False)

class HelperTableMixin(TimestampMixin):
    name = col_str(50, False)

# ==== Main Tables ====

class User(TimestampMixin, Base):
    __tablename__ = "users"

    u_id = col_int_pk()

    name = col_str(50, False)
    password = wk_hash(False)
    override_phrase = wk_hash()

    clearance_lvl_id = col_int_fk("clearance_levels.cl_id", False)

    title_id = col_int_fk("titles.t_id", False)
    site_id = col_int_fk("sites.s_id", False)

    is_active = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, default=None)


    clearance_level = rel("ClearanceLevel", "users", [clearance_lvl_id])
    title = rel("Title", "users", [title_id])
    site = rel("Site", "users", [site_id])

class SCP(TimestampMixin, Base):
    __tablename__ = "scps"

    scp_id = col_int_pk()

    classification_level_id = col_int_fk("clearance_levels.cl_id", False)

    containment_class_id = col_int_fk("containment_classes.cc_id", False)
    secondary_class_id = col_int_fk("secondary_classes.sc_id")

    object_class_id = col_int_fk("object_classes.oc_id")
    risk_class_id = col_int_fk("risk_classes.r_id")

    site_responsible_id = col_int_fk("sites.s_id")
    assigned_task_force_id = col_int_fk("mtfs.mtf_id")

    status = Column(String(15), default="active", nullable=False)

    containment_class = rel("ContainmentClass", "scps", [containment_class_id])
    secondary_class = rel("SecondaryClass", "scps", [secondary_class_id])
    object_class = rel("ObjectClass", "scps", [object_class_id])
    risk_class = rel("RiskClass", "scps", [risk_class_id])

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'neutralized', 'explained', 'deleted')",
            name="status_check"
        )
    )

class MTF(TimestampMixin, Base):
    __tablename__ = "mtfs"

    mtf_id = col_int_pk()

    name = col_str(25, False) # eg. Epsilon-6
    nickname = col_str(100, False) # eg. "Village Idiots", long just in case

    leader_id = col_int_fk("users.u_id")
    site_id = col_int_fk("sites.s_id")

    leader = rel("User", "mtfs", [leader_id])
    site = rel("Site", "mtfs", [site_id])

class Site(TimestampMixin, Base):
    __tablename__ = "sites"

    s_id = col_int_pk()

    name = col_str(100, False) # eg. "Site-01"
    director_id = col_int_fk("users.u_id", True)

    director = rel("User", "sites", [director_id])

class AuditLog(TimestampMixin, Base):
    __tablename__ = "audit_log"

    log_id = col_int_pk()

    user_id = col_int_fk("users.u_id", False)
    user_ip = col_str(25, False) # IP address of the user

    action = col_str(255, False) # description of action taken
    details = col_str(255, False) # additional details about the action
    status = Column(Boolean) # success or failure of the action

    timestamp = Column(DateTime, default=timestamp, nullable=False)

    user = rel("User", "audit_log", [user_id])


# ==== Helper Tables ====

# clearance lvls for users and
# classification lvls for scps
class ClearanceLevel(HelperTableMixin, Base):
    __tablename__ = "clearance_levels"

    cl_id = col_int_pk()

    # relationships
    users = User_rel(__tablename__)
    scps = SCP_rel(__tablename__)


# SCP specific tables
class ContainmentClass(HelperTableMixin, Base):
    __tablename__ = "containment_classes"

    cc_id = col_int_pk()

    # relationships
    scps = SCP_rel(__tablename__)

class SecondaryClass(HelperTableMixin, Base):
    __tablename__ = "secondary_classes"

    sc_id = col_int_pk()

    # relationships
    scps = SCP_rel(__tablename__)

class DisruptionClass(HelperTableMixin, Base):
    __tablename__ = "disruption_classes"

    dc_id = col_int_pk()

    # relationships
    scps = SCP_rel(__tablename__)

class RiskClass(HelperTableMixin, Base):
    __tablename__ = "risk_classes"

    r_id = col_int_pk()

    # relationships
    scps = SCP_rel(__tablename__)


# all user titles
class Title(HelperTableMixin, Base):
    __tablename__ = "titles"

    t_id = col_int_pk()

    # relationships
    users = User_rel("titles")


# colours used for display
class Colour(TimestampMixin, Base):
    __tablename__ = "colours"

    c_id = col_int_pk()
    hex_code = col_str(7, False) # eg. "#FF0000", "#00FF00", "#0000FF"
