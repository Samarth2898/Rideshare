import sqlite3
conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS users")
c.execute('''CREATE TABLE users(
    username TEXT PRIMARY KEY,
    password CHAR(40) NOT NULL)''')

conn.commit()
conn.close()