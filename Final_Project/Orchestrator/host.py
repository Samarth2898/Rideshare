from flask import Flask,render_template,jsonify,request,abort
import requests
import sqlite3
import re
import csv
import json
import subprocess
from datetime import datetime
import docker
client = docker.from_env()

app=Flask(__name__)
@app.route('/getpid/<cont_id>',methods=["GET"])
def getpid(cont_id):
	cont = client.containers.get(cont_id)
	x = cont.top()
	#print("Top -")
	#print(x)
	pid = x["Processes"][0][2]
	print("Mapping - "+cont_id+" : "+pid)
	return pid,200

@app.route('/new_worker',methods=["POST"])
def new_worker():
	cont = client.containers.run(image="worker", network="orchestrator_default", detach=True)#project_default
	return cont.id,200

@app.route('/kill_worker/<cont_id>',methods=["POST"])
def kill_worker(cont_id):
	cont = client.containers.get(cont_id)
	cont.kill()
	client.containers.prune()
	return cont.id,200

if __name__ == '__main__':	
	app.debug=True
	open('commands.txt', 'w').close()
	app.run(host="0.0.0.0",port=5000)