import os
from flask import *
from functools import wraps
from cs50 import SQL

db = SQL("sqlite:///test.db")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user_id")
        print('User in session is ; ',user)
        if user is None:
            return redirect("/login")
        # else : 
        #     user = db.execute("SELECT * FROM User WHERE Id=:id", id=user)
        #     if(len(user) == 0) : 
        #         return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



