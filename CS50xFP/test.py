from utils import db

print(db.execute("PRAGMA table_info(scps)"))