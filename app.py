from flask import Flask,render_template,request,redirect,url_for,flash,send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import sqlite3 as sql


app=Flask(__name__)

@app.route("/crud")
def crud():
    con=sql.connect("leaderboard.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from stats_data")
    data=cur.fetchall()
    return render_template("crud.html",datas=data)

@app.route("/add_data",methods=['POST','GET'])
def add_data():
    if request.method=='POST':
        name=request.form['name']
        create_date=request.form['create_date']
        take_ownership_timestamp=request.form['take_ownership_timestamp']
        closed_incident_timestamp=request.form['closed_incident_timestamp']
        sd_severity=request.form['sd_severity']
        type=request.form['type']

        con=sql.connect("leaderboard.db")
        cur=con.cursor()
        cur.execute("insert into stats_data(name, create_date,take_ownership_timestamp,closed_incident_timestamp,sd_severity,type) values (?, ?,?,?,?,?)",(name, create_date,take_ownership_timestamp,closed_incident_timestamp,sd_severity,type))
        con.commit()
        flash('stats Added','success')
        return redirect(url_for("crud"))
    return render_template("add_data.html")

@app.route("/edit_data/<string:id>",methods=['POST','GET'])
def edit_data(id):
    if request.method=='POST':
        name=request.form['name']
        create_date=request.form['create_date']
        take_ownership_timestamp=request.form['take_ownership_timestamp']
        closed_incident_timestamp=request.form['closed_incident_timestamp']
        sd_severity=request.form['sd_severity']
        type=request.form['type']

        con=sql.connect("leaderboard.db")
        cur=con.cursor()
        cur.execute("update stats_data set name=?,create_date=?,take_ownership_timestamp=?,closed_incident_timestamp=?,sd_severity=?,type=? where id=?",(name, create_date,take_ownership_timestamp,closed_incident_timestamp,sd_severity,type,id))
        con.commit()
        flash('data Updated','success')
        return redirect(url_for("crud"))
    con=sql.connect("leaderboard.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from stats_data where id=?",(id,))
    data=cur.fetchone()
    return render_template("edit_data.html",datas=data)
    
@app.route("/delete_data/<string:id>",methods=['GET'])
def delete_data(id):
    con=sql.connect("leaderboard.db")
    cur=con.cursor()
    cur.execute("delete from stats_data where id=?",(id,))
    con.commit()
    flash('data Deleted','warning')
    return redirect(url_for("crud"))





@app.route("/index")
def index():
    con=sql.connect("db_web.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from users")
    data=cur.fetchall()
    return render_template("index.html",datas=data)

@app.route("/add_user",methods=['POST','GET'])
def add_user():
    if request.method=='POST':
        uname=request.form['uname']
        contact=request.form['contact']
        con=sql.connect("db_web.db")
        cur=con.cursor()
        cur.execute("insert into users(UNAME,CONTACT) values (?,?)",(uname,contact))
        con.commit()
        flash('User Added','success')
        return redirect(url_for("index"))
    return render_template("add_user.html")

@app.route("/edit_user/<string:uid>",methods=['POST','GET'])
def edit_user(uid):
    if request.method=='POST':
        uname=request.form['uname']
        contact=request.form['contact']
        con=sql.connect("db_web.db")
        cur=con.cursor()
        cur.execute("update users set UNAME=?,CONTACT=? where UID=?",(uname,contact,uid))
        con.commit()
        flash('User Updated','success')
        return redirect(url_for("index"))
    con=sql.connect("db_web.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from users where UID=?",(uid,))
    data=cur.fetchone()
    return render_template("edit_user.html",datas=data)
    
@app.route("/delete_user/<string:uid>",methods=['GET'])
def delete_user(uid):
    con=sql.connect("db_web.db")
    cur=con.cursor()
    cur.execute("delete from users where UID=?",(uid,))
    con.commit()
    flash('User Deleted','warning')
    return redirect(url_for("index"))
    
if __name__=='__main__':
    app.secret_key='admin123'
    app.run(debug=True)
