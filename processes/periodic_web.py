'''
Created on Apr 9, 2014

@author: kolv
'''
from threading import Thread
from django.contrib import admin
from main_menu.models import StackUser,PricingFunc, PriceLoop, MetersCounter,\
    Udr, PriceCdr
from django.http import HttpResponseRedirect
import sys,os
from django.core import urlresolvers
from django.forms import widgets
import datetime
import time
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
from django.contrib import messagessp
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from main_menu.views import auth_token,is_auth
from time import gmtime, strftime
from threading import Timer


def periodic_counter(self,token_data,token_id,meters_used,meter_list,func,user,time,from_date,from_time,end_date,end_time,user_id_stack):
    

    q=ceilometer_api.set_query(from_date,end_date,from_time,end_time,"/",user_id_stack,True) 
    udr=get_udr(self,token_data,token_id,user,meters_used,meter_list,func,True,q=q)
    price=pricing(self,user,meter_list)
    #t = Timer(10,periodic_counter,args=[self,token_data,token_id,meters_used,meter_list,func,user,time])
    #t.start()

def get_delta_samples(self,token_data,token_id,user,meter):
    delta=0.0
    meter2=str(meter)
    samples =list( MetersCounter.objects.filter(user_id=user,meter_name = meter))
    #if len(samples)==1:
    #    delta=0.0
    #else:
    last=str(samples[-1])
        #second_to_last=str(samples[-2])
        #delta=float(last)-float(second_to_last)
    return last
        
def get_udr(self,token_data,token_id,user,meters_used,meter_list,func,web_bool,q):
    date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    delta_list=[None]*5
    all_stats=[] 
    for i in range(len(meters_used)):
        #rez=0.0
        #status,sample_list=ceilometer_api.get_meter_samples(meters_used[i],token_data["metering"],token_id,False,meter_list,web_bool,q=q)
        #for k in range(len(sample_list)):
        #    rez+=sample_list[k]["counter-volume"]
        #    meters_counter=MetersCounter(meter_name=meters_used[i],user_id=user,counter_volume=rez,unit=sample_list[k]["counter-unit"],timestamp=date_time)
        #    meters_counter.save() 
        status,stat_list=ceilometer_api.meter_statistics(meters_used[i], token_data["metering"],token_id,meter_list,True,q=q)
        all_stats.append(stat_list)
        if stat_list==[]:
            meters_counter=MetersCounter(meter_name=meters_used[i],user_id=user,counter_volume=0.0,unit="/" ,timestamp=date_time)
        else:
            meters_counter=MetersCounter(meter_name=meters_used[i],user_id=user,counter_volume=stat_list[0]["sum"],unit=stat_list[0]["unit"] ,timestamp=date_time)
        meters_counter.save() 
        delta=get_delta_samples(self,token_data,token_id,user,meters_used[i])
        delta_list[i]=delta
        udr=Udr(user_id=user,timestamp=date_time,pricing_func_id=func, param1=delta_list[0], param2=delta_list[1], param3=delta_list[2], param4=delta_list[3], param5=delta_list[4])
        udr.save()        
    return udr




def pricing(self,user,meter_list):
    func=PricingFunc.objects.get(user_id=user)
    udr=Udr.objects.filter(user_id=user,pricing_func_id=func).order_by('-id')[0]
    #udr.reverse()[:1]
    pricing_list=[]
    pricing_list.append(func.param1)
    pricing_list.append(func.sign1)
    pricing_list.append(func.param2)
    pricing_list.append(func.sign2)
    pricing_list.append(func.param3)
    pricing_list.append(func.sign3)
    pricing_list.append(func.param4)
    pricing_list.append(func.sign4)
    pricing_list.append(func.param5)
    
    
    udr_list=[]
    udr_list.append(udr.param1)
    udr_list.append(udr.param2)
    udr_list.append(udr.param3)
    udr_list.append(udr.param4)
    udr_list.append(udr.param5)
    for i in udr_list:
        if i==None:
            i=0
            
    k=0
    for i in range(len(pricing_list)):
        j=0
        while j<len(meter_list):
            if pricing_list[i]==meter_list[j]["meter-name"]:
                pricing_list[i]=udr_list[k]
                k+=1
            else:
                j=j+1 
            
    price=0.0 
            
    for i in range(len(pricing_list)):
        if i==0:   
            if periodic.is_number(str(pricing_list[i])):    
                price=price+float(str(pricing_list[i]))
 
        if i%2!=0:
            if pricing_list[i] in ["+","-","*","/","%"]:
                if periodic.is_number(str(pricing_list[i+1])):
                    x=float(str(pricing_list[i+1]))                             
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



class MyThread(Thread):
    def __init__(self, k_self,token_data,token_id,meters_used,meter_list,func,user,time_f,from_date,from_time,end_date,end_time,user_id_stack):
        super(MyThread, self).__init__()
        self.daemon = True
        self.cancelled = False
        self.k_self=k_self
        self.token_data=token_data
        self.token_id=token_id
        self.meters_used=meters_used
        self.meter_list=meter_list
        self.func=func
        self.user=user
        self.time_f=time_f
        self.from_date=from_date
        self.from_time=from_time
        self.func=func
        self.end_date=end_date
        self.end_time=end_time
        self.user_id_stack=user_id_stack

    def run(self):
        """Overloaded Thread.run, runs the update 
        method once per every 10 milliseconds."""

        while not self.cancelled:
            periodic_counter(self.k_self,self.token_data,self.token_id,self.meters_used,self.meter_list,self.func,self.user,self.time_f,self.from_date,self.from_time,self.end_date,self.end_time,self.user_id_stack)
            self.from_time=self.end_time
            self.from_date=self.end_date
            today = datetime.date.today()
            today.strftime("%Y-%m-%d")
            now = datetime.datetime.now()
            now=datetime.time(now.hour, now.minute, now.second)
            now.strftime("%H:%M:%S")
            self.end_date=str(today)
            self.end_time=str(now)

            time.sleep(self.time_f)

    def cancel(self):
        """End this timer thread"""
        self.cancelled = True
