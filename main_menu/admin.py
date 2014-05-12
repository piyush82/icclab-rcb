'''
Created on Apr 16, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@gmail.com
@organization: ICCLab, Zurich University of Applied Sciences
@summary: Custom admin module

 Copyright 2014 Zuercher Hochschule fuer Angewandte Wissenschaften
 All Rights Reserved.

    Licensed under the Apache License, Version 2.0 (the "License"); you may
    not use this file except in compliance with the License. You may obtain
    a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.

'''

from main_menu import admin_custom as admin
from main_menu.models import StackUser,PricingFunc, PriceLoop, MetersCounter,\
    Udr, PriceCdr
from django.http import HttpResponseRedirect
import sys,os
from django.core import urlresolvers
from django.forms import widgets
import datetime
from datetime import date
from django.forms.widgets import RadioSelect

from processes import periodic_web
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
import ceilometer_api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'processes')))
import periodic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf.urls import patterns
from django.shortcuts import render, redirect
import django.forms as forms
from django.shortcuts import render_to_response
from django.contrib import messages
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from main_menu.views import auth_token,is_auth
from time import gmtime, strftime
from threading import Timer



class stackUserAdmin(admin.ModelAdmin):
    fields = ['user_id', 'user_name','tenant_id']
    list_display = ('user_id', 'user_name','tenant_id')
    actions = ['add_pricing_func','calculate_price','start_periodic','stop_periodic']  
    
    class AddPricingFuncForm(forms.Form):
        CHOICES = (('EUR', 'EUR',), ('CHF', 'CHF',),('USD', 'USD',), ('GBP', 'GBP',))
        CHOICES2 = (('0.01', '0.01',), ('1', '1',))
        func=forms.CharField(required=True)
        currency = forms.ChoiceField(widget=forms.Select(),choices=CHOICES, required=True) 
        unit = forms.ChoiceField(widget=forms.Select(),choices=CHOICES2, required=True) 
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    

    def add_pricing_func(self, request, queryset):
        if len(queryset)>1:
            messages.warning(request, "You can only select one user at a time!") 
            return HttpResponseRedirect('/admin/main_menu/stackuser/')
             
        else:  
            try:
                token_data=request.session["token_data"] 
                token_id=token_data["token_id"]
                status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])      
            except KeyError:
                messages.warning(request, "You have to authenticate first!")
                return redirect('/auth_token/?next=%s' % request.path)

        
            form = None  
            resources=[]
            for i in range(len(meter_list)):
                resources.append(meter_list[i]["resource-id"])
            set_resources=set(resources)
            resources=list(set_resources)
            meters = [None]*len(resources)
            for i in range(len(resources)):
                meters[i]=[]
                for j in range(len(meter_list)):
                    if resources[i]==meter_list[j]["resource-id"]:
                   
                        meters[i].append(meter_list[j]['meter-name'])
                    
            if 'add_pricing' in request.POST:
                form = self.AddPricingFuncForm(request.POST)
                if form.is_valid():
                    var=form.cleaned_data['func']
                    var2=" ".join(var.split())
                    var2=var2.replace(" ", "")
                    #price_def=var2.split(" ")
                    price_def=parse(var2)
                    curr=form.cleaned_data['currency']
                    unit=form.cleaned_data['unit']
                    input_p=price_def[:]
                    if len(price_def)>9:
                        messages.error(request, "You can use only 5 parameters!")
                    else:
                        meters_used=[]
                        meters_ids=[]
            
                    for i in range(len(price_def)):
                        j=0
                        while j<len(meter_list):
                            if price_def[i]==meter_list[j]["meter-name"]:
                                meters_used.append(price_def[i])
                                meters_ids.append(meter_list[j]["meter-id"])
                                status_samples,sample_list=ceilometer_api.get_meter_samples(price_def[i],token_data["metering"],token_id,False,meter_list,False,'')
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
                            if periodic.is_number(price_def[i]):    
                                continue
                                  
                            else:
                                messages.warning(request, "Parameters should be valid meters and numbers!")  
                                status_ret=False
                        if i%2!=0:
                            if price_def[i] in ["+","-","*","/","%"]:
                                if periodic.is_number(price_def[i+1]):
                                    x=float(price_def[i+1])
                                    continue
                                else:
                                    messages.warning(request, "Parameters should be valid meters and numbers!")
                                    status_ret=False
                                    break
                                if price_def[i]=="+":
                                    continue
                                if price_def[i]=="-": 
                                    continue
                                if price_def[i]=="*":
                                    continue
                                if price_def[i]=="/":
                                    if x!=0:
                                        continue
                                    else:
                                        messages.error(request, "Division by zero!")
                                        status_ret=False
                                if price_def[i]=="%":
                                    continue
                            else:
                                messages.warning(request, 'You should use one of the following signs:"+","-","*","/","%"!')
                                status_ret=False
                        else:
                            continue
                    if status_ret==True:
                        pricing_f=[None]*9
                        for i in range(len(input_p)):
                            pricing_f[i]=input_p[i]
                        func=PricingFunc(user_id=queryset[0],param1=pricing_f[0],sign1=pricing_f[1],param2=pricing_f[2],sign2=pricing_f[3],param3=pricing_f[4],sign3=pricing_f[5],param4=pricing_f[6],sign4=pricing_f[7],param5=pricing_f[8],currency=curr,unit=unit)
                        func.save()            
                        self.message_user(request, "Successfully added pricing function to the user and meter ")
                    else:
                        messages.error(request, "Error. Poorly defined pricing function!")
                
                return HttpResponseRedirect(request.get_full_path())

            if not form:
                num_results = PricingFunc.objects.filter(user_id=queryset[0]).count()
                if num_results==0:
                    form=self.AddPricingFuncForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                    context={'user': queryset,'pricing_func_form': form,'meter_list':meters,'resources':resources}
                    return render(request,'admin/price.html',context)   
                else:
                    messages.warning(request, "Pricing function already defined for selected user. You can change it in main_menu->pricing func!") 
    add_pricing_func.short_description = "Specify a pricing function for the selected user."


    class AddQueryForm(forms.Form):
        dateStart=forms.DateField( input_formats=['%Y-%m-%d'])
        dateEnd=forms.DateField( input_formats=['%Y-%m-%d'])
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)  
        
    def calculate_price(self, request, queryset):
        if len(queryset)>1:
            messages.warning(request, "You can only select one user at a time!") 
            return HttpResponseRedirect('/admin/main_menu/stackuser/')
             
        else:
            try:
                token_data=request.session["token_data"] 
                token_id=token_data["token_id"]
                status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])      
            except KeyError:
                messages.warning(request, "You have to authenticate first!")
                return redirect('/auth_token/?next=%s' % request.path)
            form3=None
            flag=True
            user=queryset[0]
            try:
                func=PricingFunc.objects.get(user_id=user)
                usr=StackUser.objects.get(user_id=user)
                pricing_list=[]
                meters_used=[]
                pricing_list.append(func.param1)
                pricing_list.append(func.sign1)
                pricing_list.append(func.param2)
                pricing_list.append(func.sign2)
                pricing_list.append(func.param3)
                pricing_list.append(func.sign3)
                pricing_list.append(func.param4)
                pricing_list.append(func.sign4)
                pricing_list.append(func.param5)     

                unit=float(func.unit)
                currency=func.currency
                user_id_stack=usr.user_id
                
                
                for i in range(len(pricing_list)):
                    j=0
                    while j<len(meter_list):
                        if pricing_list[i]==meter_list[j]["meter-name"]:
                            if pricing_list[i] in meters_used:
                                continue
                            else:
                                meters_used.append(pricing_list[i])                                                                
                            break
                        else:
                            j=j+1
            except PricingFunc.DoesNotExist:
                messages.warning(request, 'You have to define the pricing function first.')
                flag=False
            if flag==True:  
                if 'calculate' in request.POST:
                    form3 = self.AddQueryForm(request.POST)
                    if form3.is_valid():                                          
                        from_date=str(form3.cleaned_data["dateStart"])
                        from_time="00:00:00"
                        to_date=str(form3.cleaned_data["dateEnd"])
                        to_time="23:59:59"
                        all_stats=[] 
                        time_period=0
                        total=[None]*len(meters_used)
                        for i in range(len(meters_used)):
                            total[i]=0
                            for j in range(len(meter_list)):
                                if meters_used[i]==meter_list[j]["meter-name"]:
                                    resource_id=meter_list[j]["resource-id"]
                                    q=ceilometer_api.set_query(from_date,to_date,from_time,to_time,resource_id,user_id_stack,True)
                                    status,stat_list=ceilometer_api.meter_statistics(meters_used[i], token_data["metering"],token_id,meter_list,True,q=q)
                                    if stat_list==[]:
                                        total[i]+=0
                                    else:
                                        if meter_list[j]["meter-type"]=="cumulative":
                                            total[i]+=stat_list[0]["max"]-stat_list[0]["min"]                                           
                                        if meter_list[j]["meter-type"]=="gauge":
                                            t1=datetime.datetime.combine(datetime.datetime.strptime(from_date,"%Y-%m-%d").date(),datetime.datetime.strptime(from_time,"%H:%M:%S").time())
                                            t2=datetime.datetime.combine(datetime.datetime.strptime(to_date,"%Y-%m-%d").date(),datetime.datetime.strptime(to_time,"%H:%M:%S").time())
                                            t=t2-t1
                                            time_period=t.total_seconds()
                                            total[i]+=stat_list[0]["average"]*time_period
                                        if meter_list[j]["meter-type"]=="delta":
                                            total[i]+=stat_list[0]["sum"]
                            all_stats.append(total[i])
                            for s in range(len(pricing_list)):
                                if(pricing_list[s]==meters_used[i]):
                                    pricing_list[s]=total[i]


                    for i in range(len(pricing_list)):
                        if pricing_list[i]==None:
                            pricing_list[i]=0
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
                                
                    price=price*unit
                
                    date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cdr=PriceCdr(user_id=user,timestamp=date_time,pricing_func_id=func, price=price)
                    cdr.save()
                    self.message_user(request, "Successfully calculated price.")
                    self.message_user(request, "period: %s" %(time_period))
                    context={'user': queryset,'price':price,'currency':currency}
                    return render(request,'admin/show_price.html',context) 

                if not form3:
                    for i in request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                        selected=int(str(i))
                    form3=self.AddQueryForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                    context={'user': queryset,'query_form': form3, 'selected':selected}
                    return render(request,'admin/query.html',context)   
            
        
    calculate_price.short_description = "Calculate the price for the specific user."
    



    class StartPeriodicForm(forms.Form):
        dateStart=forms.DateField( input_formats=['%Y-%m-%d'])
        time=forms.CharField(required=True)
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    
    def start_periodic(self, request, queryset):
        if len(queryset)>1:
            messages.warning(request, "You can only select one user at a time!") 
            return HttpResponseRedirect('/admin/main_menu/stackuser/')
             
        else:
            form2 = None
            try:
                token_data=request.session["token_data"] 
                token_id=token_data["token_id"]
                status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])      
            except KeyError:
                messages.warning(request, "You have to authenticate first!")
                return redirect('/auth_token/?next=%s' % request.path)
            user=queryset[0]
        
                    
            if 'start_counter' in request.POST:
                form2 = self.StartPeriodicForm(request.POST)
                if form2.is_valid():
                    from_date=str(form2.cleaned_data["dateStart"])
                    from_time='00:00:00'
                    time_f=str(form2.cleaned_data["time"])
                    today = datetime.date.today()
                    today.strftime("%Y-%m-%d")
                    now = datetime.datetime.now()
                    now=datetime.time(now.hour, now.minute, now.second)
                    now.strftime("%H:%M:%S")
                    time_f=float(time_f)
                    end_date=str(today)
                    end_time=str(now)
                    if periodic.is_number(time_f):
                        if  time_f>0:
                            try:
                                func=PricingFunc.objects.get(user_id=user) 
                                usr=StackUser.objects.get(user_id=user)
                                
                                pricing_list=[]
                                meters_used=[]
                                pricing_list.append(func.param1)
                                pricing_list.append(func.sign1)
                                pricing_list.append(func.param2)
                                pricing_list.append(func.sign2)
                                pricing_list.append(func.param3)
                                pricing_list.append(func.sign3)
                                pricing_list.append(func.param4)
                                pricing_list.append(func.sign4)
                                pricing_list.append(func.param5)     
            
                                user_id_stack=usr.user_id
            
                                for i in range(len(pricing_list)):
                                    j=0
                                    while j<len(meter_list):
                                        if pricing_list[i]==meter_list[j]["meter-name"]:
                                            if pricing_list[i] in meters_used:
                                                continue
                                            else:
                                                meters_used.append(pricing_list[i])                                                                
                                            break
                                        else:
                                            j=j+1
                                k_self=self
                                request.session["thread_running"] = True
                                global thread1
                                thread1=periodic_web.MyThread(k_self,token_data,token_id,meters_used,meter_list,func,user,time_f,from_date,from_time,end_date,end_time,user_id_stack)
                                thread1.start()
                            except PricingFunc.DoesNotExist:
                                    messages.warning(request, 'You have to define the pricing function first.')   


            if not form2:
                form2=self.StartPeriodicForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                context={'user': queryset,'periodic_form': form2}
                return render(request,'admin/periodic.html',context)       
                

    start_periodic.short_description = "Start the periodic counter for the selected user"


    class StopPeriodicThread(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    
    def stop_periodic(self, request, queryset):
        if len(queryset)>1:
            messages.warning(request, "You can only select one user at a time!") 
            return HttpResponseRedirect('/admin/main_menu/stackuser/')
             
        else:
            form5 = None
            try:
                token_data=request.session["token_data"] 
                token_id=token_data["token_id"]
                status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])      
            except KeyError:
                messages.warning(request, "You have to authenticate first!")
                return redirect('/auth_token/?next=%s' % request.path)
            user=queryset[0]
        
                    
            if 'stop_counter' in request.POST:
                form5 = self.StopPeriodicThread(request.POST)
                if form5.is_valid():
                    try:
                        thread_running=request.session["thread_running"] 
                        global thread1
                        if thread1.isAlive():
                            thread1.cancel()
                    except KeyError:
                        messages.warning(request, "Counter hasn't been started!")
                        return redirect('/auth_token/?next=%s' % request.path)


            if not form5:
                form5=self.StopPeriodicThread(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                context={'user': queryset,'stop_form': form5}
                return render(request,'admin/stop_periodic.html',context)       
                

    stop_periodic.short_description = "Stop the periodic counter for the selected user"

     
        

class pricingFuncAdmin(admin.ModelAdmin):
    fields = ['user_id', 'param1','sign1', 'param2','sign2', 'param3','sign3', 'param4','sign4', 'param5']
    list_display = ('user_id', 'param1','sign1', 'param2','sign2', 'param3','sign3', 'param4','sign4', 'param5')
    actions = ['change_pricing_func']


admin.site.register(StackUser,stackUserAdmin)
admin.site.register(PricingFunc,pricingFuncAdmin)
        


def parse(f):
    rez=[]  
    x=f    
    for i in f:
        for j in  ["+","-","*","/","%"]:
            if i==j:
                m=x.split(j)  
                x=m[1]     
                rez.append(m[0])
                rez.append(j)
    rez.append(m[1])
    return rez



