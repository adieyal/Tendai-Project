# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ORForm'
        db.create_table('openrosa_orform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('form_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('majorminorversion', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('modified_data', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('openrosa', ['ORForm'])

        # Adding model 'ORFormSubmission'
        db.create_table('openrosa_orformsubmission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openrosa.ORForm'], null=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('device_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('subscriber_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('sim_id', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('openrosa', ['ORFormSubmission'])

        # Adding model 'ORSubmissionMedia'
        db.create_table('openrosa_orsubmissionmedia', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openrosa.ORFormSubmission'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('openrosa', ['ORSubmissionMedia'])


    def backwards(self, orm):
        
        # Deleting model 'ORForm'
        db.delete_table('openrosa_orform')

        # Deleting model 'ORFormSubmission'
        db.delete_table('openrosa_orformsubmission')

        # Deleting model 'ORSubmissionMedia'
        db.delete_table('openrosa_orsubmissionmedia')


    models = {
        'openrosa.orform': {
            'Meta': {'object_name': 'ORForm'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'form_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'majorminorversion': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'modified_data': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'openrosa.orformsubmission': {
            'Meta': {'object_name': 'ORFormSubmission'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openrosa.ORForm']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sim_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'subscriber_id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'})
        },
        'openrosa.orsubmissionmedia': {
            'Meta': {'object_name': 'ORSubmissionMedia'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openrosa.ORFormSubmission']"})
        }
    }

    complete_apps = ['openrosa']
