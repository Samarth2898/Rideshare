from flask import Flask,render_template,jsonify,request,abort
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import sqlite3
import json
import pika
import uuid
from kazoo.client import KazooClient

zk = KazooClient(hosts='zookeeper', read_only=True)
zk.start()
zk.ensure_path("/t")

@zk.ChildrenWatch("/t")
def func(ch):
	print(ch)
	flag = True
	if len(ch)==0:
		print("No Worker")
		return
	min_name = ""
	min_dict = False
	min_pid = float('inf')
	for c in ch:
		data,stat=zk.get("/t/"+c)
		res_dict = json.loads(data.decode("utf-8"))
		if res_dict["master"]:
			print("Master Exists")
			flag = False
			break
		if res_dict["proc_id"] < min_pid:
			min_pid = res_dict["proc_id"]
			min_name = c
			min_dict = res_dict
	if len(ch)<2:
		requests.post("http://172.17.0.1:5000/new_worker")
	if flag:
		if min_dict:
			min_dict["master"]=True
			res_bytes = json.dumps(min_dict).encode('utf-8')
			zk.set("/t/"+min_name,res_bytes)
			print("/t/"+min_name+"-"+str(min_pid)+" is the new master")

first = True

app=Flask(__name__)

class ReadRpcClient(object):
	def __init__(self):
		self.connection = pika.BlockingConnection(
			pika.ConnectionParameters(host='rabbitmq'))
		self.channel = self.connection.channel()

		result = self.channel.queue_declare(queue='responseQ', durable=True)
		self.callback_queue = result.method.queue

		self.channel.basic_consume(
			queue=self.callback_queue,
			on_message_callback=self.on_response,
			auto_ack=True)

	def on_response(self, ch, method, props, body):
		print("RPC Response")
		print(body)
		if self.correlation_id == props.correlation_id:
			self.response = body
			ch.basic_ack(delivery_tag=method.delivery_tag)

	def call(self, data):
		print("RPC Call")
		self.response = None
		self.correlation_id = str(uuid.uuid4())
		self.channel.queue_declare(queue='readQ',durable=True)
		self.channel.basic_publish(
			exchange='',
			routing_key='readQ',
			properties=pika.BasicProperties(
				reply_to=self.callback_queue,
				correlation_id=self.correlation_id,
			),
			body=data)
		while self.response is None:
			self.connection.process_data_events()
		return json.loads(self.response)

def inc_count():
    try:
        with open( 'counter.txt', 'r' ) as file:
            counter = int( file.readline() ) + 1
    except FileNotFoundError:
        counter = 1
    with open( 'counter.txt', 'w' ) as file:
         file.write( str(counter) )

def reset_count():
    with open( 'counter.txt', 'w' ) as file:
         file.write( "0" )

def return_count():
    try:
        with open( 'counter.txt', 'r' ) as file:
            counter = int( file.readline() ) 
    except FileNotFoundError:
        counter = 0
    return counter

def save_sql_stmt(command):
	with open('sql_stmts.txt','a') as file:
		c = command+'\n'
		file.write(c)

def check_func():
	count = return_count()
	print("Request Count -",count)
	reset_count()
	print("Check Func")
	l = list()
	ch = zk.get_children("/t")
	for c in ch:
		data,stat=zk.get("/t/"+c)
		res_dict = json.loads(data.decode("utf-8"))
		if not res_dict["master"]:
			res_dict["name"]=c
			l.append(res_dict)

	cur_slave = len(l)
	total_slave = int((count-1)/20)+1
	dif_slave = total_slave - cur_slave
	if(dif_slave>0):
		for i in range(dif_slave):
			requests.post("http://172.17.0.1:5000/new_worker")
	
	elif(dif_slave<0):
		dif_slave = -dif_slave
		l = sorted(l, key = lambda i: i['proc_id'], reverse=True) 
		l = l[:dif_slave]
		for i in l:
			print("Kill -",i["cont_id"])
			zk.delete("/t/"+i["name"])
			requests.post("http://172.17.0.1:5000/kill_worker/{}".format(i["cont_id"]))

@app.route('/')
def hello_world():
	return "Orchestrator API"

@app.route('/get_sql_stmts',methods=["GET"])
def get_cmd():
	f = open("sql_stmts.txt", "r")
	cmd = f.readlines()
	cmd = [line.strip('\n') for line in cmd]
	if(len(cmd)==0):
		return {}, 204
	return jsonify(cmd), 200

#8
@app.route('/api/v1/db/write', methods=["POST"])
def write():
	req = request.get_json()
	if('insert' in req):
		query = "INSERT INTO {}({}) VALUES({})".format(req["table"],req["column"],req["insert"])
	if('delete' in req):
		query = "DELETE FROM {} WHERE {}".format(req['table'],req['delete'])
	save_sql_stmt(query)
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
	channel = connection.channel()
	channel.queue_declare(queue='writeQ', durable=True)
	channel.basic_publish(exchange='',routing_key='writeQ',body=query,properties=pika.BasicProperties(delivery_mode=2))
	connection.close()
	return {},200

#9
@app.route('/api/v1/db/read', methods=["POST"])
def read():
	inc_count()
	req = request.get_json()
	global first
	if first:
		print("Scheduler Started")
		scheduler.start()
		first = False
	where = req["where"]
	columns = req["column"]
	table = req["table"]
	query = "SELECT {} FROM {} WHERE {}".format(columns,table,where)
	read_rpc = ReadRpcClient()
	response = read_rpc.call(query)
	return jsonify(response),200

#10
@app.route('/api/v1/db/clear', methods=["POST"])
def clear():
	inc_count()
	query1 = "DELETE FROM ride_pool"
	query2 = "DELETE FROM ride"
	query3 = "DELETE FROM users"
	#save_sql_stmt(query1)
	#save_sql_stmt(query2)
	#save_sql_stmt(query3)
	open('sql_stmts.txt', 'w').close()
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
	channel = connection.channel()
	channel.queue_declare(queue='writeQ', durable=True)
	channel.basic_publish(exchange='',routing_key='writeQ',body=query1,properties=pika.BasicProperties(delivery_mode=2))
	channel.basic_publish(exchange='',routing_key='writeQ',body=query2,properties=pika.BasicProperties(delivery_mode=2))
	channel.basic_publish(exchange='',routing_key='writeQ',body=query3,properties=pika.BasicProperties(delivery_mode=2))
	connection.close()
	return {},200


@app.route('/api/v1/worker/list',methods=["GET"])
def list_worker():
	l = list()
	ch = zk.get_children("/t")
	for c in ch:
		data,stat=zk.get("/t/"+c)
		res_dict = json.loads(data.decode("utf-8"))
		l.append(res_dict["proc_id"])
	return json.dumps(sorted(l)), 200

@app.route('/api/v1/crash/slave',methods=["POST"])
def crash_slave():
	max_dict = False
	max_name = ""
	max_pid = 0
	l=list()
	ch = zk.get_children("/t")
	if ch:
		for c in ch:
			data,stat=zk.get("/t/"+c)
			res_dict = json.loads(data.decode("utf-8"))
			if res_dict["proc_id"] > max_pid and not res_dict["master"]:
				max_pid = res_dict["proc_id"]
				max_dict = res_dict
				max_name = c
		if max_dict:
			zk.delete("/t/"+max_name)
			requests.post("http://172.17.0.1:5000/kill_worker/{}".format(max_dict["cont_id"]))
			#if len(ch)<=2:
			#	requests.post("http://172.17.0.1:pro5000/new_worker")
			l.append(str(max_dict["proc_id"]))
	return json.dumps(l), 200

@app.route('/api/v1/crash/master',methods=["POST"])
def crash_master():
	min_dict = False
	min_name = ""
	l=list()
	ch = zk.get_children("/t")
	if ch:
		for c in ch:
			data,stat=zk.get("/t/"+c)
			res_dict = json.loads(data.decode("utf-8"))
			if res_dict["master"]:
				min_dict = res_dict
				min_name = c
				break
		if min_dict:
			zk.delete("/t/"+min_name)
			requests.post("http://172.17.0.1:5000/kill_worker/{}".format(min_dict["cont_id"]))
			#if len(ch)<=2:
			#	requests.post("http://172.17.0.1:5000/new_worker")
			l.append(str(min_dict["proc_id"]))
	return json.dumps(l), 200

if __name__ == '__main__':	
	app.debug=True
	open('sql_stmts.txt', 'w').close()
	requests.post("http://172.17.0.1:5000/new_worker") #Master
	#requests.post("http://172.17.0.1:5000/new_worker") #Slave No need Children watch will only create new worker if count <2
	scheduler = BackgroundScheduler()
	job = scheduler.add_job(check_func, 'interval', minutes=2)
	app.run(host="0.0.0.0",port=80,use_reloader=False)