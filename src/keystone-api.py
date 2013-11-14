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

def get_endpoints(tokenId):
    headers = {
               'Accept': 'application/json',
               'Content-Type': 'application/json;'
    }
    uri = 'http://160.85.4.11:5000' #replace this with the API end-point of your setup
    path = '/v2.0/tokens/' + tokenId + '/endpoints'
    target = urlparse(uri+path)
    method = 'GET'
    body = ''
    h = http.Http()
    response, content = h.request(target.geturl(),method,body,headers)
    print "Endpoints:\n" + content

def main(argv):
    print "Hello There. This is a simple test application making a test API call to OS"
    headers = {
               'Accept': 'application/json',
               'Content-Type': 'application/json;'
    }
    uri = 'http://160.85.4.11:5000' #replace this with the API end-point of your setup
    path = '/v2.0/tokens'
    target = urlparse(uri+path)
    method = 'POST'
    username, password, tenant = login()
    
    body = '{"auth":{"passwordCredentials":{"username": "' + username + '", "password": "' + password + '"},"tenantId":"' + tenant + '"}}'
    
    h = http.Http()
    response, content = h.request(target.geturl(),method,body,headers)
    
    #print response
    print "The data received is:\n" + content
    header = json.dumps(response)
    json_header = json.loads(header)
    server_response = json_header["status"]
    print "Server response: " + server_response
    
    if server_response not in {'200'}: 
        print "Something went wrong!"
    else:
        data = json.loads(content)
        print "Token was issued at: " + data["access"]["token"]["issued_at"]
        print "Token will expire at: " + data["access"]["token"]["expires"]
        print "Token-id: " + data["access"]["token"]["id"]
        print "Username: " + data["access"]["user"]["username"]
        print "User-id: " + data["access"]["user"]["id"]
        print "Catalog List:"
        for i in range(len(data["access"]["serviceCatalog"])):
            catalog_element =  data["access"]["serviceCatalog"][i]
            print catalog_element["name"] + ", " + catalog_element["type"] + ", endpoint: " + catalog_element["endpoints"][0]["publicURL"]
            
    return True
    
if __name__ == '__main__':
    main(sys.argv[1:])