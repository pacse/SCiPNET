from utils import db

rows = db.execute("SELECT id, name FROM disruption_class")
for row in rows:
    print(row)
    print(f"{row['id']} - {row['name']}")
'''
with open("output.txt", "w") as f:
    for row in rows:
        f.write(f"printc(\"{row['id']} - {row['name']}\")\n")
'''