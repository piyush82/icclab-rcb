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
    Udr, PriceCdr,Tenant
from django.http import HttpResponseRedirect
import sys,os
from django.core import urlresolvers
from django.forms import widgets
import datetime
from datetime import date
from django.forms.widgets import RadioSelect
import socket
import struct
import json
from django.contrib.admin.options import ModelAdmin
from os_api import keystone_api
from common.pdf_generator import generate_pdf
from sympy.core import sympify
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
from dateutil.relativedelta import *
pic_path=os.path.join(os.path.dirname( __file__ ), '..', 'static')
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
dir_path=os.path.join(os.path.dirname( __file__ ), '..',)
config = {}
execfile(dir_path+"/config.conf", config) 

class stackUserAdmin(admin.ModelAdmin):
    fields = ['user_id', 'user_name','tenant_id']
    list_display = ('user_id', 'user_name','tenant_id')
    actions = ['add_pricing_func','calculate_price','start_periodic','stop_periodic','generate_bill']  
    
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
                        
            resources_choice=tuple()
            li=[]
            for i in range(len(resources)):
                li.append((resources[i],resources[i]))
            resources_choice=tuple(li)            
                
            if 'add_pricing' in request.POST:
                form = self.AddPricingFuncForm(request.POST)
                if form.is_valid():
                    var=form.cleaned_data['func']
                    var2=" ".join(var.split())
                    var2=var2.replace(" ", "")
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
                    for i in request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                        selected=int(str(i))
                    form=self.AddPricingFuncForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                    context={'user': queryset,'pricing_func_form': form,'meter_list':meters,'resources':resources,'selected':selected}
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
                        to_date=str(form3.cleaned_data["dateEnd"])
                        price,var=calculate_price_helper(from_date,to_date,meters_used,meter_list,user_id_stack,token_data,token_id,pricing_list,unit)

                    self.message_user(request, "Successfully calculated price.")

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
            except KeyError:
                messages.warning(request, "You have to authenticate first!")
                return redirect('/auth_token/?next=%s' % request.path)
            user=queryset[0]
        
                    
            if 'start_counter' in request.POST:
                form2 = self.StartPeriodicForm(request.POST)
                username=request.session['username']
                password=request.session['password']
                domain=request.session['domain']
                project=request.session['project']
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
                                user_id_stack=usr.user_id
                                user_id=usr.id

                                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                try:
                                    sock_addr=config["SOCKET_ADDR"]
                                    sock_port=config["PORT_SOCKET"]
                                    s.connect((sock_addr,sock_port))
                                except socket.error:
                                    print 'could not open socket'
                                    sys.exit(1)
                                s.sendall('periodic_start')
                                resp = s.recv(100)
                                if resp=="ok":
                                    print("Got ok, sending data.")
                                    lista=[username,password,domain,project,user_id,time_f,from_date,from_time,end_date,end_time,user_id_stack,None]
                                    for i in lista:
                                        msg=str(i)
                                        msg = struct.pack('>I', len(msg)) + msg
                                        s.sendall(msg)
                                    print("Done sending data")
                                    resp2 = s.recv(200)
                                    self.message_user(request, resp2)
                                s.close()
                                print("Closing client socket.")
                            except PricingFunc.DoesNotExist:
                                    messages.warning(request, 'You have to define the pricing function first.')   


            if not form2:
                user=queryset[0]
                usr=StackUser.objects.get(user_id=user)
                user_id=usr.id
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock_addr=config["SOCKET_ADDR"]
                    sock_port=config["PORT_SOCKET"]
                    s.connect((sock_addr,sock_port))
                except socket.error:
                    print 'could not open socket'                
                s.sendall('check threads')
                response = s.recv(100)
                if response=="ok":
                    thread_name="thread"+str(user_id)
                    print (thread_name)
                    s.sendall(thread_name)
                    response=s.recv(100)
                    s.close()
                    if response=="True":
                        messages.warning(request, "Periodic counter already started for this user.") 
                        return HttpResponseRedirect('/admin/main_menu/stackuser/')                        
                    else:  
                        for i in request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                            selected=int(str(i)) 
                        form2=self.StartPeriodicForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                        context={'user': queryset,'periodic_form': form2,'selected':selected}
                        return render(request,'admin/periodic.html',context)       
                

    start_periodic.short_description = "Start the periodic counter for the selected user"


    class StopPeriodicThread(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    
    def stop_periodic(self, request, queryset):
        if len(queryset)>1:
            messages.warning(request, "You can only select one user at a time!") 
            return HttpResponseRedirect('/admin/main_menu/stackuser/')
             
        else:
            user=queryset[0]
            user_id=user.id
            form5 = None
            try:
                token_data=request.session["token_data"] 
                token_id=token_data["token_id"]    
            except KeyError:
                messages.warning(request, "You have to authenticate first!")
                return redirect('/auth_token/?next=%s' % request.path)
            user=queryset[0]
        
                    
            if 'stop_counter' in request.POST:
                form5 = self.StopPeriodicThread(request.POST)
                if form5.is_valid():
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        try:
                            sock_addr=config["SOCKET_ADDR"]
                            sock_port=config["PORT_SOCKET"]
                            s.connect((sock_addr,sock_port))
                        except socket.error:
                            print 'Could not open socket' 
                        s.sendall('periodic_stop')
                        resp = s.recv(100)
                        if resp=="ok":
                            thread_name="thread"+str(user_id)
                            s.sendall(thread_name)
                            resp=s.recv(1000)
                            self.message_user(request, resp)
            if not form5:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock_addr=config["SOCKET_ADDR"]
                    sock_port=config["PORT_SOCKET"]
                    s.connect((sock_addr,sock_port))
                except socket.error:
                    print 'could not open socket'                
                s.sendall('check threads')
                response = s.recv(100)
                if response=="ok":
                    thread_name="thread"+str(user_id)
                    print (thread_name)
                    s.sendall(thread_name)
                    response=s.recv(100)
                    s.close()
                    if response=="False":
                        messages.warning(request, "Periodic counter hasn't been  started for this user.") 
                        return HttpResponseRedirect('/admin/main_menu/stackuser/') 
                    else:
                        form5=self.StopPeriodicThread(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                        context={'user': queryset,'stop_form': form5}
                        return render(request,'admin/stop_periodic.html',context)       
                

    stop_periodic.short_description = "Stop the periodic counter for the selected user"


    class CreateBillForm(forms.Form):
        dateStart=forms.DateField( input_formats=['%Y-%m-%d'])
        dateEnd=forms.DateField( input_formats=['%Y-%m-%d'])
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput) 

    def generate_bill(self, request, queryset):
        if len(queryset)>1:
            messages.warning(request, "You can only select one user at a time!") 
            return HttpResponseRedirect('/admin/main_menu/stackuser/')
             
        else:
            user=queryset[0]
            user_id=user.id
            form7 = None
            try:
                token_data=request.session["token_data"] 
                token_id=token_data["token_id"]    
            except KeyError:
                messages.warning(request, "You have to authenticate first!")
                return redirect('/auth_token/?next=%s' % request.path)
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
                
                now = datetime.datetime.now()
                prefix = '%d-%d-%d-' % (now.year, now.month, now.day)
                userid = 'piyush'
                logo = pic_path+'/icclab1.png'
                company_name = 'InIT Cloud Computing Lab'
                one_month_ago = datetime.datetime.now() - relativedelta(months=1)
                ######### This is how the dictionary is to be created, all entries are self explanatory
                data = {}
                data['prefix'] = prefix
                data['userid'] = usr.user_name
                data['logo'] = logo
                data['company'] = company_name
                data['company-address-1'] = 'Obere Kirchgasse 2'
                data['company-address-2'] = '8400, Winterthur, Switzerland'
                data['user-name'] = usr.user_name
                data['user-address-1'] = 'Team-IAMP, Technikumstrasse 9'
                data['user-address-2'] = '8400 Winterthur, Switzerland'
                data['notes'] = 'As a public service to our research and student community, currently we do not charge you for using our cloud facilities. This arrangement may change in the future.'
                data['due-date'] = str(datetime.date.today() + datetime.timedelta(20)) 
                data['currency']=func.currency
                data['unit']=func.unit
                data['itemized-data'] = {}
                dat_len=0
                for i in range(len(pricing_list)):
                    if pricing_list[i]:                      
                        if periodic.is_number(pricing_list[i])==False and pricing_list[i] not in ["+","-","/","*","%"]: 
                            data['itemized-data'][dat_len]={}
                            data['itemized-data'][dat_len]['name']=pricing_list[i]
                            dat_len+=1
               
                if 'bill' in request.POST:
                    HttpResponseRedirect('/admin/main_menu/stackuser/')
                    form7 = self.CreateBillForm(request.POST)
                    if form7.is_valid():                                          
                        from_date=str(form7.cleaned_data["dateStart"])
                        to_date=str(form7.cleaned_data["dateEnd"])
                        data['bill-start'] = datetime.datetime.strftime(datetime.datetime.strptime(from_date,'%Y-%m-%d'),'%d.%m.%Y')
                        data['bill-end'] = datetime.datetime.strftime(datetime.datetime.strptime(to_date,'%Y-%m-%d'),'%d.%m.%Y')
                        cdrs=PriceCdr.objects.filter(timestamp__range=(from_date, to_date))
                        print cdrs
                        bill_total=0
                        data_value=[None]*dat_len
                        data_value2=[]
                        all_values=[]
                        total=[]*len(pricing_list)
                        count=0
                        if cdrs:
                            for i in cdrs:
                                bill_total+=i.price
                            udrs=Udr.objects.filter(timestamp__range=(from_date,to_date))
                            for i in range(len(pricing_list)):
                                if pricing_list[i]:
                                    if periodic.is_number(pricing_list[i])==False and pricing_list[i] not in ["+","-","/","*","%"]:
                                        data_value[count]=0
                                        for j in udrs:
                                            if pricing_list[i]==func.param1:
                                                data_value[count]+=float(j.param1)
                                            elif pricing_list[i]==func.param2:
                                                data_value[count]+=float(j.param2)
                                            elif pricing_list[i]==func.param3:
                                                data_value[count]+=float(j.param3)
                                            elif pricing_list[i]==func.param4:
                                                data_value[count]+=float(j.param4)
                                            elif pricing_list[i]==func.param5:
                                                data_value[count]+=float(j.param5)
                                            data['itemized-data'][count]['value']=data_value[count]
                                        count+=1
                                    
                        else:
                            status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"]) 
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
                            list_helper=list(pricing_list)
                            price,modified_list=calculate_price_helper(from_date,to_date,meters_used,meter_list,user_id_stack,token_data,token_id,pricing_list,unit)
                            count=0
                            pricing_list=list_helper
                            for i in range(len(pricing_list)):
                                if pricing_list[i]:
                                    if periodic.is_number(pricing_list[i])==False and pricing_list[i] not in ["+","-","/","*","%"]:
                                        data_value2.append(modified_list[i])
                            i=0
                            while i<dat_len:
                                data['itemized-data'][i]['value']=data_value2[i]
                                i+=1
                            bill_total=price
                            data_value=list(data_value2)
                            
                        count2=0
                        k=0
                        data_price=[]
                        for i in range(len(pricing_list)):
                            if (pricing_list[i]) and pricing_list[i+1]!=None:
                                if periodic.is_number(pricing_list[i+1])==True:
                                    #for j in range(len(data_value)):
                                            if pricing_list[i]=="+":
                                                data_price.append(data_value[k]+float(pricing_list[i+1]))
                                            if pricing_list[i]=="-": 
                                                    data_price.append(data_value[k]-float(pricing_list[i+1]))
                                            if pricing_list[i]=="*":
                                                data_price.append(data_value[k]*float(pricing_list[i+1]))
                                            if pricing_list[i]=="/":
                                                if data_value[i+2]!=0:
                                                    data_price.append(data_value[k]/float(pricing_list[i+1]))
                                            if pricing_list[i]=="%":
                                                data_price.append(data_value[k]*float(pricing_list[i+1])/100.0)
                                            k+=1
                        i=0
                        while i<dat_len:
                            data['itemized-data'][i]['price']=data_price[i]  
                            i+=1           
                        data['amount-due']=bill_total  
                        file_path=generate_pdf(data) 
                        file_name=data['prefix'] + data['userid'] + '.pdf'
                        response = HttpResponse(FileWrapper(open(file_path)), content_type='application/pdf')
                        response['Content-Disposition'] = 'inline; filename='+file_name
                        return response

                if not form7:
                    for i in request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                        selected=int(str(i))
                    form7=self.AddQueryForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                    context={'user': queryset,'query_form': form7, 'selected':selected}
                    return render(request,'admin/bill.html',context)   

            
                                            
            except PricingFunc.DoesNotExist:
                messages.warning(request, 'You have to define the pricing function first.')
            
    generate_bill.short_description = "Generate the bill for the specific user."    
     

class pricingFuncAdmin(admin.ModelAdmin):
    fields = ['user_id', 'param1','sign1', 'param2','sign2', 'param3','sign3', 'param4','sign4', 'param5','currency','unit']
    list_display = ('user_id', 'param1','sign1', 'param2','sign2', 'param3','sign3', 'param4','sign4', 'param5','currency','unit')
    actions = ['change_pricing_func']
    
    
class tenantAdmin(admin.ModelAdmin):
    fields=['tenant_id','tenant_name']
    list_display=('tenant_id','tenant_name')    
    actions = ['list_users']
    
    def get_list_display(self, request):
        """
        Return a sequence containing the fields to be displayed on the
        changelist.
        """
         
        try:
            token_data=request.session["token_data"] 
            token_id=token_data["token_id"]   
            auth_uri=config["AUTH_URI"]
            status,tenant_list=keystone_api.get_list_tenants(token_id,auth_uri)  
            for i in range(len(tenant_list)):
                try:
                    ten=Tenant.objects.get(tenant_id=tenant_list[i]["tenant_id"])
                except Tenant.DoesNotExist:
                    tenant=Tenant(tenant_id=tenant_list[i]["tenant_id"],tenant_name=tenant_list[i]["tenant_name"])
                    tenant.save()
        except KeyError:
            messages.warning(request, "You have to authenticate first!")  
            return redirect('/auth_token/?next=%s' % request.path)  
        return self.list_display 
    
    class ListUsersForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)   



    def list_users(self, request, queryset):
        if len(queryset)>1:
            messages.warning(request, "You can only select one tenant at a time!") 
            return HttpResponseRedirect('/admin/main_menu/tenant/')
             
        else:  
            try:
                token_data=request.session["token_data"] 
                token_id=token_data["token_id"]
                var=str(queryset[0]).split(" ")
                tenant=var[0]
                user_ids=[]
                user_names=[]
                form6=None
                if 'user_status' in request.POST:
                    form6 = self.ListUsersForm(request.POST)
                    user=request.POST["user"]
                    pricing_func_status,periodic_thread_status,stack_user_status=show_user_status(request)
                    if stack_user_status==True:
                        context={'tenant': tenant,'user':user,'pricing_func_status':pricing_func_status,'periodic_thread_status':periodic_thread_status,'users_form':form6}
                        return render(request,'admin/user_status.html',context)  
                    else:
                        messages.warning(request, "User has not been added to the database!")
                        return HttpResponseRedirect('/admin/main_menu/stackuser/add/' )
                if 'user_status_start_periodic' in request.POST:
                    form6 = self.ListUsersForm(request.POST)
                    user=request.POST["user"]
                    stack_user_object=stackUserAdmin(StackUser,admin)
                    for i in request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                            selected=int(str(i))
                    form2=stack_user_object.StartPeriodicForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                    context={'user': [user],'periodic_form': form2,'selected':selected}
                    return render(request,'admin/periodic_tenant.html',context)
                
                if 'start_counter' in request.POST:
                    user=request.POST["user"]
                    username=request.session['username']
                    password=request.session['password']
                    domain=request.session['domain']
                    project=request.session['project']
                    stack_user_object=stackUserAdmin(StackUser,admin)
                    form2 = stack_user_object.StartPeriodicForm(request.POST)
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
                                     
                                    usr=StackUser.objects.get(user_id=user)
                                    user_id_stack=usr.user_id
                                    user_id=usr.id
                                    func=PricingFunc.objects.get(user_id=user_id)
                                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    try:
                                        sock_addr=config["SOCKET_ADDR"]
                                        sock_port=config["PORT_SOCKET"]
                                        s.connect((sock_addr,sock_port))
                                    except socket.error:
                                        print 'could not open socket'
                                        sys.exit(1)
                                    s.sendall('periodic_start')
                                    resp = s.recv(100)
                                    if resp=="ok":
                                        print("Got ok, sending data.")
                                        lista=[username,password,domain,project,user_id,time_f,from_date,from_time,end_date,end_time,user_id_stack,None]
                                        for i in lista:
                                            msg=str(i)
                                            msg = struct.pack('>I', len(msg)) + msg
                                            s.sendall(msg)
                                        print("Done sending data")
                                        resp2 = s.recv(200)
                                        self.message_user(request, resp2)
                                    s.close()
                                    print("Closing client socket.")
                                except PricingFunc.DoesNotExist:
                                    messages.warning(request, 'You have to define the pricing function first.')     
                    
                if 'user_status_define_pricing' in request.POST:
                    stack_user_object=stackUserAdmin(StackUser,admin)
                    form6 = self.ListUsersForm(request.POST)
                    user=request.POST["user"]
                    usr=StackUser.objects.get(user_id=user)   
                    resources=[]
                    status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])
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
                    resources_choice=tuple()
                    li=[]
                    for i in range(len(resources)):
                        li.append((resources[i],resources[i]))
                    resources_choice=tuple(li)    
                    for i in request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                        selected=int(str(i))           
                    form=stack_user_object.AddPricingFuncForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                    context={'user': [user],'pricing_func_form': form,'meter_list':meters,'resources':resources,'selected':selected}
                    return render(request,'admin/price_tenant.html',context)
                
                if 'user_status_stop_periodic' in request.POST:
                    form6 = self.ListUsersForm(request.POST)
                    user=request.POST["user"]
                    usr=StackUser.objects.get(user_id=user)
                    user_id=usr.id
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        sock_addr=config["SOCKET_ADDR"]
                        sock_port=config["PORT_SOCKET"]
                        s.connect((sock_addr,sock_port))
                    except socket.error:
                        print 'Could not open socket' 
                    s.sendall('periodic_stop')
                    resp = s.recv(100)
                    if resp=="ok":
                        thread_name="thread"+str(user_id)
                        s.sendall(thread_name)
                        resp=s.recv(1000)
                        self.message_user(request, resp)
                        
                if 'add_pricing' in request.POST:
                    form6 = self.ListUsersForm(request.POST)
                    user=request.POST["user"]
                    usr=StackUser.objects.get(user_id=user)
                    user_id=usr.id
                    resources=[]
                    status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])
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
                    resources_choice=tuple()
                    li=[]
                    for i in range(len(resources)):
                        li.append((resources[i],resources[i]))
                    resources_choice=tuple(li) 
                    stack_user_object=stackUserAdmin(StackUser,admin)
                    form = stack_user_object.AddPricingFuncForm(request.POST)
                    if form.is_valid():
                        var=form.cleaned_data['func']
                        var2=" ".join(var.split())
                        var2=var2.replace(" ", "")
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
                            func=PricingFunc(user_id=usr,param1=pricing_f[0],sign1=pricing_f[1],param2=pricing_f[2],sign2=pricing_f[3],param3=pricing_f[4],sign3=pricing_f[5],param4=pricing_f[6],sign4=pricing_f[7],param5=pricing_f[8],currency=curr,unit=unit)
                            func.save()            
                            self.message_user(request, "Successfully added pricing function to the user and meter ")
                        else:
                            messages.error(request, "Error. Poorly defined pricing function!")
                
                    return HttpResponseRedirect(request.get_full_path())
                
                if not form6:
                    form6=self.ListUsersForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                    status,user_list=keystone_api.get_users_per_tenant(token_id,'http://160.85.4.64:5000',str(tenant))  
                    for i in range(len(user_list)):
                        user_ids.append(user_list[i]["user_id"])
                        user_names.append(user_list[i]["user_name"])
                    context={'tenant': tenant,'user_ids':user_ids,'user_names':user_names,'users_form':form6}
                    return render(request,'admin/list_users.html',context)  
            except KeyError:
                messages.warning(request, "You have to authenticate first!")
                return redirect('/auth_token/?next=%s' % request.path)  



admin.site.register(StackUser,stackUserAdmin)
admin.site.register(PricingFunc,pricingFuncAdmin)
admin.site.register(Tenant,tenantAdmin)        


def parse(f):
    rez=[]  
    x=f    
    for i in f:
        for j in  ["+","-","*","/","%"]:
            if i==j:
                m=x.split(j,1)  
                x=m[1]     
                rez.append(m[0])
                rez.append(j)
    rez.append(m[1])
    return rez


def show_user_status(request):
    pricing_func_status=True
    periodic_thread_status=True
    stack_user_status=True
    try:
        user=request.POST["user"]
        usr=StackUser.objects.get(user_id=user)
        user_id=usr.id
        func=PricingFunc.objects.get(user_id=user_id)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock_addr=config["SOCKET_ADDR"]
            sock_port=config["PORT_SOCKET"]
            s.connect((sock_addr,sock_port))
        except socket.error:
            print 'Could not open socket'                
        s.sendall('check threads')
        response = s.recv(100)
        if response=="ok":
            thread_name="thread"+str(user_id)
            print (thread_name)
            s.sendall(thread_name)
            response=s.recv(100)
            s.close()
            if response=="True":
                periodic_thread_status=True                        
            else:   
                periodic_thread_status=False
    except PricingFunc.DoesNotExist:
        pricing_func_status=False
    except StackUser.DoesNotExist:
        stack_user_status=False
    return pricing_func_status,periodic_thread_status,stack_user_status

def calculate_price_helper(from_date,to_date,meters_used,meter_list,user_id_stack,token_data,token_id,pricing_list,unit):
    from_time="00:00:00"
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
        print pricing_list

    for i in range(len(pricing_list)):
        if pricing_list[i]==None:
            pricing_list[i]=0
    price=0.0 
    str_expr=""
    for i in range(len(pricing_list)):
        if i!=None:
            str_expr+=str(pricing_list[i])
        else:
            break
    print(str_expr)
    expr=sympify(str_expr)   
    price=expr.evalf()
                                
    price=price*unit
    return price,pricing_list


