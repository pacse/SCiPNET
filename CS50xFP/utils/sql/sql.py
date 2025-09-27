"""
SQL stuff
"""

# ==== imports utils.sql ====

from . import tables
from .tables import MainModels, HelperModels
from .exceptions import *
from .conn import db_session

# ==== other imports ====
from sqlalchemy import func, select
import ipaddress

# for type hinting
from sqlalchemy.sql.elements import ColumnElement
from typing import Type, TypeAlias, Any

ModelClass: TypeAlias = Type[tables.Base] # simplify a common type
AnyColumn: TypeAlias = ColumnElement[Any]

# helpers to shorten common expressions
def get_table_name(model_class: ModelClass) -> str:
    """
    Returns a ModelClass's tablename
    """
    return model_class.__tablename__


def get_id_col(model_class: ModelClass) -> AnyColumn:
    """
    Returns a ModelClass's id column
    (first primary key)
    """
    return model_class.__mapper__.primary_key[0]

def get_id_col_name(model_class: ModelClass) -> str:
    """
    Returns the name of a ModelClass's id column
    (first primary key)
    """
    return str(get_id_col(model_class)).split('.')[1]


def get_type_name(value) -> str:
    """
    Returns the name of a value's type
    """
    return type(value).__name__


# ==== proper functions ====

def next_id(model_class: ModelClass) -> int:
    """
    Returns the next id in a table:
    COALESCE(MAX(id), 0) + 1
    """
    # get table name & id col
    t_name = get_table_name(model_class)
    id_col  = get_id_col(model_class)

    # sanity check
    if not tables.validate_table(t_name):
        raise TableNotFoundError(t_name)

    # execute query
    try:
        with db_session() as session:
            result = session.scalar( # scalar gets first column of first row
                select(
                    func.coalesce(func.max(id_col), 0) + 1
                    )
                )

            if result is None:
                raise RecordNotFoundError(
                                          t_name,
                                          str(id_col),
                                          'COALESCE(MAX(id), 0) + 1'
                                         )

            return result

    # catch all
    except Exception as e:
        raise DatabaseError(
                            f'Failed to get next ID for {get_table_name}:\n{e}'
                           )


def get_field_with_field(model_class: ModelClass,
                         lookup_field: str, lookup_value: str | int,
                         return_field: str
                        ) -> Any:
    """
    Gets `return_field` from `model_class`
    where `lookup_field` = `lookup_value`
    """

    # reused strings & template
    lookup_val_type = get_type_name(lookup_value)
    t_name: str = get_table_name(model_class)


    # validate inputs
    if not tables.validate_table(t_name):
        raise TableNotFoundError(t_name)

    # validate lookup field & value types
    if lookup_field.endswith('id') and not isinstance(lookup_value, int):
        raise FieldError('id', lookup_value,
                         f'int, got {lookup_val_type}'
                        )

    elif lookup_field == 'name' and not isinstance(lookup_value, str):
        raise FieldError('name', lookup_value,
                         f'str, got {lookup_val_type}'
                        )

    elif not (lookup_field.endswith('id') or lookup_field == 'name'):
        raise FieldError('lookup field', lookup_field,
                         f"'id' or 'name', got {lookup_field!r}"
                        )

    try:
        with db_session() as session:
            # getattr is equivalent to `model_class.lookup_field`
            # just `.lookup_field` would look for a `lookup_field` col
            lookup_col = getattr(model_class, lookup_field)
            return_col = getattr(model_class, return_field)

            # exec query
            result = session.scalar(
                select(return_col).filter(
                    lookup_col == lookup_value
                )
            )

            # ensure we got something & return it
            if result is None:
                raise RecordNotFoundError(
                    t_name,
                    lookup_field,
                    lookup_value
                    )

            return result

    except AttributeError as e:
        # getattr() failed, col not found
        if lookup_field in str(e):
            raise ColumnNotFoundError(t_name, lookup_field)
        else:
            raise ColumnNotFoundError(t_name, return_field)


def get_name(model_class: ModelClass, table_id: int) -> str:
    """
    Gets the name of a row in a table by its ID

    returns the name as a string
    """
    return get_field_with_field(model_class,
                                get_id_col_name(model_class),
                                table_id, 'name')

def get_nickname(MTF_id: int) -> str:
    """
    Gets an MTF's nickname

    Returns the nickname as a string
    """
    return get_field_with_field(MainModels.MTF,
                                'mtf_id', MTF_id,
                                'nickname')


def get_id(model_class: ModelClass, name: str) -> int:
    """
    Gets the ID of a row in a table by its name

    Returns the ID as an integer
    """
    return get_field_with_field(
                                model_class,
                                'name', name,
                                get_id_col_name(model_class)
                               )


def get_colour(c_id: int) -> str | None:
    """
    Gets a ID's colour (for art.py) from a table

    Returns hex colour code: #XXXXXX or None if code is not found
    """
    try:
        return get_field_with_field(
                                    HelperModels.Colour,
                                    'id', c_id, 'hex_code'
                                   )

    # if not 1-6, return none
    except RecordNotFoundError:
        return None


# Log events in the audit log
# (eg. account creation, login, file access, file edit, ect.)
def log_event(
              user_id: int, user_ip: str,
              action: str, details: str,
              status: bool = True
             ) -> None:
    """
    Logs an event in the audit log
    """

    # validate inputs
    if not isinstance(user_id, int):
        raise FieldError(
                         'user_id',
                         user_id,
                         f'(expected int, got {get_type_name(user_id)})'
                        )

    if not isinstance(user_ip, str):
        raise FieldError(
                         'user_ip',
                         user_ip,
                         f'(expected str, got {get_type_name(user_ip)})'
                        )

    try:
        ipaddress.ip_address(user_ip)
    except ValueError:
        raise FieldError(
                         'user_ip',
                         user_ip,
                         '(expected valid IP address'
                        )

    if not isinstance(action, str):
        raise FieldError(
                         'action',
                         action,
                         f'(expected str, got {get_type_name(action)})'
                        )

    if not isinstance(details, str):
        raise FieldError(
                         'details',
                         details,
                         f'(expected str, got {get_type_name(details)})'
                        )

    if not isinstance(status, bool):
        raise FieldError(
                         'status',
                         status,
                         f'(expected bool, got {get_type_name(status)})'
                        )

    # create & insert row
    row = MainModels.AuditLog(
        user_id=user_id,
        user_ip=user_ip,
        action=action,
        details=details,
        status=status
    )
    try:
        with db_session() as session:
            session.add(row)
            session.commit()
    except Exception as e:
        raise DatabaseError(f'Failed to log event:\nRow: {row}\nError: {e}')
