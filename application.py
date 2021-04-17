import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from datetime import date, datetime
from flask_session import Session
import json
from tempfile  import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from support import login_required
# Check empty function can be used to check weather the passed dictionary has some None value or not
from utility import getUser, checkEmpty

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
@login_required
def home() : 
    rows = db.execute("SELECT * FROM Assets")
    return render_template("index.html", row = rows) 

@app.route('/register', methods=['GET', 'POST']) 
def register() : 
    print("I am in register route")
    if request.method == "GET":
        return render_template("register.html") 
    else : 
        # TODO : Add register functionality here
        # data = json.loads(request.data)
        # print(data['username'])
        # username = data["username"]
        # emailId = data["email"]
        # password = data["pass"]
        # contact = data["contact"]
        # an = data["adharno"]
        # govid = data["govid"]
        
        username = request.form.get("username")
        print("username : ", username)
        emailId = request.form.get("emailId")
        print("EMail : ", emailId)
        password = request.form.get("password")
        print("Password : ", password)
        contact = request.form.get("contactnum") 
        print("contact : ", contact)
        an = request.form.get("PanNo")
        print("adhar : ", an)
        govid = request.form.get("Govid")
        print("govid : ", govid)
        timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        user = db.execute("SELECT * FROM User WHERE username=:username", username = username)
        print("Coming here 1")
        
        if len(user) != 0:
            return render_template("register.html", error="Username already exist .. !!")
        print("Coming here 2")
        email = db.execute("SELECT * FROM User WHERE Email=:email", email = emailId)
        print('email : ', email)
        if len(email) != 0:
            return render_template("register.html", error="Email already exist .. !!")
        print("Coming here 3")
        hashed = generate_password_hash(password)
        db.execute("INSERT INTO User (Username, Email, Passwords, PanNumber, GovId,ContactNumber, Timestamp) VALUES( :username, :emailId, :pasword, :adharnumber, :govid, :contact, :timestamp)", username = username, emailId = emailId, pasword = hashed, adharnumber = an, govid = govid,contact=contact, timestamp = timestamp)
        print("Coming here 4")
        return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login() :
    session.clear() 
    print("Coming to login after calling register because i am redirected")
    
    if request.method == "GET" : 
        print("Here in login in Get method") 
        return render_template("login.html")
    else:
        print("Here in login in Post method") 
        email = request.form.get("email")
        password = request.form.get("password")
        rows = db.execute("SELECT * FROM User WHERE Email = :email", email = email)
        if len(rows) == 0:
            return render_template("sorry.html", text = "Invalid User")
        if not check_password_hash(rows[0]["Passwords"], password):
            return render_template("sorry.html", text="Invalid User")
        session["user_id"] = rows[0]["Id"]
        print('user_Id in session : ', session["user_id"])
        return redirect("/")

@app.route('/profile', methods=['GET']) 
@login_required
def profile() : 
    # Create an API to get the current user and send it to profile
    user = getUser()
    return render_template('profile.html', user=user) 

@app.route('/profile/update', methods=['PUT']) 
def updateProfile() : 
    # Add functionality to update user profile and redirect to profile page with respective data
    redirect('/profile')


@app.route("/addAssets", methods=["GET", "POST"])
@login_required
def addassets():
    #For adding the assets from client side
    if request.method == "GET":
        return render_template("asset_form.html")
    else:
        print("I am at add asset")
        name = request.form.get("Name")
        description = request.form.get("Description")
        #image = request.files["image"]
        image = request.form.get("assetimage")
        print(image)
        tarBid = request.form.get("tarBid")
        today = date.today()
        db.execute("INSERT INTO Assets ( sellerId, Name, Description, Image, TimeStamp, tarBid) VALUES (:id, :name, :description, :image, :timestamp, :tarBid)", id = session["user_id"], name = name, description = description, image = image, timestamp = today, tarBid = tarBid)
        print("Queries added Successfully")
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