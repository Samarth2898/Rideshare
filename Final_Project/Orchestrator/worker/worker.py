#Worker
import pika
import json
import requests
import sqlite3
import socket
from subprocess import Popen
from kazoo.client import KazooClient
zk = KazooClient(hosts='zookeeper', read_only=True)
zk.start()
zk.ensure_path("/t")

############ Creating Z-node ############

cont_id = socket.gethostname()
url = 'http://172.17.0.1:5000/getpid/'+cont_id
response = requests.get(url)
proc_id = int(response.text)

data = {
	"cont_id":cont_id,
	"proc_id":proc_id,
	"master":False
}
res_bytes = json.dumps(data).encode('utf-8')

path = zk.create("/t/worker", value=res_bytes, ephemeral=True, sequence=True) #, makepath=True)

############ Sync DB ############

url = 'http://orchestrator:80/get_sql_stmts'
response = requests.get(url)
if(response.status_code!=204):
	l = response.json()
	with sqlite3.connect("rideshare.db") as conn:
		conn.execute("PRAGMA foreign_keys = 1")
		c = conn.cursor()
		for query in l:
			try:
				c.execute(query)
				print("Sync-Write",query)
			except sqlite3.Error as e:
				print("Database error: %s" % e)
			except Exception as e:
				print("Exception in _query: %s" % e)
		conn.commit()

############ Start Subprocess ############

process = Popen(['python', '-u', 'slave.py'],shell=False)
#print("Hello")

############ Watch for change to Master ############
@zk.DataWatch(path)
def watch_node(data, stat, event=None):
	res_dict = json.loads(data.decode("utf-8"))
	print("Watch")
	if(res_dict["master"]):
		print("Master")
		global process
		process.kill()
		print("Killed Slave Process")
		process = Popen(['python', '-u', 'master.py'],shell=False)
		process.communicate()

process.communicate()