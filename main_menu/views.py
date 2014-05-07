from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from main_menu.models import StackUser
import sys
import os
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
        #user_id_stack=usr.user_id
                
                
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
                q=ceilometer_api.set_query(from_date,to_date,from_time,to_time,"/",user,True) 
                all_stats=[]           
                for i in meters_used:
                    status,stat_list=ceilometer_api.meter_statistics(i, token_data["metering"],token_data['token_id'],meter_list,True,q=q)
                    all_stats.append(stat_list)
                        
                k=0
                for i in range(len(pricing_list)):
                    j=0
                    while j<len(meter_list):
                        if pricing_list[i]==meter_list[j]["meter-name"]:
                            if all_stats[k]==[]:
                                pricing_list[i]=0
                            else:
                                pricing_list[i]=all_stats[k][0]['sum']
                            k+=1
                        else:
                            j=j+1 
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
            context={'user': user,'price':price,'currency':currency}
            return render(request,'user_show_price.html',context) 

        if not form:
            form=forms.UserQueryForm()
            context={'user': user,'query_form': form }
            return render(request,'user_query.html',context)   
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
            auth_uri = 'http://160.85.4.10:5000'
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
        return HttpResponseRedirect('/admin/')
    except KeyError:
        if request.method == 'POST':
            username=request.POST['user']
            password=request.POST['pass']
            domain=request.POST['domain']
            project=request.POST['project']
            auth_uri = 'http://160.85.4.10:5000'
            status, token_data = keystone_api.get_token_v3(auth_uri,True,username=username, password=password, domain=domain,project=project)
            request.session["status"] = status
            request.session["token_data"] = token_data
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

