'''
Created on Jan 27, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@zhaw.ch
@organization: ICCLab, Zurich University of Applied Sciences

'''

import ceilometer_api
import compute_api
import keystone_api
import textwrap
import threading,time
import httplib2 as http
import sys, re
import json
from collections import namedtuple
from threading import Timer
from time import sleep
import sqlite3

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_meter_samples_periodic(meter_name,api_endpoint,token):
    meter_samples=[None]
    headers = {
               'Content-Type': 'application/json;',
               'X-Auth-Token': token
               
    }
  
    path = "/v2/meters/"+meter_name
    target = urlparse(api_endpoint+path)
    method = 'GET'  
    body='{"limit": 1 }'
    
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
            cat_pom = json.dumps(catalog)
            cat_pom=cat_pom.translate(None,'"{}')
            meter_samples[i]["resource-metadata"]=cat_pom
            meter_samples[i]["source"] = data[i]["source"]
            meter_samples[i]["timestamp"] = data[i]["timestamp"]
            meter_samples[i]["user-id"] = data[i]["user_id"]
        return True, meter_samples
    


def periodic_counter(meters_used,metering,pom,periodic_counts,reden_br,time,meters_ids):

    
    for i in range(len(meters_used)):
        

        status,sample_list=get_meter_samples_periodic(str(meters_used[i]),metering,pom)
        if status:
            print '--------------------------------------------------------------------------------------------------------------------------' 
            for j in range(len(sample_list)):     
                print "Resource id: " + str(sample_list[j]["resource-id"]) 
                print "Counter volume: "+ str(sample_list[j]["counter-volume"]) 
                print "Timestamp: " + str(sample_list[j]["timestamp"])
          
                datetime=str(sample_list[j]["timestamp"]).split("T")
                periodic_counts[i].append(sample_list[j]["counter-volume"])

                global conn    
                conn = sqlite3.connect('meters.db',check_same_thread=False)
                print "Delta: " +str(periodic_counts[i][reden_br]-periodic_counts[i][reden_br-1])
                cursor = conn.execute("SELECT max(ID)  from METERS_COUNTER")
                row_count=conn.execute("SELECT COUNT(*) from METERS_COUNTER ")
                result=row_count.fetchone()
                number_of_rows=result[0]
                #print number_of_rows
                if number_of_rows==0:
                    conn.execute("INSERT INTO METERS_COUNTER (ID,METER_ID,METER_NAME,USER_ID,RESOURCE_ID,COUNTER_VOLUME,UNIT,TIMESTAMP) \
                          VALUES (1, '"+ str(meters_ids[i]) +"', '"+ str(meters_used[i]) +"','" + str(sample_list[j]["user-id"]) +" ','"+ str(sample_list[j]["resource-id"]) +"' ,' "+ str(sample_list[j]["counter-volume"])+"' ,' "+ str(sample_list[j]["counter-unit"]) +"' ,' "+ str(datetime[0])+" "+str(datetime[1])+" ')")
                else:
                    id_last = cursor.fetchone()[0]+1
                    conn.execute("INSERT INTO METERS_COUNTER (ID,METER_ID,METER_NAME,USER_ID,RESOURCE_ID,COUNTER_VOLUME,UNIT,TIMESTAMP) \
                            VALUES ("+str(id_last)+",' "+ str(meters_ids[i]) +"', '"+ str(meters_used[i]) +"','" + str(sample_list[j]["user-id"]) +" ','"+ str(sample_list[j]["resource-id"]) +"' ,' "+ str(sample_list[j]["counter-volume"])+"' ,' "+ str(sample_list[j]["counter-unit"]) +"' ,' "+ str(datetime[0])+" "+str(datetime[1])+" ')")    
               
#                 id_last+=1
                conn.commit()
    reden_br+=1
    
    t = Timer(float(time),periodic_counter,args=[meters_used,metering,pom,periodic_counts,reden_br,time,meters_ids])
    t.start()
    return status

def pricing(metering,meter_list,pom):                        
            price=0
            price_def=raw_input("Define the pricing function. Use only the meters from above and numbers as arguments. Use the following signs: '+' for sum, '-' for substraction, '*' for multiplying, '/' for division or '%' for percentage. Use whitespace in between. ")
            price_def=price_def.split(" ")

            meters_used=[]
            meters_ids=[]
            
            for i in range(len(price_def)):
                j=0
                while j<len(meter_list):
                    if price_def[i]==meter_list[j]["meter-name"]:
                        meters_used.append(price_def[i])
                        meters_ids.append(meter_list[j]["meter-id"])

                        status,sample_list=get_meter_samples_periodic(price_def[i],metering,pom)
                        if sample_list==[]:
                            price_def[i]=str(0)

                        
                        for n,m in enumerate(price_def):
                            if m==price_def[i]:
                                for k in range(len(sample_list)):
                                    price_def[n]=str(sample_list[k]["counter-volume"])                                 
                        break
                    else:
                        j=j+1
                       
            
            status_ret=True 
            
            for i in range(len(price_def)):
                if i==0:   
                     if is_number(price_def[i]):    
                         price=price+float(price_def[i]) 
                                  
                     else:
                         status_ret=False  
                if i%2!=0:
                    if price_def[i] in ["+","-","*","/","%"]:
   
                       
                            if is_number(price_def[i+1]):
                                 x=float(price_def[i+1])
                                
                            else:
                                status_ret=False
                            
                            if price_def[i]=="+":
                                price=price+x
                            if price_def[i]=="-": 
                                price=price-x
                            if price_def[i]=="*":
                                price=price*x
                            if price_def[i]=="/":
                                if x!=0:
                                    price=price/x
                                else:
                                    print "Division by zero."
                                    status_ret=False
                            if price_def[i]=="%":
                                price=price*x/100.0
                                print price
                    else:
                        status_ret=False
                else:
                    continue
            if status_ret==True:
                print "The price value is: " + str(price)
            else:
                print "Error. Poorly defined pricing function."
            return status_ret,meters_used,meters_ids
         
conn = sqlite3.connect('meters.db',check_same_thread=False)
print "Opened database successfully"           

          
 
def main(argv):
    print "Hello there. This is a simple periodic counter."
    auth_uri = 'http://160.85.4.10:5000' #internal test-setup, replace it with your own value
    status, token_data = keystone_api.get_token_v3(auth_uri)
    if status:
        print 'The authentication was successful.'
        print '--------------------------------------------------------------------------------------------------------'
        print 'The authentication token is: ', token_data["token-id"]
        pom=token_data["token-id"]
    else:
        print "Authentication was not successful."
    if status:
        status, meter_list = ceilometer_api.get_meter_list(pom, token_data["metering"])
        if status:
            print "The list of available meters are printed next."
            print '--------------------------------------------------------------------------------------------------------------------------'
            print '%1s %16s %2s %10s %2s %10s %2s %70s %1s' % ('|','meter-name', '|', 'meter-type', '|', 'meter-unit', '|', 'meter-id', '|')
            print '--------------------------------------------------------------------------------------------------------------------------'

            for i in range(len(meter_list)):
                print '%1s %16s %2s %10s %2s %10s %2s %70s %1s' % ('|', meter_list[i]["meter-name"], '|', meter_list[i]["meter-type"], '|', meter_list[i]["meter-unit"], '|', meter_list[i]["meter-id"].strip(), '|')         

            status,meters_used,meters_ids=pricing(token_data["metering"],meter_list,pom)
            if status:
                time=raw_input("Enter the desired time interval in seconds. ")                
                periodic_counts = [None]*len(meters_used)
                for i in range(len(meters_used)):
                    periodic_counts[i]=[]
                periodic_counter(meters_used,token_data["metering"],pom,periodic_counts,0,time,meters_ids) 
                conn.close()

    return True
    
if __name__ == '__main__':
    main(sys.argv[1:])
            