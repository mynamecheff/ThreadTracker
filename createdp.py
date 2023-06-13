import sqlite3 as sql

#connect to SQLite
con = sql.connect('leaderboard.db')

#Create a Connection
cur = con.cursor()

#Drop  table if already exsist.
cur.execute("DROP TABLE IF EXISTS stats_data")
cur.execute("DROP TABLE IF EXISTS users")



sql = '''CREATE TABLE "stats_data" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "create_date" TEXT NOT NULL,
    "take_ownership_timestamp" TEXT NOT NULL,
    "closed_incident_timestamp" TEXT,
    "sd_severity" TEXT NOT NULL,
    "type" TEXT NOT NULL
)'''

#sql = '''CREATE TABLE "users" (
 #   "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  #  "name" TEXT NOT NULL,
   # "password" TEXT NOT NULL
    #)'''

cur.execute(sql)

#commit changes
con.commit()

#close the connection
con.close()