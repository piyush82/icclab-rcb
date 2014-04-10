# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Udr.param5'
        db.alter_column(u'main_menu_udr', 'param5', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'Udr.param4'
        db.alter_column(u'main_menu_udr', 'param4', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'Udr.param3'
        db.alter_column(u'main_menu_udr', 'param3', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'Udr.param2'
        db.alter_column(u'main_menu_udr', 'param2', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'Udr.param1'
        db.alter_column(u'main_menu_udr', 'param1', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

    def backwards(self, orm):

        # Changing field 'Udr.param5'
        db.alter_column(u'main_menu_udr', 'param5', self.gf('django.db.models.fields.CharField')(default=0, max_length=200))

        # Changing field 'Udr.param4'
        db.alter_column(u'main_menu_udr', 'param4', self.gf('django.db.models.fields.CharField')(default=0, max_length=200))

        # Changing field 'Udr.param3'
        db.alter_column(u'main_menu_udr', 'param3', self.gf('django.db.models.fields.CharField')(default=0, max_length=200))

        # Changing field 'Udr.param2'
        db.alter_column(u'main_menu_udr', 'param2', self.gf('django.db.models.fields.CharField')(default=0, max_length=200))

        # Changing field 'Udr.param1'
        db.alter_column(u'main_menu_udr', 'param1', self.gf('django.db.models.fields.CharField')(default=0, max_length=200))

    models = {
        u'main_menu.meterscounter': {
            'Meta': {'object_name': 'MetersCounter'},
            'counter_volume': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meter_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['main_menu.StackUser']"})
        },
        u'main_menu.pricecdr': {
            'Meta': {'object_name': 'PriceCdr'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'pricing_func_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['main_menu.PricingFunc']"}),
            'tenant_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['main_menu.StackUser']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'param1': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param3': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param4': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'param5': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'sign1': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sign2': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sign3': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'sign4': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
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