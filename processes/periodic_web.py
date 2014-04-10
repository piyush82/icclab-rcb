'''
Created on Apr 9, 2014

@author: kolv
'''

from django.contrib import admin
from main_menu.models import StackUser,PricingFunc, PriceLoop, MetersCounter,\
    Udr, PriceCdr
from django.http import HttpResponseRedirect
import sys,os
from django.core import urlresolvers
from django.forms import widgets
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
import ceilometer_api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'processes')))
import periodic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf.urls import patterns
from django.shortcuts import render
import django.forms as forms
from django.shortcuts import render_to_response
from django.contrib import messages
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from main_menu.views import auth_token,is_auth
from time import gmtime, strftime
from threading import Timer

def get_delta_samples(self,token_data,token_id,user,meter):
    delta=0.0
    samples = list(MetersCounter.objects.filter(user_id=user,meter_name=meter)) 
    if len(samples)==1:
        delta=0.0
    else:
        last=samples[-1]
        second_to_last=samples[-2]
        delta=last-second_to_last
    return delta
        
def get_udr(self,token_data,token_id,user,meters_used,meter_list,func):
    date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    delta_list=[None]*5
    for i in range(len(meters_used)):
        rez=0.0
        status,sample_list=ceilometer_api.get_meter_samples(meters_used[i],token_data["metering"],token_id,False,meter_list)
        for k in range(len(sample_list)):
            rez+=sample_list[k]["counter-volume"]
            meters_counter=MetersCounter(meter_name=meters_used[i],user_id=user,counter_volume=rez,unit=sample_list[k]["counter-unit"],timestamp=date_time)
            meters_counter.save() 
        delta=self.get_delta_samples(token_data,token_id,user,meters_used[i])
        delta_list[i]=delta
    udr=Udr(user_id=user,timestamp=date_time,pricing_func_id=func, param1=delta_list[0], param2=delta_list[1], param3=delta_list[2], param4=delta_list[3], param5=delta_list[4])
    udr.save()        
    return udr
        

def periodic(self,token_data,token_id,meters_used,meter_list,func,user,time):
    udr=self.get_udr(token_data,token_id,user,meters_used,meter_list,func)
    price=self.pricing(user)
    t = Timer(float(time),periodic,args=[token_data,token_id,meters_used,meter_list,func,user,time])
    t.start()
    
    
def pricing(self,user):
    func=PricingFunc.objects.get(user_id=user)
    udr=Udr.objects.get(user_id=user,pricing_func_id=func)
    udr.reverse()[0]
    pricing_list=[]
    pricing_list.append(udr.param1)
    pricing_list.append(func.sign1)
    pricing_list.append(udr.param2)
    pricing_list.append(func.sign2)
    pricing_list.append(udr.param3)
    pricing_list.append(func.sign3)
    pricing_list.append(udr.param4)
    pricing_list.append(func.sign4)
    pricing_list.append(udr.param5)
            
    price=0.0 
            
    for i in range(len(pricing_list)):
        if i==0:   
            if periodic.is_number(pricing_list[i]):    
                price=price+float(pricing_list[i]) 
 
        if i%2!=0:
            if pricing_list[i] in ["+","-","*","/","%"]:
                if periodic.is_number(pricing_list[i+1]):
                    x=float(pricing_list[i+1])                             
                else:
                    break                          
                if pricing_list[i]=="+":
                    price=price+x
                if pricing_list[i]=="-": 
                    price=price-x
                if pricing_list[i]=="*":
                    price=price*x
                if pricing_list[i]=="/":
                    if x!=0:
                        price=price/x
                if pricing_list[i]=="%":
                    price=price*x/100.0
    date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cdr=PriceCdr(user_id=user,timestamp=date_time,pricing_func_id=func, price=price)
    cdr.save()
    return price


