import os
from flask import *
from functools import wraps
from cs50 import SQL
from threading import *

from utility import getAssetVerifiedTimestamp, closeExpiredAssets, sendMail

db = SQL("sqlite:///test.db")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user_id")
        if user is None:
            return redirect("/login")
        else : 
            user = db.execute("SELECT * FROM User WHERE Id=:id", id=user)
            if(len(user) == 0) :
                return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f) : 
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_user = session.get("user_id")
        if admin_user is None:
            return redirect("/admin/login")
        else : 
            admin = db.execute("SELECT * FROM Admin WHERE Id=:id", id=admin_user)
            if(len(admin) == 0) :
                return redirect("/admin/login")
        return f(*args, **kwargs)
    return decorated_function

def user_first_land(f) : 
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        print('user_id : ', user_id)
        user = db.execute("SELECT * FROM User WHERE Id=:id", id=user_id)
        print(user[0])
        if int(user[0]["firstLand"]) == 1 : 
            # Redirect to middle page
            print('I am here in middle page')
            return render_template("midDetailsPage.html")
        else : 
            
            print('user_id while rendering index.html : ', user_id)
            rows = db.execute("SELECT U.Username, U.profileImage, A.* FROM Assets AS A INNER JOIN User AS U on A.isActivated = True AND U.Id = A.SellerId AND A.SellerId != :user_id AND A.status = 'Accepted'", user_id=user_id)
            print('rows in index.html : ', rows)
            book = db.execute("SELECT assetId FROM bookmark WHERE userId = :userid", userid = session["user_id"])
            (rows, expired_rows) = getAssetVerifiedTimestamp(rows) 
            print('Expired rows in support py : ', expired_rows)
            # sendMail("prasheetp@gmail.com", "hello this is testing mail", "testing mail") 
            # closeExpiredAssets(expired_rows) 
            try : 
                closingAssetsThread = Thread(target=closeExpiredAssets, args=(expired_rows,))
                closingAssetsThread.start() 
            except error : 
                print('Error in thread : ', error)
            return render_template("index.html", row=rows, books=book) 
        return f(*args, **kwargs)
    return decorated_function

