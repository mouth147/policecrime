import os
import sqlite3
from flask import g
from mainapp import app

DATABASE = os.path.abspath(os.path.join(os.getcwd(), './db/project.db'))

def get_db():
    #db = getattr(g, '_database', None)
    #if db is None:
    db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one = False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
