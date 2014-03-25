from django.contrib import admin
from main_menu.models import StackUser
from django.http import HttpResponseRedirect

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse


class stackUserAdmin(admin.ModelAdmin):
    fields = ['user_id', 'user_name','tenant_id']
    list_display = ('user_id', 'user_name','tenant_id')
    actions = ['add_pricing_func']
    def add_pricing_func(self, request, queryset):
        #selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ct = ContentType.objects.get_for_model(queryset.model)
        #return HttpResponseRedirect("/define_pricing/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))
        #return HttpResponseRedirect("define_pricing/?ct=%s" %(ct.pk))
        url = reverse('define_pricing', kwargs={ 'pk': ct.pk })
        return HttpResponseRedirect(url)
    add_pricing_func.short_description = "Specify a pricing function for the selected user."

admin.site.register(StackUser,stackUserAdmin)