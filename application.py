import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, getuser, get_user_from_name, tobinary, debyte

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
    tasks = db.execute("SELECT * FROM tasks WHERE creator = :id", id=session["user_id"])
    return render_template("index.html",tasks = tasks,user=getuser(session, db))


@app.route("/profile/<username>")
@login_required
def profile(username):
    user = getuser(session, db)
    if user["username"] != username:
        other_user = get_user_from_name(username, db)
    else:
        other_user = user
    alltasks = db.execute("SELECT * FROM tasks")

    tasks = []
    for task in alltasks:
        if (alltasks['creator'] = other_user['id'] or other_user['id'] in debyte(alltasks['collaborators'])):
            tasks.append(task)
    
    return render_template("profile.html",other_user=other_user,user=user,active_tasks=tasks,task_count=len(tasks), len=len)

@app.route("/notifications")
@login_required
def notifications():
    user=getuser(session, db)
    tasks = db.execute("SELECT * FROM tasks WHERE creator = :id", id=session["user_id"])

    return render_template("notifications.html",user=user,active_tasks=tasks,task_count=len(tasks), len=len)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        return render_template("response.html",user=getuser(session, db))
    else:
        return render_template("search.html",user=getuser(session, db))



@app.route("/login", methods=["GET", "POST"])
def login():

    """Log user in"""

    # Forget any user_id
    session.clear()

    error = None

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error = "Error: No Username"

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "Error: No Password"

        else:
            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=request.form.get("username"))

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                error = "Error: Invalid Username or Password"

            else:
                # Remember which user has logged in
                session["user_id"] = rows[0]["id"]
                session["user_name"] = rows[0]["username"]

                # Redirect user to home page
                return redirect("/")

    if error is not None: flash(error)
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

    return render_template("register.html",user=getuser(session, db))

@app.route("/taskCreation")
@login_required
def taskCreation():
    return render_template("taskCreation.html",user=getuser(session, db))

@app.route("/createTask", methods=["POST"])
def createTask():
    task = request.form.to_dict()
    db.execute("INSERT INTO tasks (id, title, description, languages, image, hmin, hmax, cmax, collaborators, creator) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",db.execute("SELECT count(*) FROM tasks")[0]['count(*)'] + 1, task['title'], task['description'], task['languages'], task['image'], tasks['hmin'], tasks['hmax'], tasks['cmax'], tobinary([session['user_id']]), session['user_id'])
    return redirect("/task/" + str(task['id']))

@app.route("/task/<id>")
@login_required
def task(id):
    task = db.execute("SELECT * FROM tasks WHERE id = :id", id=id)[0]
    creator = db.execute("SELECT * FROM users WHERE id = :id", id=task['creator'])[0]
    task['collaborators'] = [db.execute("SELECT * FROM users WHERE id = :id", id=a)[0] for a in debyte(task['collaborators'])]
    print(task)
    print(creator)
    return render_template("task.html", task=task, creator=creator, user=getuser(session, db))

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return None # TODO - error handler


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)