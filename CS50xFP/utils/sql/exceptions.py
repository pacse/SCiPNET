'''
All custom exceptions for SQLite Database related errors
'''

class DatabaseError(Exception):
    '''
    Base exception for SQLite Database related errors
    '''
    pass


class TableNotFoundError(DatabaseError):
    '''
    Exception raised when a specified table does not exist
    '''
    def __init__(self, table_name: str):
        super().__init__(f"Table {table_name!r} does not exist.")

class ColumnNotFoundError(DatabaseError):
    '''
    Exception raised when a specified column does not exist
    '''
    def __init__(self, column_name: str, table_name: str):
        super().__init__(f"Column {column_name!r} does not exist in table {table_name!r}.")

class RecordNotFoundError(DatabaseError):
    '''
    Exception raised when a specified record (row) does not exist in a table
    '''
    def __init__(self, table_name: str, lookup_field: str, lookup_value: str | int):
        super().__init__(f"Record with {lookup_field!r} = {lookup_value!r} does not exist in table {table_name!r}.")

class DatabaseNotFoundError(DatabaseError):
    '''
    Exception raised when the SQLite database file is not found
    '''
    def __init__(self):
        super().__init__("Database file not found.")