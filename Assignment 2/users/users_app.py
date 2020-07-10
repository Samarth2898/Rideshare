from flask import Flask, request,abort 
import sqlite3
import json
import requests
import csv
import datetime

def isSHA1(s):
    if len(s) != 40:return False
    try:i = int(s, 16)
    except ValueError:return False
    return True

def inc_count():
    try:
        with open( 'counter.txt', 'r' ) as fle:
            counter = int( fle.readline() ) + 1
    except FileNotFoundError:
        counter = 1

    with open( 'counter.txt', 'w' ) as fle:
         fle.write( str(counter) )
    # with counter.get_lock():
        # counter.value += 1

def reset_count():
    try:
        with open( 'counter.txt', 'r' ) as fle:
            counter = 0
    except FileNotFoundError:
        counter = 0

    with open( 'counter.txt', 'w' ) as fle:
         fle.write( str(counter) )
    # with counter.get_lock():
        # counter.value = 0

def return_count():
    # temp = counter.value
    try:
        with open( 'counter.txt', 'r' ) as fle:
            counter = int( fle.readline() ) 
    except FileNotFoundError:
        counter = 0
    return counter

app=Flask(__name__)

# 1
@app.route('/api/v1/users',methods=["PUT"]) #returns 405 if any other method is used
def add_user():
    inc_count()
    req=request.get_json()
    fields = {"username","password"}
    if not(fields.issubset(req)):return {},400
    if isSHA1(req["password"])==False:
        return {},400 # Bad Request
    body = {"table":"users","column":"'username','password'","insert":"'{}','{}'".format(req["username"],req["password"])}
    x = requests.post('http://0.0.0.0:8080/api/v1/db/write', json=body)
    if(x.text=="True"):return {},201
    else:return {},400


# 2
@app.route('/api/v1/users/<user_name>',methods=["DELETE"])
def rem_user(user_name):
    inc_count()
    body1 = {"table":"users","column":"*","where":"username = '{}'".format(user_name)}
    body2 = {"table":"users","delete":"username = '{}'".format(user_name)}
    x = requests.post('http://0.0.0.0:8080/api/v1/db/read', json=body1)
    if(x.text=="[]"):return {},400
    x = requests.post('http://0.0.0.0:8080/api/v1/db/write', json=body2)
    if(x.text=="True"):
        b1 = {"table":"ride","delete":"created_by = '{}'".format(user_name)}
        b2 = {"table":"ride_pool","delete":"username = '{}'".format(user_name)}
        x = requests.post('http://rides:8000/api/v1/db/write', json=b1)
        x = requests.post('http://rides:8000/api/v1/db/write', json=b2)
        return {},200
    else:return {},400
#3
@app.route('/api/v1/users',methods=["GET"])
def list_user():
    inc_count()
    data={"table":"users","column":"username","where":"1=1"}
    r=requests.post("http://0.0.0.0:8080/api/v1/db/read",json=data)
    s1=json.loads(r.text)
    l1=[row[0] for row in s1]
    s2=json.dumps(l1)
    print(s2)
    if(len(l1)>0):return s2,200
    else:return s2,204
#8
@app.route('/api/v1/db/write', methods=["POST"])
def write():
    req = request.get_json()
    if('insert' in req):
        query = "INSERT INTO {}({}) VALUES({})".format(req["table"],req["column"],req["insert"])
    if('delete' in req):
        query = "DELETE FROM {} WHERE {}".format(req['table'],req['delete'])
    with sqlite3.connect("users.db") as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return "True"
    return "False"

#9
@app.route('/api/v1/db/read', methods=["POST"])
def read():
    req = request.get_json()
    where = req["where"]
    columns = req["column"]
    table = req["table"]
    with sqlite3.connect("users.db") as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        c = conn.cursor()
        query = "SELECT {} FROM {} WHERE {}".format(columns,table,where)
        c.execute(query)
        x = c.fetchall()
        return json.dumps(x)

#10
@app.route('/api/v1/db/clear', methods=["POST"])
def clear():
    query = "DELETE FROM users"
    with sqlite3.connect("users.db") as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        x = requests.post('http://rides:8000/api/v1/db/clear')
        return {},200
    return {},400

@app.route('/api/v1/_count', methods=["GET"])
def get_count():
    count = return_count()
    l = list()
    l.append(count)
    x=json.dumps(l)
    return x,200

@app.route('/api/v1/_count', methods=["DELETE"])
def del_count():
    reset_count()
    return {},200

@app.errorhandler(405)
def method_not_allowed(e):
    inc_count()
    return {},405

if __name__== "__main__":
    app.run(host="0.0.0.0",port=8080)
