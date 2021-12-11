import os
import requests
import urllib.parse
import pickle

from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def tobinary(obj):
    return pickle.dumps(obj)

def debyte(obj):
    return pickle.loads(obj)

def getuser(session, db):
    user =  db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])[0]
    
    user["level"]=int(user['points']**.5//10)
    user["level-progress"] = (user['points']**.5%8)/(((user["level"]+1)*10)**2)

    return user

def get_user_from_name(name, db):
    user =  db.execute("SELECT * FROM users WHERE username = :name", name=name)[0]
    
    user["level"]=int(user['points']**.5//10)
    user["level-progress"] = (user['points']**.5%8)/(((user["level"]+1)*10)**2)

    return user

def get_user_from_id(id, db):
    user =  db.execute("SELECT * FROM users WHERE id = :id", id=id)[0]
    
    user["level"]=int(user['points']**.5//10)
    user["level-progress"] = (user['points']**.5%8)/(((user["level"]+1)*10)**2)

    return user

def calculate_points(task):
    return 500




