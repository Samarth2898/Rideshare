#Master
import pika
import json
import requests
import sqlite3

############ Rabbit-MQ Channels ############

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))

write_channel = connection.channel()
write_channel.queue_declare(queue='writeQ', durable=True)

sync_channel = connection.channel()
sync_channel.exchange_declare(exchange='sync', exchange_type='fanout')

############ Functions ############

def master_writedb(ch, method, properties, body):
	query=body.decode("utf-8")
	print("Master-Write",query)
	try:
		with sqlite3.connect("rideshare.db") as conn:
			conn.execute("PRAGMA foreign_keys = 1")
			c = conn.cursor()
			c.execute(query)
			conn.commit()
			sync_channel.basic_publish(
				exchange='sync',
				routing_key='',
				body=query,
				properties=pika.BasicProperties(
					delivery_mode=2,  # make message persistent
				))
	except sqlite3.Error as e:
			print("Database error: %s" % e)
	except Exception as e:
			print("Exception in _query: %s" % e)
	ch.basic_ack(delivery_tag=method.delivery_tag)

############ Consume ############

write_channel.basic_qos(prefetch_count=1)
write_channel.basic_consume(queue='writeQ', on_message_callback=master_writedb)
write_channel.start_consuming()