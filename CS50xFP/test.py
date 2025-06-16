from utils import db

rows = db.execute("SELECT * FROM secondary_class")
print(rows)
'''
with open("output.txt", "w") as f:
    for row in rows:
        f.write(f"printc(\"{row['id']} - {row['name']}\")\n")
'''