import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from datetime import datetime
from flask_session import Session
import json
from tempfile  import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from support import login_required, admin_login_required, user_first_land
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

# User Routes
@app.route('/', methods=['GET']) 
@login_required
#@user_first_land
def home() : 
    rows = db.execute("SELECT U.Username, U.profileImage, A.* FROM Assets AS A INNER JOIN User AS U on U.Id = A.SellerId")
    print(rows) 
    return render_template("index.html", row=rows) 

@app.route('/register', methods=['GET', 'POST']) 
def register() : 
    if request.method == "GET":
        return render_template("register.html") 
    else :      
        username = request.form.get("username")
        emailId = request.form.get("emailId")
        password = request.form.get("password")
        an = request.form.get("PanNo")
        govid = request.form.get("Govid")
        timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        user = db.execute("SELECT * FROM User WHERE username=:username", username = username)
        
        if len(user) != 0:
            return render_template("register.html", error="Username already exist .. !!")
        email = db.execute("SELECT * FROM User WHERE Email=:email", email = emailId)
        if len(email) != 0:
            return render_template("register.html", error="Email already exist .. !!")
        hashed = generate_password_hash(password)
        db.execute("INSERT INTO User (Username, Email, Passwords, PanNumber, GovId, Timestamp) VALUES( :username, :emailId, :pasword, :adharnumber, :govid, :timestamp)", username = username, emailId = emailId, pasword = hashed, adharnumber = an, govid = govid, timestamp = timestamp)
        return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login() :
    session.clear() 
    
    if request.method == "GET" : 
        return render_template("login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        rows = db.execute("SELECT * FROM User WHERE Email = :email", email = email)
        if len(rows) == 0:
            return render_template("sorry.html", text = "Invalid User")
        if not check_password_hash(rows[0]["Passwords"], password):
            return render_template("sorry.html", text="Invalid User")
        if rows[0]["isBlocked"] == 1 : 
            return render_template("sorry.html", text="This user has been blocked by ADMIN") 
        session["user_id"] = rows[0]["Id"]
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
    return redirect('/profile')


@app.route("/addAssets", methods=["GET", "POST"])
@login_required
def addassets():
    #For adding the assets from client side
    if request.method == "GET":
        return render_template("asset_form.html")
    else:
        name = request.form.get("Name")
        description = request.form.get("Description")
        image = request.form.get("assetImage")
        startBid = request.form.get("startBid")
        tarBid = request.form.get("tarBid")
        today = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        db.execute("INSERT INTO Assets ( sellerId, Name, Description, Image, TimeStamp, tarBid, startBid, maxBid) VALUES (:id, :name, :description, :image, :timestamp, :tarBid, :startBid, :maxBid)", id = session["user_id"], name = name, description = description, image = image, timestamp = today, tarBid = tarBid, startBid = startBid, maxBid = int(startBid))
        return redirect('/Assets') 
    return render_template("sorry.html")

@app.route("/Assets", methods=["GET"])
@login_required
def assets():
    user_id = session["user_id"]
    rows = db.execute("SELECT * FROM Assets WHERE Id=:id ", id=user_id) 
    return render_template("assets.html", rows=rows)


@app.route("/bookmark", methods=["GET", "POST"])
@login_required
def bookmark():
    if request.method == "GET":
        row = db.execute("SELECT * FROM bookmark WHERE userId = :userid", userid = session["user_id"])
        assets = []
        for asset in row:
            assd = db.execute("SELECT *FROM Assets WHERE Id = :assetid", assetid = asset["assetId"])
            assets.append(assd)
        print(assets)
        print("")
        return render_template("bookmark.html", row = assets)
    else:
        assetid = request.form.get("assetid")
        db.execute("INSERT INTO bookmark (assetId, userId) VALUES (:assetid, :userid)", assetid = assetid, userid = session["user_id"])
        return redirect("/")

@app.route("/mybids",methods=['GET', 'POST']) 
@login_required
def getMyBids() : 
    user = session["user_id"]
    rows= db.execute("SELECT * FROM Transactions WHERE BuyerId=:buyerid", buyerid=user) 
    return render_template("mybids.html", rows=rows) 

@app.route("/midpagedetails", methods=['POST'])
@login_required
def midPageRender() : 
    user = session["user_id"]
    print('User in mid page : ', user)
    profileImage = request.form.get('profile-image-url')
    dob = request.form.get('dob')
    mob = request.form.get('mob')
    occupation = request.form.get('occupation')
    print('profileImage : ', profileImage)
    print('dob : ', dob)
    print('mob : ', mob)
    print('occupation : ', occupation)
    db.execute('UPDATE User SET profileImage=:image, DOB=:dob, ContactNumber=:contact, occupation=:occupation WHERE Id=:id', image=profileImage, dob=dob, contact=mob, occupation=occupation, id=session["user_id"])
    db.execute("UPDATE User SET firstLand=False WHERE Id=:id", id=session["user_id"])
    return redirect('/')

@app.route("/midpage/skip")
def midpageSkip() : 
    db.execute("UPDATE User SET firstLand=False WHERE Id=:id", id=session["user_id"])
    return redirect('/') 
    
@app.route('/bid', methods=['POST'])
def bidAsset() : 
    assetId = request.form.get('assetId')
    maxBid = request.form.get('bid_amount') 
    loggedInUser = session["user_id"]
    print('asset id : ', assetId, ' and bid amount : ', maxBid)
    db.execute('UPDATE Assets SET maxBid=:maxBid, maxBidUser=:maxBidUser WHERE Id=:id', maxBid=maxBid, id=assetId, maxBidUser=loggedInUser)
    asset = db.execute('SELECT * FROM Assets WHERE Id=:id', id=assetId)
    print('This is the asset to get bidded : ', asset)
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    db.execute('INSERT INTO Transactions (SellerId, BuyerId, Amount, AssetId, TimeStamp) VALUES (:sellerid, :buyerid, :amount, :assetId, :timestamp)', sellerid=asset[0]["SellerId"], buyerid=loggedInUser, amount=maxBid, assetId=asset[0]["Id"], timestamp=timestamp)
    print('Here in assets')
    return redirect('/') 
    


# Admin Routes
@app.route('/admin', methods=['GET'])
@admin_login_required
def adminHome() : 
    rows = db.execute("SELECT Id, Username, Email, ContactNumber, PanNumber, GovId, profileImage, DOB, occupation, isBlocked FROM User") 
    return render_template("admin.index.html", rows=rows) 

@app.route('/admin/login', methods=['GET', 'POST']) 
def adminLogin() : 
    if(request.method == "GET") : 
        session.clear()
        return render_template("admin.login.html") 
    else : 
        adminEmail = request.form.get("emailAdmin") 
        adminPass = request.form.get("passwordAdmin")
        rows = db.execute("SELECT * FROM Admin WHERE Email = :email", email = adminEmail) 
        if len(rows) == 0:
            return render_template("sorry.html", text = "Invalid Admin")
        if not (rows[0]["Passwords"] == adminPass):
            return render_template("sorry.html", text="Invalid Admin")
        session["user_id"] = rows[0]["Id"]
        return redirect("/admin")

@app.route("/admin/assets/active")
@admin_login_required
def getActiveAssets() : 
    rows = db.execute("SELECT * FROM Assets WHERE status='Accepted' and isActivated=True")
    return render_template("admin.activeassets.html",rows=rows)

@app.route("/admin/assets/pending")
@admin_login_required
def getPendingAssets() : 
    rows = db.execute("SELECT A.*, U.Username FROM Assets AS A INNER JOIN User AS U on U.Id=A.SellerId AND status='Pending' AND isActivated=False")
    return render_template("admin.pendingassets.html",rows=rows)

@app.route("/admin/assets/accepted")
@admin_login_required
def getAcceptedAssets() : 
    rows = db.execute("SELECT A.*, U.Username FROM Assets AS A INNER JOIN User AS U on U.Id=A.SellerId AND status='Accepted'")
    return render_template("admin.acceptedassets.html", rows=rows) 


@app.route("/admin/toggle/blockUser")
@admin_login_required
def blockUser() : 
    td = request.args.get("td")
    print('This is before td : ', td)
    todo = not bool(int(td))
    print('This is after td : ', todo)
    user_id = request.args.get("user")
    db.execute("UPDATE User SET isBlocked=:td WHERE Id=:id", id=user_id, td=todo) 
    return redirect('/admin')

@app.route("/admin/toggle/asset/status") 
@admin_login_required
def changeAssetStatus() : 
    status = request.args.get("status")
    assetId = request.args.get("assetId")
    print('This is status and id : ', status, assetId)
    db.execute("UPDATE Assets SET status=:status WHERE Id=:id", status=status, id=assetId)
    return redirect("/admin/assets/pending")
    
# Logout is common for Admin and normal user
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