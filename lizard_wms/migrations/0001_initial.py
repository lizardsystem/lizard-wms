# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WMSSource'
        db.create_table('lizard_wms_wmssource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('lizard_wms', ['WMSSource'])

        # Adding M2M table for field category on 'WMSSource'
        db.create_table('lizard_wms_wmssource_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wmssource', models.ForeignKey(orm['lizard_wms.wmssource'], null=False)),
            ('category', models.ForeignKey(orm['lizard_maptree.category'], null=False))
        ))
        db.create_unique('lizard_wms_wmssource_category', ['wmssource_id', 'category_id'])


    def backwards(self, orm):
        
        # Deleting model 'WMSSource'
        db.delete_table('lizard_wms_wmssource')

        # Removing M2M table for field category on 'WMSSource'
        db.delete_table('lizard_wms_wmssource_category')


    models = {
        'lizard_maptree.category': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '20', 'db_index': 'True'})
        },
        'lizard_wms.wmssource': {
            'Meta': {'ordering': "('name',)", 'object_name': 'WMSSource'},
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['lizard_maptree.Category']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['lizard_wms']
