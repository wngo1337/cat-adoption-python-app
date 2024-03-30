import sqlite3

conn = sqlite3.connect("Data/adoption_agency.db")

with open('schema.sql') as f:
    conn.executescript(f.read())

conn.commit()
conn.close()