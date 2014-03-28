from django.contrib import admin
from main_menu.models import StackUser,PricingFunc
from django.http import HttpResponseRedirect
import sys,os
from django.core import urlresolvers
from django.forms import widgets
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'os_api')))
import ceilometer_api
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf.urls import patterns
from django.shortcuts import render
import django.forms as forms
from django.shortcuts import render_to_response
from django.contrib import messages

class stackUserAdmin(admin.ModelAdmin):
    fields = ['user_id', 'user_name','tenant_id']
    list_display = ('user_id', 'user_name','tenant_id')
    actions = ['add_pricing_func']
    #def add_pricing_func(self, request, queryset):
        #selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        #ct = ContentType.objects.get_for_model(queryset.model)
        #return HttpResponseRedirect("/define_pricing/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))
        #return HttpResponseRedirect("define_pricing/?ct=%s" %(ct.pk))
        #ct = ContentType.objects.get_for_model(queryset.model)
        #url = urlresolvers.reverse('mein_menu:define_pricing', kwargs={ 'ct': ct.id })
        #return HttpResponseRedirect(url)
    #add_pricing_func.short_description = "Specify a pricing function for the selected user."
    
 #   class ChoiceWidget(widgets.MultiWidget):
 #       def __init__(self, *args, **kwargs):
  #          choices = kwargs.pop("meter_choices")
 #           widget = (widgets.TextInput(),
  #                widgets.Select(choices=choices)
  #               )
 #           super(self.__class__, self).__init__(*args, **kwargs)
    
    class AddPricingFuncForm(forms.Form):
        def __init__(self, *args, **kwargs):
            choices = kwargs.pop("meter_choices")
            super(self.__class__, self).__init__(*args, **kwargs)
            self.fields["meters"] = forms.CharField(widget=forms.Select(choices=choices))

        meters = forms.ChoiceField(widget=forms.Select(),choices=(), required=True)   
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        #meters=forms.ChoiceField(widget=forms.Select())
        CHOICES = (('+', '+',), ('-', '-',),('*', '*',), ('/', '/',), ('%', '%',))
        choice_field1 = forms.ChoiceField(widget=forms.Select(), choices=CHOICES,required=True)
        choice_field2 = forms.ChoiceField(widget=forms.Select(), choices=CHOICES,required=True)
        choice_field3 = forms.ChoiceField(widget=forms.Select(), choices=CHOICES,required=True)
        choice_field4 = forms.ChoiceField(widget=forms.Select(), choices=CHOICES,required=True)       
        
        #def clean(self):
         #   cleaned_data = super(self.__class__, self).clean()
         #   if (self.fields['meters'] in self.choices):
         #       cleaned_data.append(self.fields['meters'])
         #   return cleaned_data
                
        
        #pricing_func = forms.ModelChoiceField(PricingFunc.objects)
      
        
    
    def add_pricing_func(self, request, queryset):
        form = None
        token_data=request.session["token_data"] 
        token_id=token_data["token_id"]
        status_pricing, meter_list = ceilometer_api.get_meter_list(token_id, token_data["metering"])
        request.session["status_pricing"] = status_pricing
        
        
        METER_CHOICES=tuple()
        li=[]
        for i in range(len(meter_list)):
            li.append((meter_list[i]["meter-id"],meter_list[i]["meter-name"]))
        METER_CHOICES=tuple(li)
            
        if 'add_pricing' in request.POST:
            form = self.AddPricingFuncForm(request.POST,meter_choices=METER_CHOICES)
            #form.fields['meters']=forms.ChoiceField()
            if form.is_valid():
                pricing_func = form.cleaned_data['meters']
                self.message_user(request, "Successfully added pricing function to the user and meter %s" %(pricing_func))
                return HttpResponseRedirect(request.get_full_path())

        if not form:

            form=self.AddPricingFuncForm(meter_choices=METER_CHOICES,initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        context={'user': queryset,'pricing_func_form': form}
        return render(request,'admin/price.html',context)   
        #return render_to_response('admin/price.html', {'user': queryset,
                                                        #'pricing_func_form': form})
    add_pricing_func.short_description = "Specify a pricing function for the selected user."


admin.site.register(StackUser,stackUserAdmin)



