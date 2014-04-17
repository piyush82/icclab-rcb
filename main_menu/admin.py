#from django.contrib import admin
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

class stackUserAdmin(admin.ModelAdmin):
    fields = ['user_id', 'user_name','tenant_id']
    list_display = ('user_id', 'user_name','tenant_id')
    actions = ['add_pricing_func','calculate_price','start_periodic','soberi_func']
    


    
    
    class AddPricingFuncForm(forms.Form):
        func=forms.CharField(required=True)
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    
    def add_pricing_func(self, request, queryset):
        #if is_auth(request)==False:
        #        HttpResponseRedirect('/auth_token/')
        form = None
        token_data=request.session["token_data"] 
        token_id=token_data["token_id"]
        status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])      
        
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
                price_def=form.cleaned_data['func'].split(" ")
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
                            status_samples,sample_list=ceilometer_api.get_meter_samples(price_def[i],token_data["metering"],token_id,False,meter_list,False)
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
                            messages.error(request, "Parameters should be valid meters and numbers!")  
                            status_ret=False
                    if i%2!=0:
                        if price_def[i] in ["+","-","*","/","%"]:
                            if periodic.is_number(price_def[i+1]):
                                x=float(price_def[i+1])
                                continue
                            else:
                                messages.error(request, "Parameters should be valid meters and numbers!")
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
                            messages.error(request, 'You should use one of the following signs:"+","-","*","/","%"!')
                            status_ret=False
                    else:
                        continue
                if status_ret==True:
                    pricing_f=[None]*9
                    for i in range(len(input_p)):
                        pricing_f[i]=input_p[i]
                    func=PricingFunc(user_id=queryset[0],param1=pricing_f[0],sign1=pricing_f[1],param2=pricing_f[2],sign2=pricing_f[3],param3=pricing_f[4],sign3=pricing_f[5],param4=pricing_f[6],sign4=pricing_f[7],param5=pricing_f[8] )
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



    class SoberiForm(forms.Form):
        dateStart=forms.DateField( input_formats=['%d-%m-%Y'], initial=date.today)
        timeStart=forms.TimeField(input_formats=['%H:%M:%S'])
        dateEnd=forms.DateField( input_formats=['%d-%m-%Y'], initial=date.today)
        timeEnd=forms.TimeField(input_formats=['%H:%M:%S'])
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)    
        
    def soberi_func(self, request, queryset):
        forma = None
        token_data=request.session["token_data"] 
        token_id=token_data["token_id"]
        status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])      
       
        user=queryset[0]
        
                    
        if 'soberi' in request.POST:
            forma = self.SoberiForm(request.POST)
            if forma.is_valid():
                        try:
                            func=PricingFunc.objects.get(user_id=user) 
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
                            from_date=str(forma.cleaned_data["dateStart"])
                            from_time=str(forma.cleaned_data["timeStart"])
                            to_date=str(forma.cleaned_data["dateEnd"])
                            to_time=str(forma.cleaned_data["timeEnd"])
                            #ceilometer_api.set_query(from_date,to_date,from_time,to_time,"/","/",True)            
                            udr=get_udr(self,token_data,token_id,user,meters_used,meter_list,func,False)
                            price=pricing(self,user)
                            self.message_user(request, "Successfully calculated price.")
                            context={'user': queryset,'price':price}
                            return render(request,'admin/show_price.html',context)    
                        except PricingFunc.DoesNotExist:
                                messages.warning(request, 'You have to define the pricing function first.')   


        if not forma:
                for i in request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                        selected=int(str(i))
                forma=self.SoberiForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                context={'user': queryset,'soberi_form': forma, 'selected':selected}
                return render(request,'admin/soberi.html',context)       
                

    soberi_func.short_description = "Get price."
  
    class AddQueryForm(forms.Form):
        query_choice = (('yes', 'Yes',), ('no', 'No',))
        radio = forms.ChoiceField(required = True, widget=RadioSelect(), choices=query_choice)
        dateStart=forms.DateField( input_formats=['%d-%m-%Y'], initial=date.today)
        timeStart=forms.TimeField(input_formats=['%H:%M:%S'])
        dateEnd=forms.DateField( input_formats=['%d-%m-%Y'], initial=date.today)
        timeEnd=forms.TimeField(input_formats=['%H:%M:%S'])
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)  
        
    def calculate_price(self, request, queryset):
        token_data=request.session["token_data"] 
        token_id=token_data["token_id"]
        form3=None
        status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])
        flag=True
        user=queryset[0]
        try:
            func=PricingFunc.objects.get(user_id=user)
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
                    if request.POST["radio"]=="yes":                      
                        from_date=str(form3.cleaned_data["dateStart"])
                        from_time=str(form3.cleaned_data["timeStart"])
                        to_date=str(form3.cleaned_data["dateEnd"])
                        to_time=str(form3.cleaned_data["timeEnd"])
                        q=ceilometer_api.set_query(from_date,to_date,from_time,to_time,"/","/",True)            
                        udr=get_udr(self,token_data,token_id,user,meters_used,meter_list,func,True,q)
                    else:
                        udr=get_udr(self,token_data,token_id,user,meters_used,meter_list,func,False,"")
                    price=pricing(self,user)
                    self.message_user(request, "Successfully calculated price.")
                    context={'user': queryset,'price':price}
                    return render(request,'admin/show_price.html',context) 
                return HttpResponseRedirect(request.get_full_path())
            if not form3:
                for i in request.POST.getlist(admin.ACTION_CHECKBOX_NAME):
                        selected=int(str(i))
                form3=self.AddQueryForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                context={'user': queryset,'query_form': form3, 'selected':selected}
                return render(request,'admin/query.html',context)   
            
        
    calculate_price.short_description = "Calculate the price for the specific user."
    



    class StartPeriodicForm(forms.Form):
        time=forms.CharField(required=True)
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)

    
    def start_periodic(self, request, queryset):
        form2 = None
        token_data=request.session["token_data"] 
        token_id=token_data["token_id"]
        status_meter_list, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])      
       
        user=queryset[0]
        
                    
        if 'start_counter' in request.POST:
            form2 = self.StartPeriodicForm(request.POST)
            if form2.is_valid():
                time=str(form2.cleaned_data["time"])
                if periodic.is_number(time):
                    if  time>0:
                        try:
                            func=PricingFunc.objects.get(user_id=user) 
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
                            periodic_counter(self,token_data,token_id,meters_used,meter_list,func,user,time)
                                
                        except PricingFunc.DoesNotExist:
                                messages.warning(request, 'You have to define the pricing function first.')   


        if not form2:
                form2=self.StartPeriodicForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
                context={'user': queryset,'periodic_form': form2}
                return render(request,'admin/periodic.html',context)       
                

    start_periodic.short_description = "Start the periodic counter for the selected user"
  
        

class pricingFuncAdmin(admin.ModelAdmin):
    fields = ['user_id', 'param1','sign1', 'param2','sign2', 'param3','sign3', 'param4','sign4', 'param5']
    list_display = ('user_id', 'param1','sign1', 'param2','sign2', 'param3','sign3', 'param4','sign4', 'param5')
    actions = ['change_pricing_func']


admin.site.register(StackUser,stackUserAdmin)
admin.site.register(PricingFunc,pricingFuncAdmin)


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
    for i in range(len(meters_used)):
        rez=0.0
        status,sample_list=ceilometer_api.get_meter_samples(meters_used[i],token_data["metering"],token_id,False,meter_list,web_bool,q)
        for k in range(len(sample_list)):
            rez+=sample_list[k]["counter-volume"]
            meters_counter=MetersCounter(meter_name=meters_used[i],user_id=user,counter_volume=rez,unit=sample_list[k]["counter-unit"],timestamp=date_time)
            meters_counter.save() 
        delta=get_delta_samples(self,token_data,token_id,user,meters_used[i])
        delta_list[i]=delta
        udr=Udr(user_id=user,timestamp=date_time,pricing_func_id=func, param1=delta_list[0], param2=delta_list[1], param3=delta_list[2], param4=delta_list[3], param5=delta_list[4])
        udr.save()        
    return udr
        

def periodic_counter(self,token_data,token_id,meters_used,meter_list,func,user,time):
    udr=get_udr(self,token_data,token_id,user,meters_used,meter_list,func,False)
    price=pricing(self,user)
    t = Timer(float(time),periodic_counter,args=[token_data,token_id,meters_used,meter_list,func,user,time])
    t.start()
    
    
def pricing(self,user):
    func=PricingFunc.objects.get(user_id=user)
    udr=Udr.objects.filter(user_id=user,pricing_func_id=func).order_by('-id')[0]
    #udr.reverse()[:1]
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


