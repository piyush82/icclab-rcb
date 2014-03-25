'''
Created on Jan 3, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@zhaw.ch
@organization: ICCLab, Zurich University of Applied Sciences
@summary: Module to test the ceilometer service

'''

import textwrap
import sys
import httplib2 as http
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
import ceilometer_api
import compute_api
import keystone_api

import json

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

def main(argv):
    print "Hello There. This is a simple test application making a test API call to OpenStack"
    auth_uri = 'http://160.85.4.10:5000' #internal test-setup, replace it with your own value
    status, token_data = keystone_api.get_token_v3(auth_uri)
    if status:
        print 'The authentication was successful, below are the data we got:'
        print '--------------------------------------------------------------------------------------------------------'
        print '%1s %32s %2s %64s %1s' % ('|', 'key', '|', 'value', '|')
        print '--------------------------------------------------------------------------------------------------------'
        for key, value in token_data.iteritems():
            if key not in {'token-id'}:
                print '%1s %32s %2s %64s %1s' % ('|', key, '|', value, '|')
        print '--------------------------------------------------------------------------------------------------------'
        print 'The authentication token is: ', token_data["token-id"]
        pom=token_data["token-id"]

    else:
        print "Authentication was not successful."

    meter_stat = [None]
    headers = {
               #'Accept': 'application/json',
               'Content-Type': 'application/json;',
               'X-Auth-Token': pom
               
    }


    path = "/v2/meters/cpu/statistics"
    target = urlparse(token_data["metering"]+path)
    method = 'GET'
    #q='{"field": "project_id","op": "eq","value": "4e9c4e1b93124cdba2a930e98eb26ede"}'

    body="""{"q":['{"field": "project_id","op": "eq","value": "4e9c4e1b93124cdba2a930e98eb26ede"}']} """
            
        
    
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

        
        

    
if __name__ == '__main__':
    main(sys.argv[1:])