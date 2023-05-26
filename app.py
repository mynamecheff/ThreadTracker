from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import sqlite3 as sql
from achievements import ACHIEVEMENT_THRESHOLD, ACHIEVEMENT_MESSAGE
from lul import EpochConverter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
DATABASE = 'leaderboard.db'

def get_db():
    conn = sql.connect(DATABASE)
    conn.row_factory = sql.Row
    return conn

def check_achievements(name, incident_type):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM stats_data WHERE name = ? AND type = ?", (name, incident_type))
        incidents_count = cur.fetchone()[0]
        if incident_type in ACHIEVEMENT_THRESHOLD and incidents_count >= ACHIEVEMENT_THRESHOLD[incident_type]['threshold']:
            achievement_message = ACHIEVEMENT_MESSAGE[incident_type]
            flash(f'Achievement Unlocked: {achievement_message}', 'info')

def login_required(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return route_function(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route("/crud")
@login_required
def crud():
    with get_db() as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM stats_data")
        rows = cur.fetchall()

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
@login_required
def add_data():
    if request.method == 'POST':
        name = request.form['name']
        create_date = request.form['create_date']
        take_ownership_timestamp = request.form['take_ownership_timestamp']
        closed_incident_timestamp = request.form['closed_incident_timestamp']
        sd_severity = request.form['sd_severity']
        incident_type = request.form['type']

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO stats_data(name, create_date, take_ownership_timestamp, closed_incident_timestamp, sd_severity, type) VALUES (?, ?, ?, ?, ?, ?)", (name, create_date, take_ownership_timestamp, closed_incident_timestamp, sd_severity, incident_type))
            conn.commit()
            flash('Stats added', 'success')
            check_achievements(name, incident_type)
        return redirect(url_for("crud"))

    return render_template("add_data.html")

@app.route("/edit_data/<string:id>", methods=['POST', 'GET'])
@login_required
def edit_data(id):
    if request.method == 'POST':
        name = request.form['name']
        create_date = request.form['create_date']
        take_ownership_timestamp = request.form['take_ownership_timestamp']
        closed_incident_timestamp = request.form['closed_incident_timestamp']
        sd_severity = request.form['sd_severity']
        incident_type = request.form['type']

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE stats_data SET name=?, create_date=?, take_ownership_timestamp=?, closed_incident_timestamp=?, sd_severity=?, type=? WHERE id=?", (name, create_date, take_ownership_timestamp, closed_incident_timestamp, sd_severity, incident_type, id))
            conn.commit()
            flash('Data updated', 'success')
            check_achievements(name, incident_type)
        return redirect(url_for("crud"))

    with get_db() as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM stats_data WHERE id=?", (id,))
        data = cur.fetchone()
    return render_template("edit_data.html", datas=data)

@app.route("/delete_data/<string:id>", methods=['GET'])
@login_required
def delete_data(id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM stats_data WHERE id=?", (id,))
        conn.commit()
        flash('Data deleted', 'warning')
    return redirect(url_for("crud"))

@app.route("/leaderboard")
@login_required
def leaderboard():
    with get_db() as conn:
        conn.row_factory = sql.Row
        cur = conn.cursor()
        cur.execute("SELECT name, COUNT(*) AS incidents, 'Total' AS type FROM stats_data GROUP BY name UNION ALL SELECT name, COUNT(*) AS incidents, type FROM stats_data WHERE type = 'QRadar' GROUP BY name, type UNION ALL SELECT name, COUNT(*) AS incidents, type FROM stats_data WHERE type = 'Phishing' GROUP BY name, type ORDER BY type ASC, incidents DESC")
        data = cur.fetchall()
    return render_template("leaderboard.html", datas=data, ACHIEVEMENT_THRESHOLD=ACHIEVEMENT_THRESHOLD, ACHIEVEMENT_MESSAGE=ACHIEVEMENT_MESSAGE)


@app.route('/achievements')
def achievements():
    # Connect to the SQLite database
    conn = sql.connect('leaderboard.db')
    cursor = conn.cursor()

    # Fetch the data from the stats_data table
    cursor.execute("SELECT * FROM stats_data")
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Process the data and generate achievements
    achievement_counts = {}
    achievement_names = {}
    for row in data:
        name = row[1]
        type_value = row[6]
        if name not in achievement_counts:
            achievement_counts[name] = {type_value: 1}
            achievement_names[name] = {type_value: row[1]}
        else:
            if type_value not in achievement_counts[name]:
                achievement_counts[name][type_value] = 1
                achievement_names[name][type_value] = row[1]
            else:
                achievement_counts[name][type_value] += 1

    achievements = []
    for name, type_values in achievement_counts.items():
        for type_value, count in type_values.items():
            if count >= 4:
                achievement = {
                    'name': 'Masters',
                    'type': type_value,
                    'person': achievement_names[name][type_value]
                }
            elif count >= 2:
                achievement = {
                    'name': 'Expert',
                    'type': type_value,
                    'person': achievement_names[name][type_value]
                }
            else:
                continue

            achievements.append(achievement)

    # Render the HTML template and pass the achievements to it
    return render_template('achievements.html', achievements=achievements)

def create_users_table():
    with get_db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT)')
        conn.commit()

create_users_table()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db() as conn:
            conn.execute('INSERT INTO users (name, password) VALUES (?, ?)', (username, password))
            conn.commit()

        return redirect('/login')

    return render_template('registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db() as conn:
            cur = conn.cursor()
            user = cur.execute('SELECT * FROM users WHERE name = ?', (username,)).fetchone()

        if user and user['password'] == password:
            session['user_id'] = user['id']
            return redirect('/crud')

    return render_template('login.html')


@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/')
def frontpage():
    return render_template('frontpage.html')

if __name__ == '__main__':
    app.run(debug=True)