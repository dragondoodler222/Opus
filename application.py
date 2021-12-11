import os

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

# Custom filter
#app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///passwords.db")

@app.route("/")
@login_required
def index():
    tasks = [{
        "points" : 500,
        "title" : "Python Project (Very Charitable)",
        "creator" : "jonah",
        "description" : "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce nibh sem, tristique sit amet nisi eu, venenatis dapibus urna. Vivamus molestie iaculis sem in scelerisque. Mauris tempus rhoncus mauris. In hac habitasse platea dictumst. Nulla vitae tellus sed nulla tincidunt consectetur. Nulla sed sem in eros aliquet consequat. Phasellus condimentum nisl at ipsum consectetur venenatis. Aliquam lorem odio, sagittis ut lectus nec, maximus pretium arcu. Donec molestie vulputate congue. Aenean id purus mollis, dictum ex et, eleifend eros. Proin lacinia tristique nibh, in dapibus lacus sagittis gravida. Praesent aliquam tincidunt tempus.",
        "hrs-min" : 4,
        "hrs-max" : 5,
        "collaborators-count" : 2,
        "collaborators-max" : 3
    }]
    return render_template("index.html",tasks = tasks)


@app.route("/account")
@login_required
def account():
    return render_template("account.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        return render_template("response.html")
    else:
        return render_template("search.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return None # TODO - error handler

        # Ensure password was submitted
        elif not request.form.get("password"):
            return None # TODO - error handler

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return None # TODO - error handler

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        if not request.form.get("username"):
            error = "Error: Invalid Username"

        elif not request.form.get("password"):
            error = "Error: Invalid Password"

        elif not request.form.get("password") == request.form.get("confirm-password"):
            error = "Error: Passwords do not match"

        elif len(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))) != 0:
            error = "Error: Username is already taken"
        else:
            db.execute("INSERT INTO users (id, username, hash) VALUES (?, ?, ?)", db.execute("SELECT count(*) FROM users")[0]['count(*)'] + 1, request.form.get("username"), generate_password_hash(request.form.get("password")))

            session["user_id"] = db.execute("SELECT count(*) FROM users")[0]['count(*)']

            return redirect("/")

    if error is not None: flash(error)

    return render_template("register.html")

@app.route("/taskCreation")
def taskCreation():
    return render_template("taskCreation.html")

@app.route("/createTask", methods=["GET", "POST"])
def createTask():
    #if request.method == "POST":
        


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return None # TODO - error handler


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
