'''
Created on Apr 16, 2014

@author: kolv

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
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
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


site.register(User, UserAdmin)



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