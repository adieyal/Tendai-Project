# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'CountryForm', fields ['country', 'form']
        db.delete_unique('devices_countryform', ['country_id', 'form_id'])

        # Deleting field 'CountryForm.country'
        db.delete_column('devices_countryform', 'country_id')

        # Adding M2M table for field countries on 'CountryForm'
        db.create_table('devices_countryform_countries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('countryform', models.ForeignKey(orm['devices.countryform'], null=False)),
            ('country', models.ForeignKey(orm['devices.country'], null=False))
        ))
        db.create_unique('devices_countryform_countries', ['countryform_id', 'country_id'])


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'CountryForm.country'
        raise RuntimeError("Cannot reverse this migration. 'CountryForm.country' and its values cannot be restored.")

        # Removing M2M table for field countries on 'CountryForm'
        db.delete_table('devices_countryform_countries')

        # Adding unique constraint on 'CountryForm', fields ['country', 'form']
        db.create_unique('devices_countryform', ['country_id', 'form_id'])


    models = {
        'devices.communityworker': {
            'Meta': {'object_name': 'CommunityWorker'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Country']", 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Organisation']"}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        'devices.country': {
            'Meta': {'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'devices.countryform': {
            'Meta': {'object_name': 'CountryForm'},
            'countries': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['devices.Country']", 'symmetrical': 'False'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openrosa.ORForm']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Language']"})
        },
        'devices.currency': {
            'Meta': {'object_name': 'Currency'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        'devices.device': {
            'Meta': {'object_name': 'Device'},
            'community_worker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.CommunityWorker']"}),
            'device_id': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'devices.district': {
            'Meta': {'object_name': 'District'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'devices.language': {
            'Meta': {'object_name': 'Language'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'devices.medicine': {
            'Meta': {'unique_together': "(('name', 'form'),)", 'object_name': 'Medicine'},
            'countries': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['devices.Country']", 'symmetrical': 'False'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.MedicineForm']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'recommended_pack_size': ('django.db.models.fields.IntegerField', [], {})
        },
        'devices.medicineform': {
            'Meta': {'object_name': 'MedicineForm'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'devices.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'devices.submissionworkerdevice': {
            'Meta': {'object_name': 'SubmissionWorkerDevice'},
            'community_worker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.CommunityWorker']", 'null': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Device']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openrosa.ORFormSubmission']", 'null': 'True'})
        },
        'openrosa.orform': {
            'Meta': {'unique_together': "(('name', 'form_id'),)", 'object_name': 'ORForm'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'form_id': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'majorminorversion': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
        }
    }

    complete_apps = ['devices']
