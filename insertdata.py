import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('leaderboard.db')
cursor = conn.cursor()

# Define the data to be inserted
data = {
    "156989": {"type": "QRadar", "create_date": 1683906292034, "take_ownership_timestamp": 1684140672317,
               "closed_incident_timestamp": 1684140782864, "sd_severity": "Low"},
    "156990": {"type": "QRadar", "create_date": 1683906292655, "take_ownership_timestamp": 1684135010486,
               "closed_incident_timestamp": 1684135335358, "sd_severity": "Low"},
    "156992": {"type": "QRadar", "create_date": 1683906814208, "take_ownership_timestamp": 1684135332360,
               "closed_incident_timestamp": 1684135798996, "sd_severity": "Low"},
    "157031": {"type": "QRadar", "create_date": 1683954585238, "take_ownership_timestamp": 1684135798996,
               "closed_incident_timestamp": None, "sd_severity": "Low"},
    "157117": {"type": "Phishing", "create_date": 1684075530547, "take_ownership_timestamp": 1684153675458,
                "closed_incident_timestamp": 1684154160904, "sd_severity": "High"}
}

# Iterate over the data and insert into the database
for key, values in data.items():
    create_date = values["create_date"]
    take_ownership_timestamp = values["take_ownership_timestamp"]
    closed_incident_timestamp = values.get("closed_incident_timestamp", None)
    sd_severity = values["sd_severity"]
    incident_type = values["type"]

    # Insert the data into the table
    cursor.execute(
        """
        INSERT INTO stats_data (create_date, take_ownership_timestamp, closed_incident_timestamp, sd_severity, type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (create_date, take_ownership_timestamp, closed_incident_timestamp, sd_severity, incident_type)
    )

# Commit the changes and close the connection
conn.commit()
conn.close()
