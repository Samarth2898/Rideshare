import sqlite3
conn = sqlite3.connect('rides.db')
c = conn.cursor()

c.execute("SELECT * FROM ride")
x = c.fetchall()
print("Ride :\n",x,"\n\n")
c.execute("SELECT * FROM ride_pool")
x = c.fetchall()
print("Ride_Pool :\n",x,"\n\n")

conn.close()