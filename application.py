import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from datetime import date
from flask_session import Session
from tempfile  import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

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

if __name__ == "__main__":
    app.run(debug = True)


@app.route('/', methods=['GET']) 
def home() : 
    return redirect("/login")

@app.route('/register', methods=['GET', 'POST']) 
def register() : 
    print("I am in register route")
    if request.method == "GET":
        return render_template("register.html") 
    else : 
        pass

@app.route('/login', methods=['GET', 'POST'])
def login() : 
    print("here in login route") 
    if request.method == "GET" : 
        return render_template("login.html")
    else : 
        pass

        
#source venv/scripts/activate
#export FLASK_APP=application.py
#flask run