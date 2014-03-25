from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from main_menu.models import StackUser
import sys
import os
from django.http.response import HttpResponseRedirect
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
import ceilometer_api
import compute_api
import keystone_api

@login_required
def index(request):
    return render_to_response('index.html',{},
            context_instance=RequestContext(request))

@login_required
def admin_page(request):
    users_list=StackUser.objects.all()
    #return render_to_response('admin_page.html',
    #    {'is_auth':request.user.is_authenticated()},
    #    context_instance=RequestContext(request))
    context={'users_list':users_list}
    return render(request,'admin_page.html',
         # {'is_auth':request.user.is_authenticated()},
          context)
    #    context_instance=RequestContext(request))

@login_required
def user_page(request):
    return render_to_response('user_page.html',
        {'is_auth':request.user.is_authenticated()},
        context_instance=RequestContext(request))
    
@login_required
def auth_token(request):
    if request.method == 'POST':
        #username=None
        #password=None

        #if request.user.is_authenticated():
            #username = request.user.username   
        #if request.user.is_authenticated():
            #password = request.user.password
        username=request.POST['user']
        password=request.POST['pass']
        domain=request.POST['domain']
        project=request.POST['project']
        auth_uri = 'http://160.85.4.10:5000'
        status, token_data = keystone_api.get_token_v3(auth_uri,username, password, domain,project)
        request.session["status"] = status
        request.session["token_data"] = token_data
        return HttpResponseRedirect('/token_data/')
    return render(request,'auth_token.html')

@login_required
def token_data(request):

    status=request.session["status"]
    token_data=request.session["token_data"] 
    context={'status':status,'token_data':token_data}
    return render(request,'token_data.html',context)
    
    
@login_required
def define_pricing(request,ct):
    token_data=request.session["token_data"] 
    token_id=token_data.token_id
    status_pricing, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])
    request.session["status_pricing"] = status_pricing
    request.session["meter_list"] = meter_list
    context={'status':status_pricing,'meter_list':meter_list}
    return render(request,'define_pricing.html',context)   
