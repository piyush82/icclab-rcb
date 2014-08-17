'''
Created on Jan 14, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@zhaw.ch
@organization: ICCLab, Zurich University of Applied Sciences
@summary: Define the pricing function.

'''
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
import ceilometer_api
import compute_api
import keystone_api
import textwrap
import logging
dir_path=os.path.join(os.path.dirname( __file__ ), '..',)
config = {}
execfile(dir_path+"/config.conf", config) 
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
path=(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'logs')))    
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(path+'/pricing_func.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False    

def main(argv):
    print "Hello There. This is a simple test pricing function."
    auth_uri = config["AUTH_URI"] #internal test-setup, replace it with your own value
    status, token_data = keystone_api.get_token_v3(auth_uri)
    if status:
        print 'The authentication was successful.'
        print '--------------------------------------------------------------------------------------------------------'
        print 'The authentication token is: ', token_data["token-id"]
        pom=token_data["token-id"]
        logger.info('Authentication was successful')
    else:
        print "Authentication was not successful."
        logger.info('Authentication was not successful')
    if status:
        status, meter_list = ceilometer_api.get_meter_list(pom, token_data["metering"])
        if status:
            print "The list of available meters are printed next."
            print '--------------------------------------------------------------------------------------------------------------------------'
            print '%1s %16s %2s %10s %2s %10s %2s %70s %1s' % ('|','meter-name', '|', 'meter-type', '|', 'meter-unit', '|', 'meter-id', '|')
            print '--------------------------------------------------------------------------------------------------------------------------'
            for i in range(len(meter_list)):
                print '%1s %16s %2s %10s %2s %10s %2s %70s %1s' % ('|', meter_list[i]["meter-name"], '|', meter_list[i]["meter-type"], '|', meter_list[i]["meter-unit"], '|', meter_list[i]["meter-id"].strip(), '|')
            print '--------------------------------------------------------------------------------------------------------------------------'
 
            #user defined price function; usage of white space for parsing the data
            price=0
            price_def=raw_input("Define the pricing function. Use only the meters from above and numbers as arguments. Use the following signs: '+' for sum, '-' for substraction, '*' for multiplying, '/' for division or '%' for percentage. Use whitespace in between. ")
            price_def=price_def.split(" ")
            if len(price_def)>9:
                print "You can use only 5 parameters"
                logger.warn('Pricing function not properly defined')
                price_def=raw_input("Define the pricing function. Use only the meters from above and numbers as arguments. Use the following signs: '+' for sum, '-' for substraction, '*' for multiplying, '/' for division or '%' for percentage. Use whitespace in between. ")            
            
            meters_used=[None]
            
            for i in range(len(price_def)):
                j=0
                while j<len(meter_list):
                    if price_def[i]==meter_list[j]["meter-name"]:
                        meters_used.append(price_def[i])
                        print "Enter query arguments."
                        status,sample_list=ceilometer_api.get_meter_samples(price_def[i],token_data["metering"],pom,True,meter_list)
                        logger.info('Getting meter samples')
                        if sample_list==[]:
                            price_def[i]=str(0)

                        #replace the meter name with the metered data
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
   
                            #check if every other parameter is a number and the parameters in between math signs
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
                logger.info('Calculated price is: %s',price)
            else:
                print "Error. Poorly defined pricing function."
                logger.warn('Pricing function not properly defined')
        return status_ret,meters_used


    
if __name__ == '__main__':
    main(sys.argv[1:])            
            
            
        
                                
                                
                                

                    
                    
                        
                
            
                
                                    
                            
                            
                            
                            
                            
                            