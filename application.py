import os

from datetime import timedelta
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_user_from_id,calculate_points, login_required, getuser, get_user_from_name, tobinary, debyte

import random

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

root = '/opus'

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
        f = False
        if (task['creator'] == session['user_id'] or session['user_id'] in debyte(task['collaborators'])):
            lst = tasks
        else:
            lst = other_tasks
            f = True
        creator = get_user_from_id(task['creator'],db)
        task['creator'] = creator["username"]
        task["collaborators-count"] = len(debyte(task['collaborators']))
        task["points"] = calculate_points(task)
        
        if f:
            if task["collaborators-count"] != task["cmax"]:
                lst.append(task)
        else:
            lst.append(task)

    random.shuffle(other_tasks)
    return render_template("index.html",len=len,active_tasks = tasks,tasks = other_tasks,user=getuser(session, db))


@app.route("/profile/<username>")
@login_required
def profile(username):
    username = username.replace('%20',' ')
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
    
    tags = [] #[("f091","Top 100")]

    return render_template("profile.html",tags=tags,other_user=other_user,user=user,active_tasks=tasks,task_count=len(tasks), len=len)

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
        # print("BANANA (GUY) (BILL)" +request.form['i'])
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


        return redirect(root+"/notifications")
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
        email = request.form.to_dict()["email"]
        db.execute("UPDATE users SET email = :email WHERE id = :id", email=email, id=user["id"])
        
    return render_template("edit_information.html",user=user,email=email,task_count=len(tasks))

@app.route("/edit_task/<id>", methods = ["GET", "POST"])
@login_required
def edit_task(id):
    task = db.execute("SELECT * FROM tasks WHERE id = :id", id=id)[0]
    #print(task['languages'])
    languages = task['languages'].replace(",","").split(' ')
    return render_template("edit_task.html", user=getuser(session, db), task = task, languages=languages)

@app.route("/editTask/<id>", methods = ["GET", "POST"])
@login_required
def editTask(id):
    task = db.execute("SELECT * FROM tasks WHERE id = :id", id=id)[0]
    print(request.form['description'])
    db.execute("UPDATE tasks SET description = :d, title = :name, cmax = :cmax, hmax = :hmax, hmin = :hmin, languages = :languages WHERE id = :id", d = request.form['description'], name= request.form['title'], cmax= request.form['cmax'], hmax= request.form['hmax'], hmin= request.form['hmin'], languages= request.form['languages'], id=id)
    return redirect(root+"/task/"+id)

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
                return redirect(root+"/")

    if error is not None: flash(error)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(root+"/")


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

            return redirect(root+"/")

    if error is not None: flash(error)

    return render_template("register.html")

@app.route("/taskcreator")
@login_required
def tcreate():
    return render_template("taskCreation.html",user=getuser(session, db))

@app.route("/createTask", methods=["GET","POST"])
def createTask():
    task = request.form.to_dict()
    db.execute("INSERT INTO tasks (title, description, languages, hmin, hmax, cmax, collaborators, creator) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", task['title'], task['description'], task['languages'], task['hmin'], task['hmax'], task['cmax'], tobinary([session['user_id']]), session['user_id'])
    return redirect("/opus/task/" + str(db.execute("SELECT * FROM tasks ORDER BY id DESC")[0]['id']))

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
        requestsent = False
        for noti in debyte(creator['notifications']):
            if noti['format'] == 'join-prompt':
                if noti['user'] == session['user_name'] and noti['task-id'] == task['id']:
                    requestsent = True
        posts = db.execute("SELECT * FROM messages WHERE task = :task ORDER BY id ASC", task=id)[-6:]
        uid_to_username = {}
        for p in posts:
            uid_to_username[p["author"]] = db.execute("SELECT * FROM users WHERE id = :id", id = p["author"])[0]["username"]
        
        person = db.execute("SELECT * FROM users WHERE id = :id", id=task['creator'])[0]
        person['notifications'] = debyte(person['notifications']) if person['notifications'] != None else []
        
        has_requested = False
        # print(person["notifications"])
        for notif in person['notifications']:
            if notif["format"] == "join-prompt":
                if "user" in notif and notif["user"] == session["user_name"]:
                    has_requested = True
                    break
        # print(has_requested)

        # print("HI GUYS ITS ME ALDEN UR FRIENDLY BOBERTA BAGGINS",posts)
        formatted_languages = task["languages"].replace(",","").split(" ")
        languages_string = ""
        for i in range(len(formatted_languages)):
            if len(formatted_languages[i]) > 0:
                if i == 0:
                    languages_string += formatted_languages[i]
                else:
                    languages_string += ", " + formatted_languages[i]
        print(languages_string)

        return render_template("task.html",should_disable = ("disabled" if has_requested else ""),is_user_task=(task["creator"]==session["user_id"]), uid_to_username=uid_to_username,is_collab_task=(session["user_id"] in ids),enumerate=enumerate,len=len,collaborators=collaborators,task=task, creator=creator, user=getuser(session, db),issent=requestsent, posts = posts, lenPosts = len(posts), languages_string=languages_string)
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
                    "task-name" : task['title']
                })
                db.execute("UPDATE users SET notifications = :p WHERE id = :id", p=tobinary(person['notifications']), id=collaborator)
            db.execute("DELETE FROM tasks WHERE id = :id", id=id)
            return redirect(root+"/")
        elif request.form['request_type'] == 'complete':
            points = calculate_points(task)
            collaborators = debyte(task['collaborators'])
            for collaborator in collaborators:
                person = db.execute("SELECT * FROM users WHERE id = :id", id=collaborator)[0]
                person['points'] += points if collaborator != session["user_id"] else 0
                person['numcomplete'] += 1
                person['notifications'] = debyte(person['notifications']) if person['notifications'] != None else []
                person['notifications'].insert(0, {
                    "format" : "complete",
                    "task-id" : task['id'],
                    "task-name" : task['title']
                })
                db.execute("UPDATE users SET notifications = :p WHERE id = :id", p=tobinary(person['notifications']), id=collaborator)
                db.execute("UPDATE users SET points = :p WHERE id = :id", p=person['points'], id=collaborator)
                db.execute("UPDATE users SET numcomplete = :p WHERE id = :id", p=person['numcomplete'], id=collaborator)
            db.execute("DELETE FROM tasks WHERE id = :id", id=id)
            return redirect(root+"/")
        elif request.form['request_type'] == 'join': 
            person = db.execute("SELECT * FROM users WHERE id = :id", id=task['creator'])[0]
            person['notifications'] = debyte(person['notifications']) if person['notifications'] != None else []
            person['notifications'].insert(0, {
                "user" : db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])[0]['username'],
                "format" : "join-prompt",
                "task-id" : task['id'],
                "task-name" : task['title']
            })
            db.execute("UPDATE users SET notifications = :p WHERE id = :id", p=tobinary(person['notifications']), id=task['creator'])
            return redirect(root+"/task/" + id)


        elif request.form['request_type'] == 'leave':
            task['collaborators'] = debyte(task['collaborators'])
            task['collaborators'].remove(session['user_id'])
            db.execute("UPDATE tasks SET collaborators = :p WHERE id = :id", id=id, p=tobinary(task['collaborators']))
            return redirect(root+"/task/" + id)
        elif request.form['request_type'] == 'create_message':
            
            task = db.execute("SELECT * FROM tasks WHERE id = :id", id=id)[0]
            ids = debyte(task['collaborators'])
            task['collaborators'] = [db.execute("SELECT * FROM users WHERE id = :id", id=a)[0] for a in ids]
            collaborators = task['collaborators']
            posts = db.execute("SELECT * FROM messages WHERE task = :task ORDER BY id ASC", task=id)[-6:]
            creator = db.execute("SELECT * FROM users WHERE id = :id", id=task['creator'])[0]
            requestsent = False
            for noti in debyte(creator['notifications']):
                if noti['format'] == 'join-prompt':
                    if noti['user'] == session['user_name'] and noti['task-id'] == task['id']:
                        requestsent = True
            uid_to_username = {}
            for p in posts:
                uid_to_username[p["author"]] = db.execute("SELECT * FROM users WHERE id = :id", id = p["author"])[0]["username"]
            # print("HI GUYS ITS ME ALDEN UR FRIENDLY BOBERTA BAGGINS",posts)
            return render_template("task.html",is_user_task=(task["creator"]==session["user_id"]), uid_to_username=uid_to_username,is_collab_task=(session["user_id"] in ids),enumerate=enumerate,len=len,collaborators=collaborators,task=task, creator=creator, user=getuser(session, db),issent=requestsent, posts = posts, lenPosts = len(posts))


@app.route("/createPost", methods=["GET", "POST"])
@login_required
def createpost():
    # print("AGLIS GUJALKS HGJLAI KGJSLDIDKGJOIASLGJAILTJGROISLTGJASLKJGAIOSLFJIO")
    # print(request.form)
    db.execute("INSERT INTO messages (id, author, task, message) VALUES (?, ?, ?, ?)", db.execute("SELECT count(*) FROM messages")[0]['count(*)'] + 1, request.form["author"], request.form["task"], request.form["message"])
    # task = db.execute("SELECT * FROM tasks WHERE id = :id", id=request.form['task'])[0]
    # posts = db.execute("SELECT * FROM messages WHERE task = :task ORDER BY id ASC", task=id)[-6:]
    # uid_to_username = {}
    # for p in posts:
    #     uid_to_username[p["author"]] = db.execute("SELECT * FROM users WHERE id = :id", id = p["author"])[0]["username"]
    # print(posts)
    return ":D"

@app.route("/get_messages/<id>", methods=["GET", "POST"])
def get_messages(id):
    posts = db.execute("SELECT * FROM messages WHERE task = :task ORDER BY id ASC", task=id)
    uid_to_username = {}
    for p in posts:
        uid_to_username[p["author"]] = db.execute("SELECT * FROM users WHERE id = :id", id = p["author"])[0]["username"]

    return jsonify(result={"posts" : posts,"uid_to_username" : uid_to_username})

def solve(s0, s1):
    s0 = s0.lower()
    s1 = s1.lower()
    s1 = s1.replace(",","")
    s1 = s1.replace(".","")
    s0 = s0.replace(",","")
    s0 = s0.replace(".","")
    s0List = s0.split(" ")
    s1List = s1.split(" ")
    stopwords = set(['the', 'is', 'and', 'a', 'i']) # good enough, okay?
    s0List = filter(lambda x : not (x in stopwords), s0List)
    return len(list(set(s0List)&set(s1List)))

@app.route("/search", methods=["GET"])
@login_required
def searchf():
    return render_template("search.html", tasks=[], user=getuser(session, db))

@app.route("/searchresult", methods=["POST", "GET"])
@login_required
def searchr():
    tasks = db.execute("SELECT * FROM tasks")
    query = request.form.get("search")
    newtasks = sorted(tasks, key=lambda x : solve((x['title'] + " " + x['description'] + " " + x['languages']), query), reverse=True)
    if len(newtasks) > 10:
        newtasks = newtasks[:10]
    for task in newtasks:
        creator = get_user_from_id(task['creator'],db)
        task['creator'] = creator["username"]
        task["collaborators-count"] = len(debyte(task['collaborators']))
        task["points"] = calculate_points(task)
    return render_template("search.html", tasks=newtasks, user=getuser(session, db))


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return None # TODO - error handler


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)