'''
Created on May 6, 2014

@author: kolv
'''
from django import forms


class UserQueryForm(forms.Form):
    dateStart=forms.DateField( input_formats=['%Y-%m-%d'])
    dateEnd=forms.DateField( input_formats=['%Y-%m-%d'])