"""
All SQLAlchemy table definitions for
SCiPnet.db and related table information/funcs
"""

from sqlalchemy import (Column, Integer, String, Boolean, DateTime,
                        ForeignKey, Index, CheckConstraint)

from sqlalchemy.orm import (relationship, RelationshipProperty,
                            DeclarativeBase as Base)

from datetime import datetime



# ease of life shortenings
def col_int_pk() -> Column[int]:
    """
    Returns a primary key integer column with autoincrement.
    """
    return Column(Integer, primary_key=True, autoincrement=True)

def col_int_fk(ref: str, nullable=False) -> Column[int]:
    """
    Returns a foreign key integer column.

    ref: `<table_name>.<column_name>`
    """
    return Column(Integer, ForeignKey(ref), nullable=nullable)


def col_str(length: int, nullable=True) -> Column[str]:
    """
    Returns a string column.
    """
    return Column(String(length), nullable=nullable)


def wk_hash(nullable: bool) -> Column[str]:
    """
    Returns a string column for storing a werkzeug password hash.
    """
    return col_str(162, nullable)


def pops_rel(to: str,
        back_pop: str,
       ) -> RelationshipProperty:
    """
    Returns a relationship to another table.
    """
    return relationship(to,
                        back_populates=back_pop)


def ref_rel(to: str,
            back_ref: str,
            foreign_keys = None
           ) -> RelationshipProperty:
    """
    Returns a relationship to another table.
    """
    return relationship(to,
                        backref=back_ref,
                        foreign_keys=foreign_keys
                        )


def SCP_rel(t_name: str) -> RelationshipProperty:
    """
    Returns a relationship to the SCP table.
    """
    return ref_rel('SCP', t_name[:-1]) # remove plural 's'

def User_rel(t_name: str,
             foreign_keys: list = []
            ) -> RelationshipProperty:
    """
    Returns a relationship to the User table.
    """
    return ref_rel('User', t_name[:-1], foreign_keys=foreign_keys) # same as above


# ease of life Mixins
class TimestampMixin:
    """
    Mixin that adds `created_at` (when row was created) and
    `updated_at` (when row was last updated) timestamp columns.
    """
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now,
                        nullable=False)


class HelperTableMixin(TimestampMixin):
    """
    Mixin that adds a 50 char `name` column.
    """
    name = col_str(50, False)


# ==== Main Models ====

class User(TimestampMixin, Base):
    __tablename__ = 'users'

    u_id = col_int_pk()

    name = col_str(50, False)
    password = wk_hash(nullable = False)
    override_phrase = wk_hash(nullable = True)

    clearance_lvl_id = col_int_fk('clearance_levels.cl_id', False)

    title_id = col_int_fk('titles.t_id', False)
    site_id = col_int_fk('sites.s_id', False)

    is_active = Column(Boolean, default = False, nullable = False)
    last_login = Column(DateTime, default = None)


    # relationship (others handled automatically, hopefully 🤞)
    audit_logs = pops_rel('AuditLog', 'user')


    __table_args__ = (
        # table indexes
        Index('idx_users_name', name),
        Index('idx_users_clearance_level_id', clearance_lvl_id),
        Index('idx_users_site_id', site_id),
        Index('idx_users_title_id', title_id),
        Index('idx_users_is_active', is_active),
        Index('idx_users_updated_at', 'updated_at')
    )

class SCP(TimestampMixin, Base):
    __tablename__ = 'scps'

    scp_id = col_int_pk()

    classification_level_id = col_int_fk('clearance_levels.cl_id', False)

    containment_class_id = col_int_fk('containment_classes.cc_id', False)
    secondary_class_id = col_int_fk('secondary_classes.sc_id', True)

    disruption_class_id = col_int_fk('disruption_classes.dc_id', True)
    risk_class_id = col_int_fk('risk_classes.rc_id', True)

    site_responsible_id = col_int_fk('sites.s_id', True)
    assigned_task_force_id = col_int_fk('mtfs.mtf_id', True)

    status = Column(String(15), default='active', nullable=False)


    # relationships handled by backrefs


    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'neutralized', 'explained', 'deleted')",
            name='status_check'
        ),

        # table indexes (maybe _every_ col is overkill but we ball)
        Index('idx_scps_classification_level_id', classification_level_id),
        Index('idx_scps_containment_class_id', containment_class_id),
        Index('idx_scps_secondary_class_id', secondary_class_id),
        Index('idx_scps_disruption_class_id', disruption_class_id),
        Index('idx_scps_risk_class_id', risk_class_id),
        Index('idx_scps_site_responsible_id', site_responsible_id),
        Index('idx_scps_assigned_task_force_id', assigned_task_force_id),
        Index('idx_scps_status', status),
        Index('idx_scps_updated_at', 'updated_at')
    )

class MTF(TimestampMixin, Base):
    __tablename__ = 'mtfs'

    mtf_id = col_int_pk()

    name = col_str(25, nullable=False) # eg. Epsilon-6
    nickname = col_str(100, nullable=False) # eg. 'Village Idiots', long just in case

    leader_id = col_int_fk('users.u_id', nullable=True)
    site_id = col_int_fk('sites.s_id', nullable=True)

    active = Column(Boolean, default=True, nullable=False)

    # relationships _mostly_ handled by backrefs
    leader = User_rel(__tablename__)
    scps = SCP_rel(__tablename__)


    __table_args__ = (
        # table indexes
        Index('idx_mtfs_name', name),
        Index('idx_mtfs_nickname', nickname),
        Index('idx_mtfs_leader_id', leader_id),
        Index('idx_mtfs_site_id', site_id),
        Index('idx_mtfs_updated_at', 'updated_at')
    )

class Site(TimestampMixin, Base):
    __tablename__ = 'sites'

    s_id = col_int_pk()

    name = col_str(100, False) # eg. 'Site-01'
    director_id = col_int_fk('users.u_id', True)


    director = User_rel(__tablename__, [director_id])
    scps = SCP_rel(__tablename__)
    mtfs = ref_rel('MTF', __tablename__)

    __table_args__ = (
        Index('idx_sites_name', name),
        Index('idx_sites_director', director_id),
        Index('idx_sites_updated_at', 'updated_at')
    )

class AuditLog(TimestampMixin, Base):
    __tablename__ = 'audit_log'

    log_id = col_int_pk()

    user_id = col_int_fk('users.u_id', nullable=False)
    user_ip = col_str(20, nullable=False) # IP address of the user

    action = col_str(255, nullable=False) # description of action taken
    details = col_str(255, nullable=False) # additional details about the action
    status = Column(Boolean, nullable=False) # success or failure of the action

    timestamp = Column(DateTime, default=datetime.now, nullable=False)

    user = pops_rel('User', 'audit_logs')

    __table_args__ = (
        Index('idx_audit_user_id', user_id),
        Index('idx_audit_user_ip', user_ip),
        Index('idx_audit_timestamp', timestamp)
    )

# ==== Helper Models ====

# clearance lvls for users and
# classification lvls for scps
class ClearanceLevel(HelperTableMixin, Base):
    __tablename__ = 'clearance_levels'

    cl_id = col_int_pk()

    # relationships
    users = User_rel(__tablename__)
    scps = SCP_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_clearance_levels_name', 'name'),
        Index(f'idx_clearance_levels_updated_at', 'updated_at')
    )


# SCP specific models
class ContainmentClass(HelperTableMixin, Base):
    __tablename__ = 'containment_classes'

    cc_id = col_int_pk()

    # relationships
    scps = SCP_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_containment_classes_name', 'name'),
        Index(f'idx_containment_classes_updated_at', 'updated_at')
    )

class SecondaryClass(HelperTableMixin, Base):
    __tablename__ = 'secondary_classes'

    sc_id = col_int_pk()

    # relationships
    scps = SCP_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_secondary_classes_name', 'name'),
        Index(f'idx_secondary_classes_updated_at', 'updated_at')
    )

class DisruptionClass(HelperTableMixin, Base):
    __tablename__ = 'disruption_classes'

    dc_id = col_int_pk()

    # relationships
    scps = SCP_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_disruption_classes_name', 'name'),
        Index(f'idx_disruption_classes_updated_at', 'updated_at')
    )

class RiskClass(HelperTableMixin, Base):
    __tablename__ = 'risk_classes'

    rc_id = col_int_pk()

    # relationships
    scps = SCP_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_risk_classes_name', 'name'),
        Index(f'idx_risk_classes_updated_at', 'updated_at')
    )


# all user titles
class Title(HelperTableMixin, Base):
    __tablename__ = 'titles'

    t_id = col_int_pk()

    # relationships
    users = User_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_titles_name', 'name'),
        Index(f'idx_titles_updated_at', 'updated_at')
    )


# colours used for display
class Colour(TimestampMixin, Base):
    __tablename__ = 'colours'

    c_id = col_int_pk()
    hex_code = col_str(7, False) # eg. '#FF0000', '#00FF00', '#0000FF'

    __table_args__ = (
        Index(f'idx_colours_hex_code', hex_code),
        Index(f'idx_colours_updated_at', 'updated_at')
    )


# ==== Table related lists & funcs ====

VALID_TABLES = [
    'users',
    'scps',
    'mtfs',
    'sites',
    'audit_log',

    'clearance_levels',
    'containment_classes',
    'secondary_classes',
    'disruption_classes',
]
"""Valid table names for SQL queries"""

VALID_MODELS = [
    # main tables
    'User',
    'SCP',
    'MTF',
    'Site',
    'AuditLog',

    # helper tables
    'ClearanceLevel',
    'ContainmentClass',
    'SecondaryClass',
    'DisruptionClass',
    'RiskClass',
    'Title',
    'Colour'
]
"""Valid model names for SQLAlchemy"""


# checks `table` against valid_tables
def validate_table(table: str) -> bool:
    """
    Validate the table name against the list of valid tables.

    Returns True if the table is valid, False otherwise.
    """
    return table in VALID_TABLES


# ==== namespaces ====
class MainModels:
    User = User
    SCP = SCP
    MTF = MTF
    Site = Site
    AuditLog = AuditLog

class HelperModels:
    ClearanceLevel = ClearanceLevel

    ContainmentClass = ContainmentClass
    SecondaryClass = SecondaryClass
    DisruptionClass = DisruptionClass
    RiskClass = RiskClass

    Title = Title

    Colour = Colour

