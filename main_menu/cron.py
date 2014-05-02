'''
Created on Apr 30, 2014

@author: kolv
'''


from main_menu.models import StackUser,PricingFunc, PriceLoop, MetersCounter,Udr, PriceCdr
import datetime
import sys,os
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
import ceilometer_api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'processes')))
import periodic


def run(self,token_data,token_id,meters_used,meter_list,func,user,time):
    periodic_counter(self,token_data,token_id,meters_used,meter_list,func,user,time)

def periodic_counter(self,token_data,token_id,meters_used,meter_list,func,user,time):
    
    from_date="2014-04-20"
    from_time="00:00:00"
    to_date="2014-04-20"
    to_time="23:59:59"
    q=ceilometer_api.set_query(from_date,to_date,from_time,to_time,"/","/",True) 
    udr=get_udr(self,token_data,token_id,user,meters_used,meter_list,func,False,q)
    price=pricing(self,user,meter_list)



def get_delta_samples(self,token_data,token_id,user,meter):
    delta=0.0
    meter2=str(meter)
    samples =list( MetersCounter.objects.filter(user_id=user,meter_name = meter))
    if len(samples)==1:
        delta=0.0
    else:
        last=str(samples[-1])
        second_to_last=str(samples[-2])
        delta=float(last)-float(second_to_last)
    return delta
        
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