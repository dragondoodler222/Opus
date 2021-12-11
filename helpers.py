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
    return db.execute("SELECT 1 FROM users WHERE id = :id", id=session["user_id"])[0]