# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MenuItem'
        db.create_table('website_menuitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.MenuItem'], null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Page'], null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('website', ['MenuItem'])

        # Adding model 'Template'
        db.create_table('website_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('website', ['Template'])

        # Adding model 'Page'
        db.create_table('website_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['website.Template'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('website', ['Page'])

        # Adding model 'Story'
        db.create_table('website_story', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openrosa.ORFormSubmission'])),
            ('heading', self.gf('django.db.models.fields.TextField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('photo', self.gf('django.db.models.fields.FilePathField')(path='/var/www/tendai.medicinesinfohub.net/server/tendai/media/openrosa/submissions/images', max_length=100, recursive=True, match='.*\\.jpg')),
            ('monitor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.CommunityWorker'])),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Country'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('website', ['Story'])


    def backwards(self, orm):
        
        # Deleting model 'MenuItem'
        db.delete_table('website_menuitem')

        # Deleting model 'Template'
        db.delete_table('website_template')

        # Deleting model 'Page'
        db.delete_table('website_page')

        # Deleting model 'Story'
        db.delete_table('website_story')


    models = {
        'devices.communityworker': {
            'Meta': {'object_name': 'CommunityWorker'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'monitors'", 'null': 'True', 'to': "orm['devices.Country']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Organisation']"}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        'devices.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Language']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'devices.language': {
            'Meta': {'object_name': 'Language'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'devices.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
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
        },
        'website.menuitem': {
            'Meta': {'object_name': 'MenuItem'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Page']", 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.MenuItem']", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'website.page': {
            'Meta': {'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['website.Template']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'website.story': {
            'Meta': {'object_name': 'Story'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Country']"}),
            'heading': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.CommunityWorker']"}),
            'photo': ('django.db.models.fields.FilePathField', [], {'path': "'/var/www/tendai.medicinesinfohub.net/server/tendai/media/openrosa/submissions/images'", 'max_length': '100', 'recursive': 'True', 'match': "'.*\\\\.jpg'"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openrosa.ORFormSubmission']"})
        },
        'website.template': {
            'Meta': {'object_name': 'Template'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['website']
