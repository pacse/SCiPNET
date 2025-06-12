from cs50 import SQL

# init sqlite database
db = SQL("sqlite:///SCiPNETdeepwell.db")

query: str = "SELECT * FROM users WHERE id = ? AND password = ?"

print(db.execute(query, 1, "DivIIne"))