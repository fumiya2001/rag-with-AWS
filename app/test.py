import os
import psycopg2

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_PORT:", os.getenv("DB_PORT"))
print("DB_NAME:", os.getenv("DB_NAME"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD exists:", os.getenv("DB_PASSWORD") is not None)
print("DB_PASSWORD length:", len(os.getenv("DB_PASSWORD") or ""))

conn = psycopg2.connect(
    **DB_CONFIG
)

cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM embeddings")
print(cur.fetchone())


cur.execute("SELECT chunk FROM embeddings LIMIT 5")
print(cur.fetchall())

cur.close()
conn.close()