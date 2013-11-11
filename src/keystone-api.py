#--------------------------------------------------------------
#Created on Nov 11, 2013
#
#@author: Piyush Harsh
#@contact: piyush.harsh@zhaw.ch
#@organization: ICCLab, Zurich University of Applied Sciences
#@summary: Module to interact with OS-keystone service
#--------------------------------------------------------------

import httplib2 as http
import sys
import json
import getpass

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
    
def login():
    user = raw_input("Username [%s]: " % getpass.getuser())
    if not user:
        user = getpass.getuser()
    pprompt = lambda: (getpass.getpass())
    p1 = pprompt()
    return user, p1

def main(argv):
    print "Hello There. This is a simple test application making a test API call to OS"
    headers = {
               'Accept': 'application/json',
               'Content-Type': 'application/json; charset=UTF-8'
    }
    uri = 'http://160.85.4.11:5000' #replace this with the API end-point of your setup
    path = '/v2.0/tokens'
    target = urlparse(uri+path)
    method = 'POST'
    username, password = login()
    
    body = '{"auth":{"passwordCredentials":{"username": "' + username + '", "password": "' + password + '"}}}'
    
    h = http.Http()
    response, content = h.request(target.geturl(),method,body,headers)
    
    #print response
    #print "The data received is:\n" + content
    header = json.dumps(response)
    json_header = json.loads(header)
    server_response = json_header["status"].encode('ascii','ignore')
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
    return True
    
if __name__ == '__main__':
    main(sys.argv[1:])