from cs50 import SQL

# init sqlite database
db = SQL("sqlite:///SCiPNETdeepwell.db")

rows = db.execute("SELECT * FROM audit_log")

for row in rows:
    print(row)