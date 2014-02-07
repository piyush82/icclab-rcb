# -*- coding: ascii -*-
#--------------------------------------------------------------
#Created on Nov 11, 2013
#
#@author: Piyush Harsh
#@contact: piyush.harsh@zhaw.ch
#@organization: ICCLab, Zurich University of Applied Sciences
#@summary: Module to interact with OS-keystone service
#@var username, tenant-id, password
#@requires: python 2.7
#--------------------------------------------------------------

import httplib2 as http
import sys, re
import json
import getpass

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def login():
    user = raw_input("Username [%s]: " % getpass.getuser())
    tenant = raw_input("Tenant Id: ")
    if not user:
        user = getpass.getuser()
    pprompt = lambda: (getpass.getpass())
    p1 = pprompt()
    return user, p1, tenant

def login_v3():
    user = raw_input("Username [%s]: " % getpass.getuser())
    domain = raw_input("Domain name: ")
    project = raw_input("Project name: ")
    if not user:
        user = getpass.getuser()
    pprompt = lambda: (getpass.getpass())
    p1 = pprompt()
    return user, p1, domain,project

def get_endpoints(tokenId, uri):
    headers = {
               'Accept': 'application/json',
               'Content-Type': 'application/json;'
    }
    # uri = 'http://160.85.4.11:5000' #replace this with the API end-point of your setup
    uri="http://160.85.4.10:5000"
    #uri = 'http://160.85.4.64:5000' #internal test-setup, replace it with your own value
    path = '/v2.0/tokens/' + tokenId + '/endpoints'
    target = urlparse(uri+path)
    method = 'GET'
    body = ''
    h = http.Http()
    response, content = h.request(target.geturl(),method,body,headers)
    print "Endpoints:\n" + content

#TODO: write the get token method with API v3    
def get_token_v3(uri):
    auth_data = {}
    headers = {
               'Accept': 'application/json',
               'Content-Type': 'application/json;'
    }
    path = '/v3/auth/tokens'
    target = urlparse(uri+path)
    method = 'POST'
    username, password, domain,project = login_v3()
    #defining the request body here
    body = '{"auth": {"identity": {"methods": ["password"],"password": {"user": {"domain":{"name":"' + domain + '"},"name": "' + username + '","password": "' + password + '"}}},"scope": {"project": {"domain": {"name": "' + domain + '"},"name": "' + project + '"}}}}'
    
    h = http.Http()
    response, content = h.request(target.geturl(),method,body,headers)
    #converting the header of the response to json object
    header = json.dumps(response)
    json_header = json.loads(header)
    
    server_response = json_header["status"]
    auth_data["server-response"] = server_response
    if server_response not in {'201'}:
        print "Inside get_token_v3(): Something went wrong!"
        return False, auth_data
    else:
        data = json.loads(content)
        auth_data["token-issued-at"] = data["token"]["issued_at"]
        auth_data["token-expires-at"] = data["token"]["expires_at"]
        auth_data["token-id"] = json_header["x-subject-token"]
        auth_data["user-name"] = data["token"]["user"]["name"]
        auth_data["user-id"] = data["token"]["user"]["id"]
        for i in range(len(data["token"]["catalog"])):
            catalog_element =  data["token"]["catalog"][i]
            #print catalog_element["name"] + ", " + catalog_element["type"] + ", endpoint: " + catalog_element["endpoints"][0]["publicURL"]
            auth_data[catalog_element["type"]] = catalog_element["endpoints"][0]["url"]
    return True, auth_data 
    
    
def get_token_v2(uri):
    auth_data = {}     #an empty dictionary
    headers = {
               'Accept': 'application/json',
               'Content-Type': 'application/json;'
    }
    
    path = '/v2.0/tokens'
    target = urlparse(uri+path)
    method = 'POST'
    username, password, tenant = login()
    #defining the request body here
    body = '{"auth":{"passwordCredentials":{"username": "' + username + '", "password": "' + password + '"},"tenantId":"' + tenant + '"}}'
    
    h = http.Http()
    response, content = h.request(target.geturl(),method,body,headers)
    #converting the header of the response to json object
    header = json.dumps(response)
    json_header = json.loads(header)
    
    server_response = json_header["status"]
    auth_data["server-response"] = server_response
    if server_response not in {'200'}:
        print "Inside get_token_v2(): Something went wrong!"
        return False, auth_data
    else:
        data = json.loads(content)
        auth_data["token-issued-at"] = data["access"]["token"]["issued_at"]
        auth_data["token-expires-at"] = data["access"]["token"]["expires"]
        auth_data["token-id"] = data["access"]["token"]["id"]
        auth_data["user-name"] = data["access"]["user"]["username"]
        auth_data["user-id"] = data["access"]["user"]["id"]
        for i in range(len(data["access"]["serviceCatalog"])):
            catalog_element =  data["access"]["serviceCatalog"][i]
            #print catalog_element["name"] + ", " + catalog_element["type"] + ", endpoint: " + catalog_element["endpoints"][0]["publicURL"]
            auth_data[catalog_element["name"]] = catalog_element["endpoints"][0]["publicURL"]
    return True, auth_data 
