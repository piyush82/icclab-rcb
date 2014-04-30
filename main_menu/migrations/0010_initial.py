# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StackUser'
        db.create_table(u'main_menu_stackuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('user_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('tenant_id', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'main_menu', ['StackUser'])

        # Adding model 'MetersCounter'
        db.create_table(u'main_menu_meterscounter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meter_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_menu.StackUser'])),
            ('counter_volume', self.gf('django.db.models.fields.TextField')(default='0.0', null=True, blank=True)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'main_menu', ['MetersCounter'])

        # Adding model 'PriceLoop'
        db.create_table(u'main_menu_priceloop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('price', self.gf('django.db.models.fields.FloatField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('tenant_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_menu.StackUser'])),
        ))
        db.send_create_signal(u'main_menu', ['PriceLoop'])

        # Adding model 'PricingFunc'
        db.create_table(u'main_menu_pricingfunc', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_menu.StackUser'])),
            ('param1', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('sign1', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('param2', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('sign2', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('param3', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('sign3', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('param4', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('sign4', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('param5', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(default='CHF', max_length=200)),
            ('unit', self.gf('django.db.models.fields.CharField')(default='0.01', max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('main_menu', ['PricingFunc'])

        # Adding model 'Udr'
        db.create_table(u'main_menu_udr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_menu.StackUser'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('pricing_func_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_menu.PricingFunc'])),
            ('param1', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('param2', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('param3', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('param4', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('param5', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'main_menu', ['Udr'])

        # Adding model 'PriceCdr'
        db.create_table(u'main_menu_pricecdr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('price', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('user_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['main_menu.StackUser'])),
            ('pricing_func_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['main_menu.PricingFunc'])),
        ))
        db.send_create_signal(u'main_menu', ['PriceCdr'])

        # Adding model 'PriceDaily'
        db.create_table(u'main_menu_pricedaily', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('price', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('tenant_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_menu.StackUser'])),
            ('pricing_func_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main_menu.PricingFunc'])),
        ))
        db.send_create_signal(u'main_menu', ['PriceDaily'])


    def backwards(self, orm):
        # Deleting model 'StackUser'
        db.delete_table(u'main_menu_stackuser')

        # Deleting model 'MetersCounter'
        db.delete_table(u'main_menu_meterscounter')

        # Deleting model 'PriceLoop'
        db.delete_table(u'main_menu_priceloop')

        # Deleting model 'PricingFunc'
        db.delete_table(u'main_menu_pricingfunc')

        # Deleting model 'Udr'
        db.delete_table(u'main_menu_udr')

        # Deleting model 'PriceCdr'
        db.delete_table(u'main_menu_pricecdr')

        # Deleting model 'PriceDaily'
        db.delete_table(u'main_menu_pricedaily')


    models = {
        u'main_menu.meterscounter': {
            'Meta': {'object_name': 'MetersCounter'},
            'counter_volume': ('django.db.models.fields.TextField', [], {'default': "'0.0'", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meter_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main_menu.StackUser']"})
        },
        u'main_menu.pricecdr': {
            'Meta': {'object_name': 'PriceCdr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'pricing_func_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['main_menu.PricingFunc']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['main_menu.StackUser']"})
        },
        u'main_menu.pricedaily': {
            'Meta': {'object_name': 'PriceDaily'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'pricing_func_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_menu.PricingFunc']"}),
            'tenant_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main_menu.StackUser']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'main_menu.priceloop': {
            'Meta': {'object_name': 'PriceLoop'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {}),
            'tenant_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main_menu.StackUser']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'main_menu.pricingfunc': {
            'Meta': {'object_name': 'PricingFunc'},
            'currency': ('django.db.models.fields.CharField', [], {'default': "'CHF'", 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param1': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param3': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param4': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param5': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'sign1': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sign2': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sign3': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sign4': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'default': "'0.01'", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main_menu.StackUser']"})
        },
        u'main_menu.stackuser': {
            'Meta': {'object_name': 'StackUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tenant_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user_id': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'main_menu.udr': {
            'Meta': {'object_name': 'Udr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param1': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param3': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param4': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param5': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'pricing_func_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main_menu.PricingFunc']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main_menu.StackUser']"})
        }
    }

    complete_apps = ['main_menu']