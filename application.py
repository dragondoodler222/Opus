import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_user_from_id,calculate_points, login_required, getuser, get_user_from_name, tobinary, debyte

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
    alltasks = db.execute("SELECT * FROM tasks")

    tasks = []
    other_tasks = []
    for task in alltasks:
        lst = None
        if (task['creator'] == session['user_id'] or session['user_id'] in debyte(task['collaborators'])):
            lst = tasks
        else:
            lst = other_tasks
        creator = get_user_from_id(task['creator'],db)
        task['creator'] = creator["username"]
        task["collaborators-count"] = len(debyte(task['collaborators']))
        task["points"] = calculate_points(task)
        
        if not (lst == other_tasks and (task["collaborators-count"] == task["cmax"])):
            lst.append(task)
    return render_template("index.html",len=len,active_tasks = tasks,tasks = other_tasks,user=getuser(session, db))


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
        if (task['creator'] == other_user['id'] or other_user['id'] in debyte(task['collaborators'])):
            task['creator'] = other_user["username"]
            task["collaborators-count"] = len(debyte(task['collaborators']))
            task["points"] = calculate_points(task)
            tasks.append(task)
    
    return render_template("profile.html",other_user=other_user,user=user,active_tasks=tasks,task_count=len(tasks), len=len)

@app.route("/notifications",methods=['POST', 'GET'])
@login_required
def notifications():
    # notifications = [
    #     {
    #         "format" : "join-prompt",
    #         "user" : "dashiell",
    #         "task-id" : 1
    #     },
    #     {
    #         "format" : "accept-notification",
    #         "task-name" : "Scheme Project :)",
    #         "task-id" : 2
    #     },
    #     {
    #         "format" : "reject-notification",
    #         "task-name" : "Ada Project :(",
    #         "task-id" : 3
    #     }
    # ]
    notifications = db.execute("SELECT * FROM users WHERE id = :id", id=session['user_id'])[0]['notifications']
    if notifications:
        notifications = debyte(notifications)
    else:
        notifications = []

    if request.method == "POST":
        notifications.pop(int(request.form['i']))
        print("BANANA (GUY) (BILL)" +request.form['i'])
        db.execute("UPDATE users SET notifications = :c WHERE id = :id", id=session['user_id'], c=tobinary(notifications))

        if request.form["request_type"] == "Accept":
            the_task = db.execute("SELECT * FROM tasks WHERE id = :id", id=request.form['identifier'])[0]
            data = debyte(the_task['collaborators'])
            if data is None: data = []
            person = db.execute("SELECT * FROM users WHERE username = :user", user=request.form['user'])[0]
            if not (person['id'] in data):
                data.append(person['id'])
            db.execute("UPDATE tasks SET collaborators = :c WHERE id = :id", id=request.form['identifier'], c=tobinary(data))
            othersNotifications = debyte(person['notifications'])
            othersNotifications.insert(0,{
                "format" : "accept-notification",
                "task-name" : the_task['title'],
                "task-id" : the_task['id']
                })
            if len(othersNotifications) > 11:
                othersNotifications = other_user[:11]
            db.execute("UPDATE users SET notifications = :c WHERE id = :id", id=person['id'], c=tobinary(othersNotifications))

        else:
            the_task = db.execute("SELECT * FROM tasks WHERE id = :id", id=request.form['identifier'])[0]
            person = db.execute("SELECT * FROM users WHERE username = :user", user=request.form['user'])[0]
            othersNotifications = debyte(person['notifications'])
            othersNotifications.insert(0,{
                "format" : "reject-notification",
                "task-name" : the_task['title'],
                "task-id" : the_task['id']
                })
            db.execute("UPDATE users SET notifications = :c WHERE id = :id", id=person['id'], c=tobinary(othersNotifications))


        return redirect("/notifications")
    else:
        user=getuser(session, db)
        tasks = db.execute("SELECT * FROM tasks WHERE creator = :id", id=session["user_id"])
        newnotifications = []
        for noti in notifications:
            if noti['format'] == 'join-prompt':
                newnotifications.append(noti)
        db.execute("UPDATE users SET notifications = :c WHERE id = :id", id=session['user_id'], c=tobinary(newnotifications))
        return render_template("notifications.html",db=db,notifications=notifications,user=user,active_tasks=tasks,task_count=len(tasks), len=len)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        return render_template("response.html",user=getuser(session, db))
    else:
        return render_template("search.html",user=getuser(session, db))

@app.route("/editinfo", methods=["GET","POST"])
@login_required
def edit_information():
    user = getuser(session, db)
    alltasks = db.execute("SELECT * FROM tasks")
    tasks = []
    for task in alltasks:
        if (task['creator'] == user['id'] or user['id'] in debyte(task['collaborators'])):
            task['creator'] = user["username"]
            task["collaborators-count"] = len(debyte(task['collaborators']))
            task["points"] = calculate_points(task)
            tasks.append(task)
    email = user["email"]
        
    if request.method == "POST":
        to_save = request.form.to_dict()
        db.execute("UPDATE users SET email = :email WHERE id = :id", email=email, id=user["id"])
        
    return render_template("edit_information.html",user=user,email=email,task_count=len(tasks))

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

        elif not request.form.get("email"):
            error = "Error: Invalid Email"

        elif not request.form.get("password"):
            error = "Error: Invalid Password"

        elif not request.form.get("password") == request.form.get("confirm-password"):
            error = "Error: Passwords do not match"

        elif len(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))) != 0:
            error = "Error: Username is already taken"
        else:
            db.execute("INSERT INTO users (id, username, hash, email) VALUES (?, ?, ?, ?)", db.execute("SELECT count(*) FROM users")[0]['count(*)'] + 1, request.form.get("username"), generate_password_hash(request.form.get("password")), request.form.get("email"))

            session["user_id"] = db.execute("SELECT count(*) FROM users")[0]['count(*)']
            session["user_name"] = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])[0]['username']

            return redirect("/")

    if error is not None: flash(error)

    return render_template("register.html")

@app.route("/taskCreation")
@login_required
def taskCreation():
    return render_template("taskCreation.html",user=getuser(session, db))

@app.route("/createTask", methods=["POST"])
def createTask():
    task = request.form.to_dict()
    db.execute("INSERT INTO tasks (id, title, description, languages, hmin, hmax, cmax, collaborators, creator) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",db.execute("SELECT count(*) FROM tasks")[0]['count(*)'] + 1, task['title'], task['description'], task['languages'], task['hmin'], task['hmax'], task['cmax'], tobinary([session['user_id']]), session['user_id'])
    return redirect("/task/" + str(db.execute("SELECT count(*) FROM tasks")[0]['count(*)']))

@app.route("/task/<id>", methods=["GET", "POST"])
@login_required
def task(id):
    if request.method == "GET":
        task = db.execute("SELECT * FROM tasks WHERE id = :id", id=id)[0]
        creator = db.execute("SELECT * FROM users WHERE id = :id", id=task['creator'])[0]
        ids = debyte(task['collaborators'])
        task['collaborators'] = [db.execute("SELECT * FROM users WHERE id = :id", id=a)[0] for a in ids]
        collaborators = task['collaborators']
        task["points"] = calculate_points(task)
        return render_template("task.html",is_user_task=(task["creator"]==session["user_id"]),is_collab_task=(session["user_id"] in ids),enumerate=enumerate,len=len,collaborators=collaborators,task=task, creator=creator, user=getuser(session, db))
    else:
        task = db.execute("SELECT * FROM tasks WHERE id = :id", id=id)[0]
        # four options given - delete, complete, join, leave
        if request.form['request_type'] == 'delete':
            collaborators = debyte(task['collaborators'])
            for collaborator in collaborators:
                person = db.execute("SELECT * FROM users WHERE id = :id", id=collaborator)[0]
                person['notifications'] = debyte(person['notifications'])
                person['notifications'].insert(0, {
                    "format" : "delete",
                    "task-id" : task['id'],
                })
                db.execute("UPDATE users SET notifications = :p WHERE id = :id", p=tobinary(person['notifications']), id=collaborator)
            db.execute("DELETE FROM tasks WHERE id = :id", id=id)
            return redirect("/")
        elif request.form['request_type'] == 'complete':
            points = calculate_points(task)
            collaborators = debyte(task['collaborators'])
            for collaborator in collaborators:
                person = db.execute("SELECT * FROM users WHERE id = :id", id=collaborator)[0]
                person['points'] += points
                person['notifications'] = debyte(person['notifications'])
                person['notifications'].insert(0, {
                    "format" : "complete",
                    "task-id" : task['id'],
                })
                db.execute("UPDATE users SET notifications = :p WHERE id = :id", p=tobinary(person['notifications']), id=collaborator)
                db.execute("UPDATE users SET points = :p WHERE id = :id", p=person['points'], id=collaborator)
            db.execute("DELETE FROM tasks WHERE id = :id", id=id)
            return redirect("/")
        elif request.form['request_type'] == 'join': 
            person = db.execute("SELECT * FROM users WHERE id = :id", id=task['creator'])[0]
            person['notifications'] = debyte(person['notifications'])
            person['notifications'].insert(0, {
                "user" : db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])[0]['username'],
                "format" : "join-prompt",
                "task-id" : task['id'],
            })
            db.execute("UPDATE users SET notifications = :p WHERE id = :id", p=tobinary(person['notifications']), id=task['creator'])
            return redirect("/task/" + id)


        elif request.form['request_type'] == 'leave':
            task['collaborators'] = debyte(task['collaborators'])
            task['collaborators'].remove(session['user_id'])
            db.execute("UPDATE tasks SET collaborators = :p WHERE id = :id", id=id, p=tobinary(task['collaborators']))
            return redirect("/task/" + id)



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return None # TODO - error handler


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)