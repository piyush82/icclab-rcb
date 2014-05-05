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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
import ceilometer_api
import compute_api
import keystone_api



def index(request):
    return render_to_response('index.html',{},
            context_instance=RequestContext(request))
    
@login_required    
def demo(request):
    #return HttpResponseRedirect('//')
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
    return render_to_response('user_page.html',
        {'is_auth':request.user.is_authenticated()},
        context_instance=RequestContext(request))
    
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
                return HttpResponseRedirect('/token_data/')
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

