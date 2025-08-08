from cs50 import SQL

db = SQL("sqlite:///SCiPNET.db")

db.execute("DROP TABLE IF EXISTS colours")
db.execute("""CREATE TABLE colours (
           id INTEGER PRIMARY KEY,
           hex_code INTEGER
           )""")

colours = [
    (0,158,107),
    (0,135,189),
    (255,211,0),
    (255,211,0),
    (255,109,0),
    (133,0,5)
]

def format_colour(colour: tuple[int, int, int]) -> int:
    string = "".join(f"{n:02x}" for n in colour)
    return int(string, 16)

for colour in colours:
    db.execute("INSERT INTO colours (hex_code) VALUES (?)", format_colour(colour))