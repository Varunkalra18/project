import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from datetime import date
from flask_session import Session
from tempfile  import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from support import login_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///test.db")


@app.route('/', methods=['GET']) 
def home() : 
    return redirect("/login")

@app.route('/register', methods=['GET', 'POST']) 
def register() : 
    print("I am in register route")
    if request.method == "GET":
        return render_template("register.html") 
    else : 
        # TODO : Add register functionality here
        username = request.form.get("username")
        emailId = request.form.get("emailId")
        password = request.form.get("password")
        confirmation = request.form.get("confirm")
        if not username or not emailId or not password or not confirmation :
            return render_template("sorry.html", text="Please Enter complete details")
        if password != confirmation:
            return render_template("sorry.html", text = "Password doesn't match .. !!")
        user = db.execute("SELECT * FROM users WHERE username=:username", username = username)
        if len(user) != 0:
            return render_template("sorry.html", text = "Username Already Exists")
        email = db.execute("SELECT * FROM users WHERE emailId=:email", email = emailId)
        if len(email) != 0:
            return render_template("Email Already Used")
        hashed = generate_password_hash(password)
        db.execute("INSERT INTO users (type, username, emailId, pasword,cash) VALUES(:type, :username, :emailId, :pasword, :cash)",type = "client", username = username, emailId = emailId, pasword = hashed, cash=0.00)
        return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login() :
    session.clear() 
    print("here in login route") 
    if request.method == "GET" : 
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        rows = db.execute("SELECT * FROM users WHERE emailID = :email", email = email)
        if len(rows) == 0:
            return render_template("sorry.html", text = "Invalid User")
        if not check_password_hash(rows[0]["pasword"], password):
            return render_template("sorry.html", text="Invalid User")
        session["user_id"] = rows[0]["id"]
        return redirect("/")

@app.route("/logout", methods = ["GET","POST"])
@login_required
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug = True)

#source venv/scripts/activate
#export FLASK_APP=application.py
#flask run