"""
All SQLAlchemy table definitions for
SCiPnet.db and related table information/funcs
"""

from sqlalchemy import (Column, Integer, String, Boolean, DateTime,
                        ForeignKey, Index, CheckConstraint)

from sqlalchemy.orm import (relationship, RelationshipProperty,
                            DeclarativeBase, validates)

from datetime import datetime

import re
wk_hash_regex = r'scrypt:32768:8:1\$[A-Za-z0-9]{16}\$[A-Za-z0-9]{128}'
"""A regex for a werkzeug hash (for validation)"""


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
    return col_str(162, nullable) # 162 is max length of werkzeug hash


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
                        backref=back_ref[:-1], # remove plural 's'
                        foreign_keys=foreign_keys
                        )


def SCP_rel(t_name: str) -> RelationshipProperty:
    """
    Returns a relationship to the SCP table.
    """
    return ref_rel('SCP', t_name)

def User_rel(t_name: str,
             foreign_keys: list = []
            ) -> RelationshipProperty:
    """
    Returns a relationship to the User table.
    """
    return ref_rel('User', t_name, foreign_keys=foreign_keys)


# ease of life Mixin

class HelperTableMixin:
    """
    Mixin that adds a 50 char `name` column.
    """
    name = col_str(50, False)


# base class for all tables
class Base(DeclarativeBase):
    """
    all tables have:
        `id`: primary key column
        `created_at`: when row was created | default: current timestamp
        `updated_at`: when row was last updated | default: current timestamp
    """
    id = col_int_pk()

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now,
                        nullable=False)

# ==== Main Models ====

class User(Base):
    __tablename__ = 'users'


    name = col_str(50, False)
    password = wk_hash(nullable = False)
    override_phrase = wk_hash(nullable = True)

    clearance_lvl_id = col_int_fk('clearance_levels.id', False)

    title_id = col_int_fk('titles.id', False)
    site_id = col_int_fk('sites.id', False)

    is_active = Column(Boolean, default = False, nullable = False)
    last_login = Column(DateTime, default = None)


    # relationship (others handled automatically, hopefully 🤞)
    audit_logs = pops_rel('AuditLog', 'user')


    # validators! 🎉
    @validates('password', 'override_phrase')
    def validate_hash(self, key, value):
        if len(value) != 162:
            raise ValueError('Werkzeug hash must be 162 characters long')

        if not re.fullmatch(wk_hash_regex, value):
            raise ValueError('Provided value is not a valid Werkzeug hash (correct length (162), did not match regex)')


    __table_args__ = (
        # table indexes
        Index('idx_users_name', name),
        Index('idx_users_clearance_level_id', clearance_lvl_id),
        Index('idx_users_site_id', site_id),
        Index('idx_users_title_id', title_id),
        Index('idx_users_is_active', is_active),
        Index('idx_users_updated_at', 'updated_at')
    )

class SCP(Base):
    __tablename__ = 'scps'

    clearance_lvl_id = col_int_fk('clearance_levels.id', False)

    containment_class_id = col_int_fk('containment_classes.id', False)
    secondary_class_id = col_int_fk('secondary_classes.id', True)

    disruption_class_id = col_int_fk('disruption_classes.id', True)
    risk_class_id = col_int_fk('risk_classes.id', True)

    site_responsible_id = col_int_fk('sites.id', True)
    assigned_task_force_id = col_int_fk('mtfs.id', True)

    status = Column(String(15), default='active', nullable=False)


    # relationships handled by backrefs


    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'neutralized', 'explained', 'deleted')",
            name='status_check'
        ),

        # table indexes (maybe _every_ col is overkill but we ball)
        Index('idx_scps_clearance_lvl_id', clearance_lvl_id),
        Index('idx_scps_containment_class_id', containment_class_id),
        Index('idx_scps_secondary_class_id', secondary_class_id),
        Index('idx_scps_disruption_class_id', disruption_class_id),
        Index('idx_scps_risk_class_id', risk_class_id),
        Index('idx_scps_site_responsible_id', site_responsible_id),
        Index('idx_scps_assigned_task_force_id', assigned_task_force_id),
        Index('idx_scps_status', status),
        Index('idx_scps_updated_at', 'updated_at')
    )

class MTF(Base):
    __tablename__ = 'mtfs'

    name = col_str(25, nullable=False) # eg. Epsilon-6
    nickname = col_str(100, nullable=False) # eg. 'Village Idiots', long just in case

    leader_id = col_int_fk('users.id', nullable=True)
    site_id = col_int_fk('sites.id', nullable=True)

    active = Column(Boolean, default=True, nullable=False)

    # relationships _mostly_ handled by backrefs
    leader = User_rel(__tablename__, [leader_id])
    scps = SCP_rel(__tablename__)


    __table_args__ = (
        # table indexes
        Index('idx_mtfs_name', name),
        Index('idx_mtfs_nickname', nickname),
        Index('idx_mtfs_leader_id', leader_id),
        Index('idx_mtfs_site_id', site_id),
        Index('idx_mtfs_updated_at', 'updated_at')
    )

class Site(Base):
    __tablename__ = 'sites'

    name = col_str(100, False) # eg. 'Site-01'
    director_id = col_int_fk('users.id', True)


    director = User_rel(__tablename__, [director_id])
    scps = SCP_rel(__tablename__)
    mtfs = ref_rel('MTF', __tablename__)

    __table_args__ = (
        Index('idx_sites_name', name),
        Index('idx_sites_director', director_id),
        Index('idx_sites_updated_at', 'updated_at')
    )

class AuditLog(Base):
    __tablename__ = 'audit_log'

    user_id = col_int_fk('users.id', nullable=False)
    user_ip = col_str(60, nullable=False) # IP address of the user, long enough for IPv6, i think

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

    # relationships
    scps = SCP_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_containment_classes_name', 'name'),
        Index(f'idx_containment_classes_updated_at', 'updated_at')
    )

class SecondaryClass(HelperTableMixin, Base):
    __tablename__ = 'secondary_classes'

    # relationships
    scps = SCP_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_secondary_classes_name', 'name'),
        Index(f'idx_secondary_classes_updated_at', 'updated_at')
    )

class DisruptionClass(HelperTableMixin, Base):
    __tablename__ = 'disruption_classes'

    # relationships
    scps = SCP_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_disruption_classes_name', 'name'),
        Index(f'idx_disruption_classes_updated_at', 'updated_at')
    )

class RiskClass(HelperTableMixin, Base):
    __tablename__ = 'risk_classes'

    # relationships
    scps = SCP_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_risk_classes_name', 'name'),
        Index(f'idx_risk_classes_updated_at', 'updated_at')
    )


# all user titles
class Title(HelperTableMixin, Base):
    __tablename__ = 'titles'

    # relationships
    users = User_rel(__tablename__)

    __table_args__ = (
        Index(f'idx_titles_name', 'name'),
        Index(f'idx_titles_updated_at', 'updated_at')
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
    'risk_classes',
    'titles',
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
