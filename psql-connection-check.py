import psycopg2

conn = psycopg2.connect(
    dbname="vendor_performance_analysis",
    user="Username",
    password="password",
    host="localhost",
    port="5432"
)

cur = conn.cursor()
cur.execute("SELECT version();")
version = cur.fetchone()[0]

print("PostgreSQL version:", version)
cur.close()
conn.close()
