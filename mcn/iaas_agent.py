#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2014 Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

'''
Created on May 27, 2014
 
@author: Piyush Harsh (piyush.harsh@zhaw.ch)
 
This is RCB IaaS Agent to send metrics for IaaS providers

This module requires python-ceilometerclient to be installed.

Instructions: sudo apt-get install python-pip git-core
              sudo pip install python-ceilometerclient

'''

import pika
import unicodedata
from random import randint
import time, threading
from datetime import date, timedelta
from ceilometer_client import get_statistics, filter_statistics, filter_statistics_by_time

def send_msg(exch, key, msg):
    '''
        This is the rabbitmq sender module.
        Arguments: exchange name, routing key, and message payload.
    '''
    connection = None
    try:
        credentials = pika.PlainCredentials('test', 'icclab')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='160.85.4.25', port=5672, virtual_host='/', credentials=credentials))
        channel = connection.channel()
        channel.basic_publish(exchange=exch, routing_key=key, body=msg)
        print " [x] Sent: %s" % msg
    except KeyboardInterrupt:
        print "  [CTRL+C] Interrupt received. Will terminate the sending process now."
    except Exception:
        print "  [err] Caught exception in the code"
        raise
    finally:
        if connection != None:
            connection.close()

def iaas_periodic_method(exchange, key, periodicity, os_creds, meter_list):
    '''This is a simple periodic message sender method.
        Arguments: exchange name, routing-key, periodicity in seconds, openstack credentials, and meter list
    '''
    try:
        def periodic_send():
            #here we will create the json message to be sent to the rabbitmq exchange
            udr = {}
            users = {}
            for meter in meter_list:
                stats = get_statistics(os_creds, meter, None, '86400', ["resource_id", "user_id"])
                for user_id in stats.keys():
                    if users.get(user_id) == None:
                        users[user_id] = {}
                        (users[user_id])['date'] = (date.today()-timedelta(days=1)).strftime("%Y-%m-%d") #setting the date to yesterday
                    (users[user_id])[meter] = {}
                    for resource_id in (stats[user_id]).keys():
                        candidates = filter_statistics(stats, user_id, resource_id)
                        filteredStats = filter_statistics_by_time(candidates, (users[user_id])['date'])
                        if len(filteredStats) > 0:
                            if ((users[user_id])[meter]).get(resource_id) == None:
                                ((users[user_id])[meter])[resource_id] = {}
                                (((users[user_id])[meter])[resource_id])['usage'] = 0.0
                                (((users[user_id])[meter])[resource_id])['meter_unit'] = 'na'
                            for entry in filteredStats:
                                (((users[user_id])[meter])[resource_id])['meter_unit'] = entry['unit']
                                (((users[user_id])[meter])[resource_id])['usage'] = ((((users[user_id])[meter])[resource_id])['usage'] + entry['max'] - entry['min'])
            #print users
            #now creating the json message to be sent out
            for user in users.keys():
                msg = '{"user-id": "%s",' % (user)
                msg = msg + '"date-from": "%s",' % (users[user])['date']
                msg = msg + '"usage": [' #now here insert the array
                meter_size = len((users[user]).keys())
                meter_index = 1
                for meter in (users[user]).keys():
                    if meter != 'date':
                        msg = msg + '{"meter-name": "%s", "usage-data": [' % (meter)
                        resource_size = len(((users[user])[meter]).keys())
                        resource_index = 1
                        for resource in ((users[user])[meter]).keys():
                            if resource_index < resource_size:
                                msg = msg + '{"resource-id": "%s", "usage": "%s", "unit": "%s"}, ' % (resource, (((users[user])[meter])[resource])['usage'], (((users[user])[meter])[resource])['meter_unit'])
                            else:
                                msg = msg + '{"resource-id": "%s", "usage": "%s", "unit": "%s"}' % (resource, (((users[user])[meter])[resource])['usage'], (((users[user])[meter])[resource])['meter_unit'])
                            resource_index = resource_index + 1
                        msg = msg + ']'
                        if meter_index < meter_size:
                            msg = msg + '},'
                        else:
                            msg = msg + '}'
                    meter_index = meter_index + 1
                msg = msg + ']}'
                send_msg(exchange, key, msg)
            threading.Timer(periodicity, periodic_send).start()
        periodic_send()
    except:
        print "  [err] Caught exception in the periodic call."
        raise

if __name__ == '__main__':
    #getting the credentials
    keystone = {}
    keystone['os_username']='your-user'
    keystone['os_password']='your-password'
    keystone['os_auth_url']='http://160.85.4.224:5000/v2.0'
    keystone['os_tenant_name']='MCN-RCBaaS'
    #the basic idea is to get the list of users belonging to a particular tenant and then send UDRs for
    #each of them periodically. Meters used are: cpu, disk.read.bytes, disk.write.bytes, network.outgoing.bytes
    meters = ['cpu', 'disk.read.bytes', 'disk.write.bytes', 'network.outgoing.bytes']
    exchange_name = 'mcn-rcb-demo'
    routing_key = 'mcn-iaas-key-w8x5nxp6v5W5qmk'
    iaas_periodic_method(exchange_name, routing_key, 86400, keystone, meters) # this thread runs every day
    
