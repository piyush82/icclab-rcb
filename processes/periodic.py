'''
Created on Jan 27, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@zhaw.ch
@organization: ICCLab, Zurich University of Applied Sciences

'''

import textwrap
import threading,time
import httplib2 as http
import sys, re
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
#sys.path.append('/home/kolv/workspace/icc-lab-master/os_api')
import ceilometer_api
import compute_api
import keystone_api
import json
from collections import namedtuple
from threading import Timer
from time import sleep
import sqlite3
import datetime
import logging
from time import gmtime, strftime
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


def is_number(s):
    """

    Check if it is a number.
    
    Args:
      s: The variable that needs to be checked.
      
    Returns:
      bool: True if float, False otherwise.
      
    """    
    try:
        float(s)
        return True
    except ValueError:
        return False
  
path=(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'logs')))  
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(path+'/periodic.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


def periodic_counter(meters_used,metering,pom,periodic_counts,reden_br,time,meters_ids,input,meter_list):
    """

    Counter thats called periodically and inserts the metered data in one table and the calculated price in another.
    
    Args:
      meters_used(list): The list of the meters used in the pricing function.
      metering(string): The api endpoint for the ceilometer service.
      pom(string): X-Auth-token.
      periodic_counts(list): List with a list of the metered data from every count for each separate meter thats used in the pricing function.
      reden_br(int):Number of meter.
      time(float): Seconds till the next periodic count.
      meter_ids(list): List of the ids of every meter used.
      input: Flag indicating whether we want to define the pricing function or use the previous one already defined.
      meter_list: List with the available meters.
      
    Returns:
      bool: True if successful, False otherwise.
      
    """    

    global conn    
    conn = sqlite3.connect('meters.db',check_same_thread=False)
    
    for i in range(len(meters_used)):
        

        status,sample_list=ceilometer_api.get_meter_samples(str(meters_used[i]),metering,pom,False,meter_list)
        logger.info('In periodic: Getting meter samples')
        if status:
            print '--------------------------------------------------------------------------------------------------------------------------' 
            for j in range(len(sample_list)):     
                print "Resource id: " + str(sample_list[j]["resource-id"]) 
                print "Counter volume: "+ str(sample_list[j]["counter-volume"]) 
                print "Timestamp: " + str(sample_list[j]["timestamp"])
          
                datetime1=str(sample_list[j]["timestamp"]).split("T")
                
                #list with a list of the metered data from every count for each separate meter thats used in the pricing function
                periodic_counts[i].append(sample_list[j]["counter-volume"])

                #calculate the difference between the metered data from each count for every meter used in the pricing function
                print "Delta: " +str(periodic_counts[i][reden_br]-periodic_counts[i][reden_br-1])
                
                #get the row count; if its first entry-id=0; else get the last id and increment it by one
                cursor = conn.execute("SELECT max(ID)  from METERS_COUNTER")
                row_count=conn.execute("SELECT COUNT(*) from METERS_COUNTER ")
                result=row_count.fetchone()
                number_of_rows=result[0]
                
                for k in range(len(meter_list)):
                    if meter_list[k]["meter-name"]==meters_used[i]:
                        tenant=meter_list[k]["tenant-id"]

                if number_of_rows==0:
                    conn.execute("INSERT INTO METERS_COUNTER (ID,METER_ID,METER_NAME,USER_ID,RESOURCE_ID,COUNTER_VOLUME,UNIT,TIMESTAMP,TENANT_ID) \
                          VALUES (1, '"+ str(meters_ids[i]) +"', '"+ str(meters_used[i]) +"','" + str(sample_list[j]["user-id"]) +" ','"+ str(sample_list[j]["resource-id"]) +"' ,' "+ str(sample_list[j]["counter-volume"])+"' ,' "+ str(sample_list[j]["counter-unit"]) +"' ,' "+ str(datetime1[0])+" "+str(datetime1[1])+"' ,' "+tenant+" ')")
                else:
                    id_last = cursor.fetchone()[0]+1
                    conn.execute("INSERT INTO METERS_COUNTER (ID,METER_ID,METER_NAME,USER_ID,RESOURCE_ID,COUNTER_VOLUME,UNIT,TIMESTAMP,TENANT_ID) \
                            VALUES ("+str(id_last)+",' "+ str(meters_ids[i]) +"', '"+ str(meters_used[i]) +"','" + str(sample_list[j]["user-id"]) +" ','"+ str(sample_list[j]["resource-id"]) +"' ,' "+ str(sample_list[j]["counter-volume"])+"' ,' "+ str(sample_list[j]["counter-unit"]) +"' ,' "+ str(datetime1[0])+" "+str(datetime1[1])+"' ,' "+tenant+" ')")    
               

                conn.commit()
                logger.info('Insert data in meters_counter ')
    reden_br+=1
    
    status2,meters_used2,meters_ids2,func,price=pricing(metering,meter_list,pom,input)
    if status2:
        cursor2 = conn.execute("SELECT max(ID)  from PRICE_LOOP")
        row2_count=conn.execute("SELECT COUNT(*) from PRICE_LOOP ")
        result2=row2_count.fetchone()
        number_of_rows2=result2[0]
        datetime2=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if number_of_rows2==0:
            conn.execute("INSERT INTO PRICE_LOOP(ID,PRICE,TIMESTAMP,TENANT_ID) \
                    VALUES (1, '"+ str(price) +"' ,' "+ str(datetime2)+"' ,' "+tenant+" ')")
        else:
            id_last2 = cursor2.fetchone()[0]+1
            conn.execute("INSERT INTO PRICE_LOOP (ID,PRICE,TIMESTAMP,TENANT_ID) \
                    VALUES ("+str(id_last2)+",' "+ str(price)  +"' ,' "+ str(datetime2)+"' ,' "+tenant+" ')")    
               

        conn.commit()
        logger.info('Insert data in price_loop ')
    t = Timer(float(time),periodic_counter,args=[meters_used,metering,pom,periodic_counts,reden_br,time,meters_ids,input,meter_list])
    t.start()
    return status

def pricing(metering,meter_list,pom,input):     
            """

            Method for defining the pricing function.
    
            Args:
              metering(string): The api endpoint for the ceilometer service.
              pom(string): X-Auth-token.
              meter_list: List with the available meters.              
              input: Flag indicating whether we want to define the pricing function or use the previous one already defined.
      
            Returns:
              bool: True if successful, False otherwise.
              list: List of the meters used in the pricing function.
              list: List of the meter's ids.
              string: The user input for the pricing function.
              float: The price.
      
            """                         
            price=0
            if input==None:
                price_def=raw_input("Define the pricing function. Use only the meters from above and numbers as arguments. Use the following signs: '+' for sum, '-' for substraction, '*' for multiplying, '/' for division or '%' for percentage. Use whitespace in between. ")
                price_def=price_def.split(" ")
                if len(price_def)>9:
                    print "You can use only 5 parameters"
                    logger.warn('More than 5 parameters used')
                    price_def=raw_input("Define the pricing function. Use only the meters from above and numbers as arguments. Use the following signs: '+' for sum, '-' for substraction, '*' for multiplying, '/' for division or '%' for percentage. Use whitespace in between. ")
                input=price_def
            else:
                price_def=input
            meters_used=[]
            meters_ids=[]
            
            for i in range(len(price_def)):
                j=0
                while j<len(meter_list):
                    if price_def[i]==meter_list[j]["meter-name"]:
                        meters_used.append(price_def[i])
                        meters_ids.append(meter_list[j]["meter-id"])

                        status,sample_list=ceilometer_api.get_meter_samples(price_def[i],metering,pom,False,meter_list)
                        logger.info('In pricing: Getting meter samples')
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
                                break
                            
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
                                    logger.warn('Division by zero')
                                    
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
                logger.info('Price is %s', price)
            else:
                print "Error. Poorly defined pricing function."
                logger.warn('Not properly defined pricing function')
                
            return status_ret,meters_used,meters_ids,input,price
         
conn = sqlite3.connect('meters.db',check_same_thread=False)
print "Opened database successfully"           

          
 
def main(argv):

    print "Hello there. This is a simple periodic counter."
    logger.info('--------------- \n')
    logger.info('Starting periodic ')
    auth_uri = 'http://160.85.4.10:5000' #internal test-setup, replace it with your own value
    #auth_uri = 'http://160.85.231.233:5000' #internal test-setup, replace it with your own value
                    
    status, token_data = keystone_api.get_token_v3(auth_uri)
    if status:
        print 'The authentication was successful.'
        print '--------------------------------------------------------------------------------------------------------'
        print 'The authentication token is: ', token_data["token-id"]
        pom=token_data["token-id"]
        user=token_data["user-id"]
        logger.info('Successful authentication for user %s', user)
    else:
        print "Authentication was not successful."
        logger.warn('Authentication not successful')
    if status:
        status, meter_list = ceilometer_api.get_meter_list(pom, token_data["metering"])
        if status:
            logger.info('Printing meters')
            print "The list of available meters are printed next."
            print '--------------------------------------------------------------------------------------------------------------------------'
            print '%1s %16s %2s %10s %2s %10s %2s %70s %1s' % ('|','meter-name', '|', 'meter-type', '|', 'meter-unit', '|', 'meter-id', '|')
            print '--------------------------------------------------------------------------------------------------------------------------'

            for i in range(len(meter_list)):
                print '%1s %16s %2s %10s %2s %10s %2s %70s %1s' % ('|', meter_list[i]["meter-name"], '|', meter_list[i]["meter-type"], '|', meter_list[i]["meter-unit"], '|', meter_list[i]["meter-id"].strip(), '|')         
                logger.info('Meter list %s', meter_list[i]["meter-name"])
            status,meters_used,meters_ids,input,price=pricing(token_data["metering"],meter_list,pom,None)
            logger.info('Defining pricing function. %s', input)
            global conn    
            conn = sqlite3.connect('meters.db',check_same_thread=False)
            func=[None]*9
            for i in range(len(input)):
                func[i]=input[i]
            conn.execute("INSERT INTO PRICING_FUNC (USER_ID,PARAM1,SIGN1,PARAM2,SIGN2,PARAM3,SIGN3,PARAM4,SIGN4,PARAM5) \
                       VALUES ( '"+ str(user) +"', '"+ str(func[0]) +"','" +str(func[1]) +"','" +str(func[2]) +"','" + str(func[3]) +" ','"+ str(func[4]) +"' ,' "+ str(func[5])+"' ,' "+ str(func[6]) +"' ,' "+ str(func[7])+"' ,' "+str(func[8])+" ')")
            conn.commit()
            logger.info('Insert pricing function in database')
            if status:
                time=raw_input("Enter the desired time interval in seconds. ")
                if time=="":
                    time=10                
                periodic_counts = [None]*len(meters_used)
                for i in range(len(meters_used)):
                    periodic_counts[i]=[]
                periodic_counter(meters_used,token_data["metering"],pom,periodic_counts,0,time,meters_ids,input,meter_list) 
                logger.info('Starting counter. Time interval is %s ', time)
                conn.close()
               

    return True
    
if __name__ == '__main__':
    main(sys.argv[1:])
            