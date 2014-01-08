# -*- coding: ascii -*-
#--------------------------------------------------------------
#Created on Nov 21, 2013
#
#@author: Piyush Harsh
#@contact: piyush.harsh@zhaw.ch
#@organization: ICCLab, Zurich University of Applied Sciences
#@summary: Module to interact with OS-ceilometer service
#@var username, tenant-id, password
#@requires: python 2.7
#--------------------------------------------------------------

import httplib2 as http
import sys, re
import json

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

def get_meter_list(token, api_endpoint):
    meter_list = [None]
    headers = {
               'Accept': 'application/json',
               'Content-Type': 'application/json;',
               'X-Auth-Token': token
    }
    path = "/v2/meters"
    target = urlparse(api_endpoint+path)
    method = 'GET'
    body = ''
    h = http.Http()
    response, content = h.request(target.geturl(),method,body,headers)
    #converting the header of the response to json object
    header = json.dumps(response)
    json_header = json.loads(header)
    
    server_response = json_header["status"]
    if server_response not in {'200'}:
        print "Inside get_server_list(): Something went wrong!"
        return False, meter_list
    else:
        data = json.loads(content)
        #print "Number of meters found: %d" % len(data) 
        meter_list = [None]*len(data)
        for i in range(len(data)):
            meter_list[i] = {}
            meter_list[i]["user-id"] = data[i]["user_id"]
            meter_list[i]["meter-name"] = data[i]["name"]
            meter_list[i]["resource-id"] = data[i]["resource_id"]
            meter_list[i]["meter-source"] = data[i]["source"]
            meter_list[i]["meter-id"] = data[i]["meter_id"]
            meter_list[i]["tenant-id"] = data[i]["project_id"]
            meter_list[i]["meter-type"] = data[i]["type"]
            meter_list[i]["meter-unit"] = data[i]["unit"]
        #print data
    return True, meter_list

def period():
    from_date = raw_input("Month from yyyy-mm-dd: ")
    from_time= raw_input("Time from hh:mm:ss ")
    to_date = raw_input("Month to yyyy-mm-dd: ")
    to_time= raw_input("Time to hh:mm:ss ")
    return from_date,to_date,from_time,to_time

def meter_statistics(meter_id,api_endpoint,token):
    meter_stat = [None]
    headers = {
               #'Accept': 'application/json',
               'Content-Type': 'application/json;',
               'X-Auth-Token': token
               
    }
    from_date,to_date,from_time,to_time=period()   
    path = "/v2/meters/"+meter_id+"/statistics"
    target = urlparse(api_endpoint+path)
    method = 'GET'
    body = '{"q":[{"field": "timestamp","op": "ge","value": "'+from_date+'T'+from_time+'"},{"field": "timestamp","op": "lt","value": "'+to_date+'T'+to_time+'"}]}'
    
    #body='{"q": [{"field": "timestamp","op": "ge","value": "2013-12-28T00:00:00"},{"field": "timestamp","op": "lt","value": "2014-01-05T00:00:00"}]}'
    h = http.Http()
    response, content = h.request(target.geturl(),method,body,headers)
    header = json.dumps(response)
    json_header = json.loads(header)
    
    server_response = json_header["status"]
    if server_response not in {'200'}:
        print "Inside meter_statistics(): Something went wrong!"
        return False, meter_stat
    else:
        data = json.loads(content)
        meter_stat = [None]*len(data)
        for i in range(len(data)):
            meter_stat[i]={}
            meter_stat[i]["average"] = data[i]["avg"]
            meter_stat[i]["count"] = data[i]["count"]
            meter_stat[i]["duration"] = data[i]["duration"]
            meter_stat[i]["duration-end"] = data[i]["duration_end"]
            meter_stat[i]["duration-start"] = data[i]["duration_start"]
            meter_stat[i]["max"] = data[i]["max"]
            meter_stat[i]["min"] = data[i]["min"]
            meter_stat[i]["period"] = data[i]["period"]
            meter_stat[i]["period-end"] = data[i]["period_end"]
            meter_stat[i]["period-start"] = data[i]["period_start"]
            meter_stat[i]["sum"] = data[i]["sum"]
            meter_stat[i]["unit"] = data[i]["unit"]
            meter_stat[i]["group-by"] = data[i]["groupby"]
        return True, meter_stat