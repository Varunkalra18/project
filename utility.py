from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify

db = SQL("sqlite:///test.db")

def getUser() : 
    user_id = session["user_id"]
    user = (db.execute("SELECT * FROM User WHERE Id=:id", id=user_id))[0]
    
    user.pop("Passwords")
    if len(user) == 0 : 
        return render_template("sorry.html", text="Invalid user logged ... Not Authorized .. !!")
    return user 


def checkEmpty(data) : 
    if not data : 
        return "No data came .. !!"
    for data_item in data : 
        if not data[data_item] : 
            return {error : "All fields are mandatory"}