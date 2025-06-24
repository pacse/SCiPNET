from utils import db

db.execute("INSERT INTO sites (id) VALUES (0)")
rows = db.execute("SELECT * FROM sites")
for row in rows:
    print(row)

'''
with open("output.txt", "w") as f:
    for row in rows:
        f.write(f"printc(\"{row['id']} - {row['name']}\")\n")
'''