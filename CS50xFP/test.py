from utils import db

rows = db.execute("SELECT id, name FROM containment_class")

with open("output.txt", "w") as f:
    for row in rows:
        line = 'printc(f"{row["id"]} - {row["name"]}")'
        f.write(f"printc(\"{row['id']} - {row['name']}\")\n")