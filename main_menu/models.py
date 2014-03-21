from django.db import models

class MetersCounter(models.Model):
    meter_id= models.TextField()
    meter_name = models.CharField(max_length=30)
    user_id = models.TextField()
    resource_id = models.TextField()
    counter_volume = models.TextField()
    unit = models.TextField()
    timestamp = models.DateTimeField()
    tenant_id = models.TextField()

class Users(models.Model):
    user_id = models.TextField()
    tenant_id = models.TextField()

class PriceLoop(models.Model):
    price = models.FloatField()
    timestamp = models.DateTimeField()
    tenant_id = models.TextField()
    
class PricingFunc(models.Model):
    user_id = models.ForeignKey(Users)
    param1 = models.TextField()
    sign1 = models.CharField(max_length=5)
    param2 = models.TextField()
    sign2 = models.CharField(max_length=5)
    param3 = models.TextField()
    sign3 = models.CharField(max_length=5)
    param4 = models.TextField()
    sign4 = models.CharField(max_length=5)
    param5 = models.TextField()
    
class Udr(models.Model):
    user_id = models.ForeignKey(Users)
    timestamp = models.DateTimeField()
    pricing_func_id = models.ForeignKey(PricingFunc)
    param1 = models.TextField()
    param2 = models.TextField()
    param3 = models.TextField()
    param4 = models.TextField()
    param5 = models.TextField()  
    
class PriceCdr(models.Model):
    price = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField() 
    tenant_id = models.TextField() 
    pricing_func_id = models.ForeignKey(PricingFunc)
    
class PriceDaily(models.Model):
    price = models.FloatField(blank=True, null=True) 
    timestamp = models.DateTimeField() 
    tenant_id = models.TextField() 
    pricing_func_id = models.ForeignKey(PricingFunc)    
