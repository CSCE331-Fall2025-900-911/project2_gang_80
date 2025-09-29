# Setup
import psycopg2

with open("DatabaseScripts/passwd.txt", "r") as f:
    password = f.read().strip()

conn = psycopg2.connect(
    host="gang_80.rds.amazonaws.com",
    port=5432,
    dbname="gang_80_db",
    user="gang_80",
    password=password
)
cur = conn.cursor()

# ======================
# Test connection
cur.execute("SELECT name FROM menu_items;")
print(cur.fetchone())

# ======================
# Read SQL file
with open("create_tables.sql", "r") as f:
    sql = f.read()


# Execute SQL commands
cur.execute(sql)  # For multiple statements, use execute if single; otherwise, see below

# ======================
# Cleanup
conn.commit()
cur.close()
conn.close()