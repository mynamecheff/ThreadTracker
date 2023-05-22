import sqlite3 as sql

#connect to SQLite
con = sql.connect('leaderboard.db')

#Create a Connection
cur = con.cursor()

#Drop users table if already exsist.
cur.execute("DROP TABLE IF EXISTS users")

#Create users table  in db_web database
#sql ='''CREATE TABLE "users" (
#	"UID"	INTEGER PRIMARY KEY AUTOINCREMENT,
#	"UNAME"	TEXT,
#	"CONTACT"	TEXT
#)'''


sql = '''CREATE TABLE "stats_data" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "create_date" TEXT NOT NULL,
    "take_ownership_timestamp" TEXT NOT NULL,
    "closed_incident_timestamp" TEXT,
    "sd_severity" TEXT NOT NULL,
    "type" TEXT NOT NULL
)'''

cur.execute(sql)

#commit changes
con.commit()

#close the connection
con.close()