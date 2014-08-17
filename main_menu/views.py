'''
Created on Apr 16, 2014

@author:  Tea Kolevska
@contact: tea.kolevska@gmail.com
@organization: ICCLab, Zurich University of Applied Sciences
@summary: App views

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

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from main_menu.models import StackUser, PriceCdr
import sys
import os
import datetime
from django.http.response import HttpResponseRedirect
from django.contrib import messages
from web_ui import settings
from processes import periodic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
import ceilometer_api
import compute_api
import keystone_api
from main_menu.models import StackUser,PricingFunc
from main_menu import forms
dir_path=os.path.join(os.path.dirname( __file__ ), '..',)
config = {}
execfile(dir_path+"/config.conf", config) 

def index(request):
    return render_to_response('index.html',{},
            context_instance=RequestContext(request))


    
@login_required    
def demo(request):
    return render_to_response('demo.html',{},
            context_instance=RequestContext(request))

@login_required
def admin_page(request):
    try:
        status=request.session["status"]
        token_data=request.session["token_data"] 
        return HttpResponseRedirect('/admin/')
    except KeyError:
        messages.warning(request, "You have to authenticate first!")
        return HttpResponseRedirect('/auth_token/')
 
@login_required
def user_page(request):
    try:
        status=request.session["status"]
        token_data=request.session["token_data"] 
        return render(request,'user_page.html')
    except KeyError:
        messages.warning(request, "You have to authenticate first!")
        return HttpResponseRedirect('/auth_token_user/')
    
@login_required
def user_page_calculate_price(request):
    try:
        status=request.session["status"]
        token_data=request.session["token_data"] 
        status_meter_list, meter_list = ceilometer_api.get_meter_list(token_data['token_id'], token_data["metering"])
        form=None
        flag=True
        user=token_data['user-id']
    except KeyError:
        messages.warning(request, "You have to authenticate first!")
        return redirect('/auth_token_user/')
    try:
        usr=StackUser.objects.get(user_id=user)
        func=PricingFunc.objects.get(user_id=usr.id)
        
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
    except StackUser.DoesNotExist:
        messages.warning(request, 'You still have not been added to the system. Contact your admin!.')
        flag=False
    if flag==True:  
        if 'calculate' in request.POST:
            form = forms.UserQueryForm(request.POST)
            if form.is_valid():                                          
                from_date=str(form.cleaned_data["dateStart"])
                from_time="00:00:00"
                to_date=str(form.cleaned_data["dateEnd"])
                to_time="23:59:59"
            price=pricing(meters_used,meter_list,from_date,to_date,from_time,to_time,user,token_data,token_data['token_id'],pricing_list,unit)
            context={'user': user,'price':price,'currency':currency}
            return render(request,'user_show_price.html',context) 

        if not form:
            form=forms.UserQueryForm()
            context={'user': user,'query_form': form }
            return render(request,'user_query.html',context)   
    return HttpResponseRedirect('/user/')

@login_required
def user_page_periodic_price(request):
    try:
        status=request.session["status"]
        token_data=request.session["token_data"] 
        status_meter_list, meter_list = ceilometer_api.get_meter_list(token_data['token_id'], token_data["metering"])
        form=None
        flag=True
        user=token_data['user-id']
    except KeyError:
        messages.warning(request, "You have to authenticate first!")
        return redirect('/auth_token_user/')
    try:
        prices=[]
        times=[]
        usr=StackUser.objects.get(user_id=user)
        cdrs=PriceCdr.objects.filter(user_id=usr.id)
        cdrs=cdrs.order_by('timestamp').reverse()[:10]
        for i in cdrs:
            prices.append(i.price)
            times.append(i.timestamp)   
        context={'user': user,'prices':prices,'times':times}
        return render(request,'user_show_periodic.html',context)         
    except PriceCdr.DoesNotExist:
        messages.warning(request, 'No records for that user.')
        flag=False
    except StackUser.DoesNotExist:
        messages.warning(request, 'You still have not been added to the system. Contact your admin!.')
        flag=False
    return HttpResponseRedirect('/user/')

@login_required
def auth_token_user(request):
    try:
        status=request.session["status"]
        token_data=request.session["token_data"] 
        return HttpResponseRedirect('/user/')
    except KeyError:
        if request.method == 'POST':
            username=request.POST['user']
            password=request.POST['pass']
            domain=request.POST['domain']
            project=request.POST['project']
            auth_uri = config["AUTH_URI"]
            status, token_data = keystone_api.get_token_v3(auth_uri,True,username=username, password=password, domain=domain,project=project)
            request.session["status"] = status
            request.session["token_data"] = token_data
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            else:
                return HttpResponseRedirect('/user/')
                    
        return render(request,'auth_token_user.html')

    
@login_required
def auth_token(request):
    try:
        status=request.session["status"]
        token_data=request.session["token_data"] 
        if status==True:
            return HttpResponseRedirect('/admin/')
        else:
            if request.method == 'POST':
                username=request.POST['user']
                password=request.POST['pass']
                domain=request.POST['domain']
                project=request.POST['project']
                auth_uri = config["AUTH_URI"]
                status, token_data = keystone_api.get_token_v3(auth_uri,True,username=username, password=password, domain=domain,project=project)
                request.session["status"] = status
                request.session["token_data"] = token_data
                request.session['username']=username
                request.session['password']=password
                request.session['domain']=domain
                request.session['project']=project
                return HttpResponseRedirect('/admin/')
            else:
                messages.warning(request, "Unsuccessful authentication!")
                return render(request,'auth_token.html')
    except KeyError:
        if request.method == 'POST':
            username=request.POST['user']
            password=request.POST['pass']
            domain=request.POST['domain']
            project=request.POST['project']
            auth_uri = config["AUTH_URI"]
            status, token_data = keystone_api.get_token_v3(auth_uri,True,username=username, password=password, domain=domain,project=project)
            request.session["status"] = status
            request.session["token_data"] = token_data
            request.session['username']=username
            request.session['password']=password
            request.session['domain']=domain
            request.session['project']=project
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            else:
                if settings.GLOBAL_SETTINGS['PRO_DEBUG']==True:
                    return HttpResponseRedirect('/token_data/')
                else:
                    return HttpResponseRedirect('/admin/')
                    
        return render(request,'auth_token.html')

@login_required
def token_data(request):
    try:
        status=request.session["status"]
        token_data=request.session["token_data"] 
        context={'status':status,'token_data':token_data}
        return render(request,'token_data.html',context)
    except KeyError:
        messages.warning(request, "You have to authenticate first!")
        return HttpResponseRedirect('/auth_token/')
    
    
@login_required
def define_pricing(request,ct):
    token_data=request.session["token_data"] 
    token_id=token_data.token_id
    status_pricing, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])
    request.session["status_pricing"] = status_pricing
    request.session["meter_list"] = meter_list
    context={'status':status_pricing,'meter_list':meter_list}
    return render(request,'define_pricing.html',context)   


@login_required
def is_auth(request):
    if 'status' not in request.session:
        return False
    else:
        return True


def pricing(meters_used,meter_list,from_date,to_date,from_time,to_time,user_id_stack,token_data,token_id,pricing_list,unit):
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
    return price




