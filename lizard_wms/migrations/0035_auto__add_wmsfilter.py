# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WMSFilter'
        db.create_table('lizard_wms_wmsfilter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('cql_filter', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')(default=1000)),
            ('display', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('lizard_wms', ['WMSFilter'])


    def backwards(self, orm):
        # Deleting model 'WMSFilter'
        db.delete_table('lizard_wms_wmsfilter')


    models = {
        'lizard_maptree.category': {
            'Meta': {'ordering': "('index', 'name')", 'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20'})
        },
        'lizard_security.dataset': {
            'Meta': {'ordering': "['name']", 'object_name': 'DataSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
        },
        'lizard_wms.featureline': {
            'Meta': {'ordering': "(u'order_using', u'description', u'name')", 'object_name': 'FeatureLine'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_hover': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order_using': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'render_as': ('django.db.models.fields.CharField', [], {'default': "u'T'", 'max_length': '1'}),
            'use_as_id': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'wms_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_wms.WMSSource']"})
        },
        'lizard_wms.filterpage': {
            'Meta': {'ordering': "(u'wms_source',)", 'object_name': 'FilterPage'},
            'available_filters': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['lizard_wms.FeatureLine']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'wms_source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'filter_pages'", 'to': "orm['lizard_wms.WMSSource']"})
        },
        'lizard_wms.wmsconnection': {
            'Meta': {'object_name': 'WMSConnection'},
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'default': 'u\'{"buffer": 0, "isBaseLayer": false, "opacity": 0.5}\''}),
            'params': ('django.db.models.fields.TextField', [], {'default': 'u\'{"height": "256", "width": "256", "styles": "", "format": "image/png", "tiled": "true", "transparent": "true"}\''}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'default': "u'1.3.0'", 'max_length': '20'}),
            'xml': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'})
        },
        'lizard_wms.wmsfilter': {
            'Meta': {'ordering': "(u'index',)", 'object_name': 'WMSFilter'},
            'cql_filter': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'lizard_wms.wmssource': {
            'Meta': {'ordering': "(u'index', u'display_name')", 'object_name': 'WMSSource'},
            '_params': ('jsonfield.fields.JSONField', [], {'default': 'u\'{"height": "256", "width": "256", "styles": "", "format": "image/png", "tiled": "true", "transparent": "true"}\'', 'null': 'True', 'blank': 'True'}),
            'bbox': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_wms.WMSConnection']", 'null': 'True', 'blank': 'True'}),
            'data_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_security.DataSet']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'enable_search': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'get_feature_type': ('django.db.models.fields.CharField', [], {'default': "u'gml'", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'layer_name': ('django.db.models.fields.TextField', [], {}),
            'legend_url': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'show_legend': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'timepositions': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['lizard_wms']