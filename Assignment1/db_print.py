import sqlite3
conn = sqlite3.connect('rideshare.db')
c = conn.cursor()

c.execute("SELECT * FROM users")
x = c.fetchall()
print("Users : ",x)
c.execute("SELECT * FROM ride")
x = c.fetchall()
print("Ride : ",x)
c.execute("SELECT * FROM ride_pool")
x = c.fetchall()
print("Ride_Pool : ",x)
conn.close()