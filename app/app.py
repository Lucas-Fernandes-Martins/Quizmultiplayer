from flask import Flask, redirect, url_for, render_template, request, session, jsonify

import json

from flask_sqlalchemy import SQLAlchemy

import random

import os

from operator import itemgetter

app = Flask(__name__)

app.secret_key = "12345678910"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'

app.config['SQLALCHEMY_BINDS'] = {
    'question':'sqlite:///question.sqlite3'}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class question(db.Model):
    __bind_key__ = 'question'
    _id = db.Column("id", db.Integer, primary_key=True)
    current = db.Column(db.Integer)
    first = db.Column(db.Integer)
    def __init__(self):
        self.current = 0

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    admin = db.Column(db.Integer)
    ready = db.Column(db.Boolean)
    points = db.Column(db.Integer)
    current = db.Column(db.Integer)
    def __init__(self, name, admin, ready):
        self.name = name
        self.admin = admin
        self.ready = ready
        self.points = 0
        self.current = 0

@app.route("/get_users", methods=["GET", "POST"])
def get_users():
    usrs = users.query.all()
    user_list = []
    for user in usrs:
        user_list.append(user.name)

    return json.dumps(user_list)

@app.route("/change_question", methods=["GET", "POST"])
def change_question():
    r = request.json
    print(r["correct"])
    if(r["correct"] == True):
        usr = users.query.filter_by(name=session["name"]).first()
        usr.points += 1
    qst = users.query.filter_by(name=session["name"]).first()
    qst.current += 1
    db.session.commit()
    return ""

@app.route("/drop")
def drop():
    db.drop_all()
    db.create_all()
    return "<h1>Databases Deleted!</h1>"
@app.route("/endgame")
def endgame():
    all_users = users.query.all()
    users_list = []
    for user in all_users:
        users_list.append({"name": user.name, "points": user.points, "answered": user.current})

    sorted_list = sorted(users_list, key=itemgetter('points'), reverse=True)

    return render_template("game_over.html", users=sorted_list)

@app.route("/game")
def game():
    doc_path = os.getcwd() + "/app/static/json/questions.json"
    q_string = open(doc_path, "r").read()
    questions = json.loads(q_string)
    qnumber = users.query.filter_by(name=session["name"]).first().current
    if(qnumber == len(questions)):
        return redirect(url_for("endgame"))
    else:
        print("==========")
        print(qnumber)
        print(len(questions))
    info = questions[qnumber]
    all_users = users.query.all()
    users_list = []
    for user in all_users:
        users_list.append({"name": user.name, "points": user.points})
    
    return render_template("game.html", users=users_list, info=json.dumps(info))

@app.route("/start")
def start():
    admin_user = users.query.filter_by(admin=1).first()
    start = 0
    current = question()
    db.session.add(current)
    db.session.commit()
    if(admin_user.ready == True):
        start = 1
    return json.dumps(start)

@app.route("/update_screen")
def update_screen():
    ready = users.query.filter_by(ready=True).all()
    return json.dumps(len(ready))

@app.route("/ready")
def ready():
    if "name" in session:
        usr = users.query.filter_by(name=session["name"]).first()
        usr.ready = True
        db.session.commit()
    return redirect(url_for('wroom'))

@app.route("/wroom")
def wroom():
    if "name" not in session:
        return redirect(url_for("login"))
    ready = users.query.filter_by(ready=True).all()
    return render_template("wroom.html", name=session["name"], admin=session["admin"], ready=len(ready))

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        players = users.query.all()
        admin = 0
        if not players:
            admin = 1 

        user_name = request.form["user_name"]
        usr = users(user_name, admin, False)
        db.session.add(usr)
        db.session.commit()
        session["name"] = user_name
        session["admin"] = admin

        return redirect(url_for("wroom"))

    values = users.query.all()

    print(values)

    list_users = []

    for item in values:
        list_users.append(item.name)

    return render_template("login.html", values=json.dumps(list_users))

@app.route("/users")
def users_list():

    values = users.query.all()

    return render_template("users.html", values=values)

@app.route("/")
def main():
    if "name" not in session:
        return redirect(url_for("login"))
    
    return redirect(url_for("login"))
        
