'''
Created on Apr 16, 2014

@author: kolv
'''

from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.admin.options import ModelAdmin, HORIZONTAL, VERTICAL
from django.contrib.admin.options import StackedInline, TabularInline
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.filters import (ListFilter, SimpleListFilter,
    FieldListFilter, BooleanFieldListFilter, RelatedFieldListFilter,
    ChoicesFieldListFilter, DateFieldListFilter, AllValuesFieldListFilter)
import os 
import copy
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule 
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

site = AdminSite()

site.index_template=BASE_DIR+"/templates/admin/index.html"


def autodiscover():
    """
    Autodiscover function from django.contrib.admin
    """

 
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
 
        try:
            before_import_registry = copy.copy(site._registry)
            import_module('%s.admin' % app)
        except:
            site._registry = before_import_registry
            if module_has_submodule(mod, 'admin'):
                raise