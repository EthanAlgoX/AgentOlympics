import os
from app.db.session import DB_PATH, DATABASE_URL
print(f"Effective DB_PATH: {DB_PATH}")
print(f"Effective DATABASE_URL: {DATABASE_URL}")
print(f"File exists: {os.path.exists(DB_PATH)}")
