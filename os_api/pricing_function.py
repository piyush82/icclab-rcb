'''
Created on Jan 14, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@zhaw.ch
@organization: ICCLab, Zurich University of Applied Sciences

'''

import ceilometer_api
import compute_api
import keystone_api
import textwrap
import sys

def main(argv):
    print "Hello There. This is a simple test pricing function."
    auth_uri = 'http://160.85.231.210:5000' #internal test-setup, replace it with your own value
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
            print '--------------------------------------------------------------------------------------------------------------------------'
            print "Define the pricing function."
            number_of_meters=raw_input("Enter the desired number of meters you want to use in your function: ")
            meter_name={}
            price=0
            for i in range(number_of_meters):
                meter_name[i]=raw_input("Enter the desired meter name: ")
#                 for j in range(len(meter_list)):
#                     if meter_name[i]==meter_list[j][meter_name[i]]:
#                         if meter_list[j]["meter-type"] != "gauge":
#                             att=raw_input("Do you want to use an attribute(average,maximum,minimum,sum)? Enter 'Y', if yes.")
#                             if att=="Y":
#                                 att_def=raw_input("Which attribute do you want to use? Write 'avg' for average, 'min' for minimum, 'max' for maximum or 'sum' for sum: ")
#                                 st,stat_list=ceilometer_api.meter_statistics(meter_name[i], token_data["metering"],pom)

                status,sample_list=ceilometer_api.get_meter_samples(meter_name,token_data["metering"],pom)
                if status:
                    for j in range(len(sample_list)):
                        if meter_name[i]==str(sample_list[j]["counter-name"]) :
                            param[i]=sample_list[i]["counter-volume"]
                            price=price+param[i]
                pom=raw_input("Do you want to execute a mathematical operation onto this parameter? Enter 'Y', if yes.")
                if pom=='Y':
                    pom_def=raw_input("What operation do you wan to perform? Enter '+' for sum, '-' for substraction, '*' for multiplying, '/' for division or '%' for percentage: ")
                    
                                
                                    
                            
                            
                            
                            
                            
                            