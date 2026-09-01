import os
from connection import get_connection

conn = get_connection()
cur = conn.cursor()

schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
with open(schema_path) as f:
    cur.execute(f.read())

conn.commit()
cur.close()
conn.close()
print("Schema created.")