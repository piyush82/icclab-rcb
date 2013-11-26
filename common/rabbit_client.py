# -*- coding: ascii -*-
#--------------------------------------------------------------
#Created on Nov 21, 2013
#
#@author: Piyush Harsh
#@contact: piyush.harsh@zhaw.ch
#@organization: ICCLab, Zurich University of Applied Sciences
#@summary: Module to interact with rabbimq messaging service
# Note: some lines of code picked from rabbitmq tutorial online
#@var 
#@requires: python 2.7, pika
#--------------------------------------------------------------

import pika
import sys

#This function just consumes messages from the queue
#You can define your own callback function and what to do with the messages
def callback(ch, method, properties, body):
    print "Received %r" % body
    ch.basic_ack(delivery_tag = method.delivery_tag)

def send_message(host, q_name, message, durability):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    #we create a new channel, in RCBaaS, we can create a new channel for each tennant if needed
    channel.queue_declare(queue=q_name, durable=durability)
    channel.basic_publish(exchange='', routing_key=q_name, body=message, 
                          properties=pika.BasicProperties(
                                                          delivery_mode = 2, # make message persistent
                                                          ))
    connection.close()  #just to flush all the messages out
    return True

def recv_message(host, q_name, durability, no_ack_strategy, callback_method):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    channel.queue_declare(queue=q_name, durable=durability)
    print 'Waiting for messages on queue: %s To exit - press Ctrl+C' % q_name
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback_method, queue=q_name, no_ack=no_ack_strategy)  #always good to acknowledge the received messages
    channel.start_consuming()   #this is a blocking loop
    return True

def main(argv):
    send_message('localhost', 'test-queue', 'Hello World!', True)
    recv_message('localhost', 'test-queue', True, False, callback)
    return True

if __name__ == "__main__":
    main(sys.argv[1:])