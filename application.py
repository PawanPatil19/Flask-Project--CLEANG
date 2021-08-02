import os
import uuid
import random

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash



from helpers import login_required


# Configure application
app = Flask(__name__)



# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True



# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///clean.db")




@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", error="Invalid Credentials! Please Try Again")


        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
             return render_template("apology.html", error="Invalid Username/Password! Please Try Again")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"]=rows[0]["username"]
        session["name"]=rows[0]["name"]


        # Redirect user to home page
        return render_template("home.html", rows=rows)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")





@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("fname"):
            return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("email"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("phone"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("password"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")


        # Ensure confirm password is correct
        elif request.form.get("password") != request.form.get("repassword"):
            return render_template("apology.html", error="Wrong Password! Please Try Again.")

        # Query database for username if already exists
        elif db.execute("SELECT * FROM users WHERE username = :username",
            username=request.form.get("username")):
            return render_template("apology.html", error="Username already taken ! Please Try Again.")

        # Insert user and hash of the password into the table
        db.execute("INSERT INTO users(name,email,phone,username, hash) VALUES (:name,:email,:phone,:username, :hash);",
            name=request.form.get("fname"), email=request.form.get("email"), phone=request.form.get("phone"),username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
            username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return render_template("login.html",message="You are registered!")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("newpassword"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("renewpassword"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")


        # Ensure confirm password is correct
        elif request.form.get("newpassword") != request.form.get("renewpassword"):
            return render_template("apology.html", error="Wrong Password! Please Try Again.")

        # Query database for username if already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username",username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1:
             return render_template("apology.html", error="Invalid Username! Please Try Again")

        # Insert user and hash of the password into the table
        db.execute("UPDATE users SET hash=:hash where username=:username;",
             hash=generate_password_hash(request.form.get("newpassword")),username=request.form.get("username"))

        # Query database for username

        # Redirect user to home page
        return render_template("login.html",message="Password Changed Successfully!")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("forgot.html")




@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    if request.method == "POST":
        rows = db.execute("SELECT * FROM orders WHERE userid = :uid",uid=session["username"])
        return render_template("history.html",rows=rows)
    else:
        return render_template("history.html")


@app.route("/order", methods=["GET", "POST"])
@login_required
def order():

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("ordername"):
            return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("ordercontact"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("orderadd1"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        ordertype = request.form.getlist('ord')
        ordtime=request.form.get("ordertime")
        for x in range(1000000):
            ordersid=random.randint(1, 1000000) * 5
        amount=0

        if "Sanitization" in ordertype:
            amount=amount+400.50
        if "Street Cleaning" in ordertype:
            amount=amount+200.50
        if "Animal Protection" in ordertype:
            amount=amount+0.00
        if "Beach Cleaning" in ordertype:
            amount=amount+2000.00
        if "Plant Trees" in ordertype:
            amount=amount+10.00
        if "Waste Collection" in ordertype:
            amount=amount+70.00






        db.execute("INSERT INTO orders(userid,order_id,order_name,order_contact, order_address1, order_address2, order_date, order_time, order_type, order_amount) VALUES (:userid,:oid,:oname,:ocontact,:oadd1,:oadd2,:odate,:otime,:otype,:oamt);",
            userid=session["username"], oid=ordersid, oname=request.form.get("ordername"), ocontact=request.form.get("ordercontact"),
            oadd1=request.form.get("orderadd1"), oadd2=request.form.get("orderadd2"),
            odate=request.form.get("orderdate"),otime=ordtime,otype=ordertype, oamt=amount)

        rows = db.execute("SELECT * FROM orders where userid = :uid",
                          uid=session["username"])






        # Redirect user to home page
        return render_template("history.html",amount=amount,rows=rows,message="Your order is placed successfully!! Amount to be paid is ")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("order.html")

@app.route("/recruit", methods=["GET", "POST"])
def recruit():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("appname"):
            return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("appphone"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("appemail"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("appjob"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("appurl"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        elif not request.form.get("appidentity"):
           return render_template("apology.html", error="Invalid Credentials! Please Try Again")

        for x in range(1000000):
            applyid=random.randint(1, 1000000) * 5



        db.execute("INSERT INTO jobs(app_id,app_name,app_phone,app_email,app_job,app_url,app_idn) VALUES (:appid,:appname,:appphone,:appemail,:appjob, :appurl, :appidentity);",
            appid=applyid, appname=request.form.get("appname"), appphone=request.form.get("appphone"), appemail=request.form.get("appemail"), appjob=request.form.get("appjob"), appurl=request.form.get("appurl"), appidentity=request.form.get("appidentity"))

        # Query database for username
        rows = db.execute("SELECT * FROM jobs WHERE app_email = :appemail",
            appemail=request.form.get("appemail"))


        return render_template("status.html",rows=rows)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("recruit.html")

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/vision")
def vision():
    return render_template("vision.html")

@app.route("/status", methods=["GET", "POST"])
def status():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("appidinp"):
            return render_template("apology.html", error="Enter your Application ID! Please Try Again")


        rows = db.execute("SELECT * FROM jobs WHERE app_id = :appidinp",
            appidinp=request.form.get("appidinp"))

        return render_template("status.html",rows=rows)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("status.html")





def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("apology.html",error="Runtime Error")


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.config['ENV'] = 'development'
    app.config['DEBUG'] = True
    app.config['TESTING'] = True