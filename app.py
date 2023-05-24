from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import sqlite3 as sql
from achievements import ACHIEVEMENT_THRESHOLD, ACHIEVEMENT_MESSAGE
from lul import EpochConverter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

@app.route("/crud")
def crud():
    con = sql.connect("leaderboard.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM stats_data")
    rows = cur.fetchall()

    # calls on lul.py to convert epoch time to human-readable time if epoch time is not None
    formatted_data = []
    for row in rows:
        formatted_row = {}
        for key, value in dict(row).items():
            if key in ['create_date', 'take_ownership_timestamp', 'closed_incident_timestamp']:
                formatted_row[key] = EpochConverter.convert(value)
            else:
                formatted_row[key] = value
        formatted_data.append(formatted_row)
    
    return render_template("crud.html", datas=formatted_data)


@app.route("/add_data", methods=['POST', 'GET'])
def add_data():
    if request.method == 'POST':
        name = request.form['name']
        create_date = request.form['create_date']
        take_ownership_timestamp = request.form['take_ownership_timestamp']
        closed_incident_timestamp = request.form['closed_incident_timestamp']
        sd_severity = request.form['sd_severity']
        incident_type = request.form['type']

        con = sql.connect("leaderboard.db")
        cur = con.cursor()
        cur.execute(
            "insert into stats_data(name, create_date, take_ownership_timestamp, closed_incident_timestamp, sd_severity, type) values (?, ?, ?, ?, ?, ?)",
            (name, create_date, take_ownership_timestamp, closed_incident_timestamp, sd_severity, incident_type))
        con.commit()
        flash('Stats added', 'success')
        check_achievements(name, incident_type)  # Check for achievements after adding data
        return redirect(url_for("crud"))

    return render_template("add_data.html")


@app.route("/edit_data/<string:id>", methods=['POST', 'GET'])
def edit_data(id):
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        create_date = request.form['create_date']
        take_ownership_timestamp = request.form['take_ownership_timestamp']
        closed_incident_timestamp = request.form['closed_incident_timestamp']
        sd_severity = request.form['sd_severity']
        incident_type = request.form['type']

        con = sql.connect("leaderboard.db")
        cur = con.cursor()
        cur.execute(
            "update stats_data set name=?, create_date=?, take_ownership_timestamp=?, closed_incident_timestamp=?, sd_severity=?, type=? where id=?",
            (name, create_date, take_ownership_timestamp, closed_incident_timestamp, sd_severity, incident_type, id))
        con.commit()
        flash('Data updated', 'success')
        check_achievements(name, incident_type)  # Check for achievements after editing data
        return redirect(url_for("crud"))

    con = sql.connect("leaderboard.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from stats_data where id=?", (id,))
    data = cur.fetchone()
    return render_template("edit_data.html", datas=data)


@app.route("/delete_data/<string:id>", methods=['GET'])
def delete_data(id):
    con = sql.connect("leaderboard.db")
    cur = con.cursor()
    cur.execute("delete from stats_data where id=?", (id,))
    con.commit()
    flash('Data deleted', 'warning')
    return redirect(url_for("crud"))


@app.route("/leaderboard")
def leaderboard():
    con = sql.connect("leaderboard.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute(
        "SELECT name, COUNT(*) AS incidents, 'Total' AS type FROM stats_data GROUP BY name UNION ALL SELECT name, COUNT(*) AS incidents, type FROM stats_data WHERE type = 'QRadar' GROUP BY name, type UNION ALL SELECT name, COUNT(*) AS incidents, type FROM stats_data WHERE type = 'Phishing' GROUP BY name, type ORDER BY type ASC, incidents DESC")
    data = cur.fetchall()
    return render_template("leaderboard.html", datas=data, ACHIEVEMENT_THRESHOLD=ACHIEVEMENT_THRESHOLD,
                           ACHIEVEMENT_MESSAGE=ACHIEVEMENT_MESSAGE)

@app.route("/achievements")
def achievements():
    con = sql.connect("leaderboard.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    achievements_data = []

    for incident_type, threshold_info in ACHIEVEMENT_THRESHOLD.items():
        threshold = threshold_info['threshold']
        cur.execute(
            "SELECT name, type, COUNT(*) AS incidents FROM stats_data WHERE type = ? GROUP BY name, type HAVING incidents >= ?",
            (incident_type, threshold))
        rows = cur.fetchall()
        for row in rows:
            # Convert sqlite3.Row to dictionary
            data = dict(row)
            data['achievement_name'] = threshold_info['name']
            achievements_data.append(data)

    return render_template("achievements.html", datas=achievements_data, ACHIEVEMENT_MESSAGE=ACHIEVEMENT_MESSAGE, ACHIEVEMENT_THRESHOLD=ACHIEVEMENT_THRESHOLD)


def check_achievements(name, incident_type):
    con = sql.connect("leaderboard.db")
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM stats_data WHERE name = ? AND type = ?", (name, incident_type))
    incidents_count = cur.fetchone()[0]
    if incident_type in ACHIEVEMENT_THRESHOLD and incidents_count >= ACHIEVEMENT_THRESHOLD[incident_type]['threshold']:
        achievement_message = ACHIEVEMENT_MESSAGE[incident_type]
        flash(f'Achievement Unlocked: {achievement_message}', 'info')


@app.route("/loading")
def loading():
     return render_template("loading.html")

if __name__ == '__main__':
    app.run(debug=True)
