# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FeatureLine'
        db.create_table('lizard_wms_featureline', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wms_layer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lizard_wms.WMSSource'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('use_as_id', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('render_as', self.gf('django.db.models.fields.CharField')(default='T', max_length=1)),
            ('in_hover', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order_using', self.gf('django.db.models.fields.IntegerField')(default=1000)),
        ))
        db.send_create_signal('lizard_wms', ['FeatureLine'])


    def backwards(self, orm):
        
        # Deleting model 'FeatureLine'
        db.delete_table('lizard_wms_featureline')


    models = {
        'lizard_maptree.category': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20', 'db_index': 'True'})
        },
        'lizard_wms.featureline': {
            'Meta': {'object_name': 'FeatureLine'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_hover': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order_using': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'render_as': ('django.db.models.fields.CharField', [], {'default': "'T'", 'max_length': '1'}),
            'use_as_id': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'wms_layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_wms.WMSSource']"})
        },
        'lizard_wms.wmsconnection': {
            'Meta': {'object_name': 'WMSConnection'},
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'options': ('django.db.models.fields.TextField', [], {'default': '\'{"buffer": 0, "reproject": true, "isBaseLayer": false, "opacity": 0.5}\''}),
            'params': ('django.db.models.fields.TextField', [], {'default': '\'{"height": "256", "width": "256", "layers": "%s", "styles": "", "format": "image/png", "tiled": "true", "transparent": "true"}\''}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'default': "'1.3.0'", 'max_length': '20'})
        },
        'lizard_wms.wmssource': {
            'Meta': {'ordering': "('name',)", 'object_name': 'WMSSource'},
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_wms.WMSConnection']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'options': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['lizard_wms']
