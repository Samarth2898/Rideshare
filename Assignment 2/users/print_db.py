import sqlite3
conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute("SELECT * FROM users")
x = c.fetchall()
print("Users :\n",x,"\n\n")

conn.close()