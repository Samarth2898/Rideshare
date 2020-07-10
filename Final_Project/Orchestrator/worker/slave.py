#Slave
import pika
import json
import requests
import sqlite3

############ Rabbit-MQ Channels ############

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))

sync_channel = connection.channel()
sync_channel.exchange_declare(exchange='sync', exchange_type='fanout')
result = sync_channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
print(queue_name)
sync_channel.queue_bind(exchange='sync', queue=queue_name)

read_channel = connection.channel()
read_channel.queue_declare(queue='readQ', durable=True)

############ Functions ############

def slave_writedb(ch, method, properties, body):
	print("Write DB in slave")
	query=body.decode("utf-8")
	print("Slave-Write",query)
	try:
		with sqlite3.connect("rideshare.db") as conn:
			conn.execute("PRAGMA foreign_keys = 1")
			c = conn.cursor()
			c.execute(query)
			conn.commit()
	except sqlite3.Error as e:
			print("Database error: %s" % e)
	except Exception as e:
			print("Exception in _query: %s" % e)
	ch.basic_ack(delivery_tag=method.delivery_tag)


def slave_readdb(ch, method, props, body):
	query = body.decode("utf-8")
	print("Read DB in slave")
	print("Slave-Read",query)
	try:
		with sqlite3.connect("rideshare.db") as conn:
			c = conn.cursor()
			c.execute(query)
			x = c.fetchall()
	except sqlite3.Error as e:
		x = []
		print("Database error: %s" % e)
	except Exception as e:
		x = []
		print("Exception in _query: %s" % e)
	response = json.dumps(x)
	#print(response)
	#print(props.correlation_id)
	ch.basic_publish(exchange='',
					routing_key=props.reply_to,
					properties=pika.BasicProperties(correlation_id = props.correlation_id),
					body=response)
	
	ch.basic_ack(delivery_tag=method.delivery_tag)

############ Consume ############

read_channel.basic_qos(prefetch_count=1)
sync_tag=sync_channel.basic_consume(queue=queue_name, on_message_callback=slave_writedb)
read_tag=read_channel.basic_consume(queue='readQ', on_message_callback=slave_readdb)

sync_channel.start_consuming()
read_channel.start_consuming()