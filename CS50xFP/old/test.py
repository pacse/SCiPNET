from cs50 import SQL

# Get sql database
db = SQL("sqlite:///SCiPNETdeepwell.db")

def get_id(table: str, name: str) -> int:
    query = f"SELECT id FROM {table} WHERE name = ?"
    row = db.execute(query, name)
    return row[0]["id"]

def get_name(table, id): # From the ducky :)
    row = db.execute("SELECT name FROM ? WHERE id = ?", table, id)
    return row[0]["name"]

def load_credentials(user_id):
    row = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    return row


print(load_credentials(2))
