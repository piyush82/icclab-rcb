# -*- coding: ascii -*-
#--------------------------------------------------------------
#Created on Nov 11, 2013
#
#@author: Piyush Harsh
#@contact: piyush.harsh@zhaw.ch
#@organization: ICCLab, Zurich University of Applied Sciences
#@summary: Module to interact with OS-compute service
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

#a simple API test case with nova
def get_server_list(token, api_endpoint):
    headers = {
               'Accept': 'application/json',
               'Content-Type': 'application/json;',
               'X-Auth-Token': token
    }
    path = "/servers"
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
        return False, server_list
    else:
        data = json.loads(content)
        servers = data["servers"]
        server_list = [None] * len(servers)   #create an array to hold parsed data
        for i in range(len(servers)):
            server_list[i] = {}
            server_list[i]["id"] = servers[i]["id"]
            server_list[i]["name"] = servers[i]["name"]
            server_list[i]["url"] = servers[i]["links"][0]["href"]
    return True, server_list