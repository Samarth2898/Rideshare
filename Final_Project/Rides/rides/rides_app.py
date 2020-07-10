from flask import Flask, request,abort 
import sqlite3
import json
import requests
import csv
import datetime

def inc_count():
    try:
        with open( 'counter.txt', 'r' ) as fle:
            counter = int( fle.readline() ) + 1
    except FileNotFoundError:
        counter = 0

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

area = {}
with open('AreaNameEnum.csv', mode='r') as infile:
    reader = csv.reader(infile)
    area = {rows[0]:rows[1] for rows in reader}

#rides
def getDate(s):
    try:
        x = datetime.datetime.strptime(s,"%d-%m-%Y:%S-%M-%H")
        return x
    except ValueError:
        return False

app=Flask(__name__)

#3
@app.route('/api/v1/rides', methods=["POST"])
def create_new_ride():
    inc_count()
    req=request.get_json()
    fields = {"created_by","timestamp","source","destination"}
    if not(fields.issubset(req)):return {},400
    #headers = {"Origin": "http://54.164.213.19"}
    #x = requests.get('http://cc-ass-3-678167101.us-east-1.elb.amazonaws.com/api/v1/users', headers=headers)
    # Check if username exists
    x = requests.get('http://52.3.109.219/api/v1/users')
    if x.status_code==204:return {},400
    l1=json.loads(x.text)
    if req["created_by"] not in l1:return {},400

    # Check if areas are correct
    if req["source"] not in area or req["destination"] not in area: return {},400
    # Check if timestamp is correct
    d = getDate(req["timestamp"])
    #if(d==False or d<datetime.datetime.now()): return {},400
    if(d==False): return {},400

    body = {"table":"ride","column":"created_by,timestamp,source,destination","insert":"'{}','{}',{},{}".format(req["created_by"],req["timestamp"],req["source"],req["destination"])}
    x = requests.post('http://54.90.15.252/api/v1/db/write', json=body)
    return {},201

#4
@app.route('/api/v1/rides', methods=["GET"])
def list_all_rides():
    inc_count()
    if ('source' not in request.args) or ('destination' not in request.args):return {},400
    source=request.args.get('source')
    destination=request.args.get('destination')
    if source not in area or destination not in area:return {},400
    data={"table":"ride","column":"ride_id,created_by,timestamp","where":"source={} AND destination={}".format(source,destination)}
    r=requests.post("http://54.90.15.252/api/v1/db/read",json=data)
    rl = json.loads(r.text)
    body = list()
    if(len(rl)==0):return {},204
    flag = True
    for row in rl:
        if(getDate(row[2])>datetime.datetime.now()):
            flag = False
            d = {}
            d["rideId"]=row[0]
            d["username"]=row[1]
            d["timestamp"]=row[2]
            body.append(d)
    if flag:return {},204
    return json.dumps(body),200

#5
@app.route('/api/v1/rides/<ride_id>',methods=["GET"])
def list_details(ride_id):
    inc_count()
    data={"table":"ride","column":"created_by,timestamp,source,destination","where":"ride_id={}".format(ride_id)}
    r=requests.post("http://54.90.15.252/api/v1/db/read",json=data)
    s=json.loads(r.text)
    #If the ride_id does not exist
    if(len(s)==0):return {},204
    s=s[0]
    body ={}
    body["rideId"]=ride_id
    body["created_by"]=s[0]
    data={"table":"ride_pool","column":"username","where":"ride_id={}".format(ride_id)}
    r=requests.post("http://54.90.15.252/api/v1/db/read",json=data)
    s1=json.loads(r.text)
    l1=[row[0] for row in s1]
    body["users"] = l1
    body["timestamp"]=s[1]
    body["source"]=s[2]
    body["destination"]=s[3]
    return json.dumps(body),200

#6
@app.route('/api/v1/rides/<ride_id>',methods=['POST'])
def join_ride(ride_id):
    inc_count()
    req=request.get_json()
    fields = {"username"}
    if not(fields.issubset(req)):return {},400
    #headers = {"Origin": "http://54.164.213.19"}
    #x = requests.get('http://cc-ass-3-678167101.us-east-1.elb.amazonaws.com/api/v1/users', headers=headers)
    # Check if username exists
    x = requests.get('http://52.3.109.219/api/v1/users')
    if x.status_code==204:return {},400
    print(x.status_code,"\n",x.text)
    l1=json.loads(x.text)
    if req["username"] not in l1:return {},400

    # Check if ride_id exists
    data={"table":"ride","column":"*","where":"ride_id={}".format(ride_id)}
    r=requests.post("http://54.90.15.252/api/v1/db/read",json=data)
    if(len(json.loads(r.text))==0):return {},400

    # Check if ride_pool already exists
    data={"table":"ride_pool","column":"*","where":"ride_id={} AND username='{}'".format(ride_id,req["username"])}
    r=requests.post("http://54.90.15.252/api/v1/db/read",json=data)
    if(len(json.loads(r.text))!=0):return {},204

    data={"table":"ride_pool","insert":"'{}','{}'".format(req["username"],ride_id),"column":"username,ride_id"}
    r=requests.post("http://54.90.15.252/api/v1/db/write",json=data)
    return {},201

#7
@app.route('/api/v1/rides/<ride_id>',methods=["DELETE"])
def rem_ride(ride_id):
    inc_count()
    body1 = {"table":"ride","column":"*","where":"ride_id = {}".format(ride_id)}
    body2 = {"table":"ride","delete":"ride_id = {}".format(ride_id)}
    x = requests.post('http://54.90.15.252/api/v1/db/read', json=body1)
    if len(json.loads(x.text))==0:return {},400
    x = requests.post('http://54.90.15.252/api/v1/db/write', json=body2)
    return {},200

"""
#8
@app.route('/api/v1/db/write', methods=["POST"])
def write():
    req = request.get_json()
    if('insert' in req):
        query = "INSERT INTO {}({}) VALUES({})".format(req["table"],req["column"],req["insert"])
    if('delete' in req):
        query = "DELETE FROM {} WHERE {}".format(req['table'],req['delete'])
    with sqlite3.connect("rides.db") as conn:
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
    with sqlite3.connect("rides.db") as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        c = conn.cursor()
        query = "SELECT {} FROM {} WHERE {}".format(columns,table,where)
        c.execute(query)
        x = c.fetchall()
        return json.dumps(x)

#10
@app.route('/api/v1/db/clear', methods=["POST"])
def clear():
    query1 = "DELETE FROM ride_pool"
    query2 = "DELETE FROM ride"
    query3 = "UPDATE SQLITE_SEQUENCE SET SEQ=1 WHERE NAME='ride'"
    with sqlite3.connect("rides.db") as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        c = conn.cursor()
        c.execute(query1)
        c.execute(query2)
        c.execute(query3)
        conn.commit()
        return {},200
    return {},400
"""

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

@app.route('/api/v1/rides/count', methods=["GET"])
def ride_count():
    inc_count()
    body = {"table":"ride","column":"ride_id","where":"1 = 1"}
    x = requests.post('http://54.90.15.252/api/v1/db/read', json=body)
    l1=json.loads(x.text)
    n = len(l1)

    l = list()
    l.append(n)
    x=json.dumps(l)
    return x,200

@app.errorhandler(405)
def method_not_allowed(e):
    inc_count()
    return {},405

if __name__== "__main__":
    app.run(host="0.0.0.0",port=8000)