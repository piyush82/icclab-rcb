# -*- coding: ascii -*-
#--------------------------------------------------------------
#Created on Nov 21, 2013
#
#@author: Piyush Harsh
#@contact: piyush.harsh@zhaw.ch
#@organization: ICCLab, Zurich University of Applied Sciences
#@summary: Module to interact with OS-ceilometer service
#@contributor: Tea Kolevska
#@contact: tea.kolevska@zhaw.ch
#@var username, tenant-id, password
#@requires: python 2.7
#--------------------------------------------------------------

import httplib2 as http
import sys, re
import json
from collections import namedtuple

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

def query():
    status=False
    
    period=raw_input("Do you want to define the starting and ending time? If yes, enter 'Y',else enter 'N'. ")
    if(period=="Y"):
        from_date = raw_input("Date from yyyy-mm-dd: ")
        from_time= raw_input("Time from hh:mm:ss ")
        to_date = raw_input("Date to yyyy-mm-dd: ")
        to_time= raw_input("Time to hh:mm:ss ")
        status=True
    else:
        from_date="/" 
        to_date="/" 
        from_time="/" 
        to_time="/" 
    rid=raw_input("Do you want to define the resource id? If yes, enter 'Y', else enter 'N'. ")
    if(rid=="Y"):
        resource_id=raw_input("Enter the resource id: ")
        status=True
    else:
        resource_id="/"
    pid=raw_input("Do you want to define the project id? If yes, enter 'Y', else enter 'N'. ")
    if(pid=="Y"):
        project_id=raw_input("Enter the project id: ")
        status=True
    else:
        project_id="/"
    return from_date,to_date,from_time,to_time,resource_id,project_id,status

def set_query(from_date,to_date,from_time,to_time,resource_id,project_id,status_q):
    if(status_q==True):
        q='"q":['
        if (from_date not in "/"):
            q= q+'{"field": "timestamp","op": "ge","value": "'+from_date+'T'+from_time+'"},{"field": "timestamp","op": "lt","value": "'+to_date+'T'+to_time+'"}'
            if (resource_id != "/"):
                q=q+',{"field": "resource_id","op": "eq","value": "'+resource_id+'"}'
                if (project_id != "/"):
                    q=q+',{"field": "project_id","op": "eq","value": "'+project_id+'"}'
            else:
                if (resource_id != "/"):
                    q=q+'{"field": "resource_id","op": "eq","value": "'+resource_id+'"}'
        else:
            if (resource_id != "/"):
                q=q+'{"field": "resource_id","op": "eq","value": "'+resource_id+'"}'
                if (project_id != ""):
                    q=q+',{"field": "project_id","op": "eq","value": "'+project_id+'"}'
            else:
                if (resource_id != "/"):
                    q=q+'{"field": "resource_id","op": "eq","value": "'+resource_id+'"}'
        q=q+']'
    return q

def meter_statistics(meter_id,api_endpoint,token):
    meter_stat = [None]
    headers = {
               #'Accept': 'application/json',
               'Content-Type': 'application/json;',
               'X-Auth-Token': token
               
    }
    from_date,to_date,from_time,to_time,resource_id,project_id,status_q=query()   
    path = "/v2/meters/"+meter_id+"/statistics"
    target = urlparse(api_endpoint+path)
    method = 'GET'
    #body = '{"q":[{"field": "timestamp","op": "ge","value": "'+from_date+'T'+from_time+'"},{"field": "timestamp","op": "lt","value": "'+to_date+'T'+to_time+'"}]}'
    
    #body='{"q": [{"field": "timestamp","op": "ge","value": "2013-12-28T00:00:00"},{"field": "timestamp","op": "lt","value": "2014-01-05T00:00:00"}]}'
    
        
    if(status_q==True):
        q=set_query(from_date,to_date,from_time,to_time,resource_id,project_id,status_q)
        body="{"+q
        period=raw_input("Do you want to define a time period? Enter 'Y' if yes, 'N' if no.")
        if(period=="Y"):
            period_def=raw_input("Enter the desired time period in seconds: ")
            body=body+',"period":'+period_def
        groupby=raw_input("Do you want to define a group by value? Enter 'Y' if yes, 'N' if no.")  
        if (groupby=="Y") :
            rid=raw_input("Do you want to group by the resource id? If yes, enter 'Y', else enter 'N'. ")
            if(rid=="Y"):
                    groupby_def='",groupby":['
                    groupby_def=groupby_def+'"resource_id"'
                    pid=raw_input("Do you want to group by the project id? If yes, enter 'Y', else enter 'N'. ")
                    if(pid=="Y"):
                        groupby_def=groupby_def+',"project_id"'  
                        groupby_def=groupby_def+']'
                        body=body+groupby_def            
            else:
                pid=raw_input("Do you want to group by the project id? If yes, enter 'Y', else enter 'N'. ")
                if(pid=="Y"):
                    groupby_def='",groupby":['
                    groupby_def=groupby_def+'"project_id"'  
                    groupby_def=groupby_def+']'
                    body=body+groupby_def
        body=body+"}"
    else:
        body="{"
        period=raw_input("Do you want to define a time period? Enter 'Y' if yes, 'N' if no.")
        if(period=="Y"):
            period_def=raw_input("Enter the desired time period in seconds: ")
            body=body+'"period":'+period_def

            rid=raw_input("Do you want to group by the resource id? If yes, enter 'Y', else enter 'N'. ")
            if(rid=="Y"):
                groupby_def='",groupby":['
                groupby_def=groupby_def+'"resource_id"'
                pid=raw_input("Do you want to group by the project id? If yes, enter 'Y', else enter 'N'. ")
                if(pid=="Y"):
                    groupby_def=groupby_def+',"project_id"'  
                    groupby_def=groupby_def+']'
                    body=body+groupby_def            
                else:
                    pid=raw_input("Do you want to group by the project id? If yes, enter 'Y', else enter 'N'. ")
                    if(pid=="Y"):
                        groupby_def='",groupby":['
                        groupby_def=groupby_def+'"project_id"'  
                        groupby_def=groupby_def+']'
                        body=body+groupby_def
            body=body+"}"
        else: 
            rid=raw_input("Do you want to group by the resource id? If yes, enter 'Y', else enter 'N'. ")
            if(rid=="Y"):
                    groupby_def='"groupby":['
                    groupby_def=groupby_def+'"resource_id"'
                    pid=raw_input("Do you want to group by the project id? If yes, enter 'Y', else enter 'N'. ")
                    if(pid=="Y"):
                        groupby_def=groupby_def+',"project_id"'  
                    groupby_def=groupby_def+']'
                    body=body+groupby_def            
            else:
                pid=raw_input("Do you want to group by the project id? If yes, enter 'Y', else enter 'N'. ")
                if(pid=="Y"):
                    groupby_def='"groupby":['
                    groupby_def=groupby_def+'"project_id"'  
                    groupby_def=groupby_def+']'
                    body=body+groupby_def
            body=body+"}"
            
        
 
            
            
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
    
    
def get_meter_samples(meter_name,api_endpoint,token):
    meter_samples=[None]
    headers = {
               'Content-Type': 'application/json;',
               'X-Auth-Token': token
               
    }
    from_date,to_date,from_time,to_time,resource_id,project_id,status_q=query()   
    path = "/v2/meters/"+meter_name
    target = urlparse(api_endpoint+path)
    method = 'GET'
    if(status_q==True):
        q=set_query(from_date,to_date,from_time,to_time,resource_id,project_id,status_q)
        body="{"+q
        limit=raw_input("Do you want to set a limit to the number of samples that gets returned? Enter 'Y' if yes, 'N' if no.")
        if(limit=="Y"):
            limit_def=raw_input("Enter the desired limit for the number of samples: ")
            body=body+',"limit":'+limit_def
        body=body+"}"
    else:
        body="{"
        limit=raw_input("Do you want to set a limit to the number of samples that gets returned? Enter 'Y' if yes, 'N' if no.")
        if(limit=="Y"):
            limit_def=raw_input("Enter the desired limit for the number of samples: ")
            body=body+'"limit":'+limit_def
        body=body+"}"
    
    h = http.Http()
    response, content = h.request(target.geturl(),method,body,headers)
    header = json.dumps(response)
    json_header = json.loads(header)
    
    server_response = json_header["status"]
    if server_response not in {'200'}:
        print "Inside meter_samples(): Something went wrong!"
        return False, meter_samples
    else:
        data = json.loads(content)
        meter_samples = [None]*len(data)

        for i in range(len(data)):
            meter_samples[i]={}
            meter_samples[i]["counter-name"] = data[i]["counter_name"]
            meter_samples[i]["counter-type"] = data[i]["counter_type"]
            meter_samples[i]["counter-unit"] = data[i]["counter_unit"]
            meter_samples[i]["counter-volume"] = data[i]["counter_volume"]
            meter_samples[i]["message-id"] = data[i]["message_id"]
            meter_samples[i]["project-id"] = data[i]["project_id"]
            meter_samples[i]["resource-id"] = data[i]["resource_id"]
            catalog=data[i]["resource_metadata"]
            #for key,value in catalog.iteritems():
            #    meter_samples[i]["resource-metadata"][catalog[key]] = catalog[key]
            #meter_samples[i]["resource-metadata"]=data[i]["resource_metadata"]
            cat_pom = json.dumps(catalog)
            cat_pom=cat_pom.translate(None,'"{}')
            #meter_samples[i]["resource-metadata"] = dict(e.split(': ') for e in cat_pom.split(','))
            meter_samples[i]["resource-metadata"]=cat_pom
            meter_samples[i]["source"] = data[i]["source"]
            meter_samples[i]["timestamp"] = data[i]["timestamp"]
            meter_samples[i]["user-id"] = data[i]["user_id"]
        return True, meter_samples
        

    
    
    
    
    
    
    