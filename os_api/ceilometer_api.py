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