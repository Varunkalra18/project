from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_mail import Mail, Message
import datetime

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
        
def getAssetVerifiedTimestamp(rows) : 
    final_asset_list = []
    expired_asset_list = [] 
    for asset in rows : 
        registered_AT = datetime.datetime.strptime(asset["AT"], "%Y-%m-%d %H:%M:%S")
        print('date now : ', datetime.datetime.now())
        print('registered_AT : ', registered_AT)
        expire_time = registered_AT + datetime.timedelta(0,int(asset["bidTime"]))
        print('expire_time : ', expire_time)
        if datetime.datetime.now() < expire_time : 
            final_asset_list.append(asset)
        else : 
            expired_asset_list.append(asset) 
    print("final asset list is here : -------------> ", final_asset_list)
    return (final_asset_list, expired_asset_list)



# Function to send mail to users
def sendMail(email, subject, message) : 
    from application import mail, app
    with app.app_context() : 
        msg=Message(subject,sender="appraisal.auc2021.support",recipients=[email])        
        msg.body=message
        mail.send(msg)
    
def closeExpiredAssets(rows) : 
    print("asset in closeExpiredAsests : ", rows)
    for asset in rows : 
            print('not asset["maxBidUser"] of current asset : ', asset)
            if asset["isSold"] == 0 : 
                rows_user = db.execute("SELECT Email, Username from User WHERE Id = :id", id=asset["SellerId"])
                if not asset["maxBidUser"] :
                    print("maxBidUser")
                    
                    # print('owner of the asset and maxUser : ', rows)
                    sendMail(rows_user[0]["Email"], "No Bidding on Your Product .", "Your Product : {} ,activated on : {} has no biddings .".format(asset["Name"], asset["AT"]))
                    sendMail("management.appraisal2021@gmail.com", "Product Denial", "No Bidding Done on {} , product uploaded by {}({})".format(asset["Name"], rows_user[0]["Username"], rows_user[0]["Email"]))
                else : 
                    print('This is buyer id in utility.p7y : ', asset["maxBidUser"])
                    user_buyer = db.execute("SELECT Email, Username from User WHERE Id = :id", id=asset["maxBidUser"])
                    print('Buyer of the closing asset : ', user_buyer)
                    sendMail(rows_user[0]["Email"],"Product Purchase reminder .. !!" , "Your Product {} has been Purchased by {} ({}). Maximum Bid was : {}".format(asset["Name"], user_buyer[0]["Username"], user_buyer[0]["Email"], asset["maxBid"]))
                    
                print('Coming here to close asset and assetId : ', asset['Name'], asset["Id"])
                db.execute("UPDATE Assets SET isSold=True WHERE Id=:id", id=asset["Id"])
        