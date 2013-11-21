# -*- coding: ascii -*-
#--------------------------------------------------------------
#Created on Nov 21, 2013
#
#@author: Piyush Harsh
#@contact: piyush.harsh@zhaw.ch
#@organization: ICCLab, Zurich University of Applied Sciences
#@summary: Module to interact with OS-services
#@var username, tenant-id, password
#@requires: python 2.7
#--------------------------------------------------------------

import ceilometer_api
import compute_api
import keystone_api
import sys

def main(argv):
    print "Hello There. This is a simple test application making a test API call to OpenStack"
    auth_uri = 'http://192.168.100.4:5000' #internal test-setup, replace it with your own value
    #auth_uri = 'http://160.85.4.11:5000' #internal test-setup, replace it with your own value
    status, token_data = keystone_api.get_token_v2(auth_uri)
    if status:
        for key, value in token_data.iteritems():
            print key, value
    else:
        print "Authentication was not successful."
    if status:
        status, server_list = compute_api.get_server_list(token_data["token-id"], token_data["nova"])
        if status:
            print "The list of servers are printed next."
            print server_list
        status, meter_list = ceilometer_api.get_meter_list(token_data["token-id"], token_data["ceilometer"])
        if status:
            print "The list of available meters are printed next."
            print '--------------------------------------------------------------------------------------------------------------------------'
            print '%1s %16s %2s %10s %2s %10s %2s %70s %1s' % ('|','meter-name', '|', 'meter-type', '|', 'meter-unit', '|', 'meter-id', '|')
            print '--------------------------------------------------------------------------------------------------------------------------'
            for i in range(len(meter_list)):
                print '%1s %16s %2s %10s %2s %10s %2s %70s %1s' % ('|', meter_list[i]["meter-name"], '|', meter_list[i]["meter-type"], '|', meter_list[i]["meter-unit"], '|', meter_list[i]["meter-id"].strip(), '|')
            print '--------------------------------------------------------------------------------------------------------------------------'
            #print meter_list
    return True
    
if __name__ == '__main__':
    main(sys.argv[1:])