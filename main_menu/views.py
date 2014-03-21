from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from main_menu.models import Users

@login_required
def index(request):
    return render_to_response('index.html',{},
            context_instance=RequestContext(request))

@login_required
def admin_page(request):
    users_list=Users.objects.all()
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
