# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Facility.distance_to_town'
        db.add_column('facility_facility', 'distance_to_town', self.gf('django.db.models.fields.PositiveIntegerField')(null=True), keep_default=False)

        # Adding field 'Facility.closest_town'
        db.add_column('facility_facility', 'closest_town', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True), keep_default=False)

        # Adding field 'Facility.population_coverage'
        db.add_column('facility_facility', 'population_coverage', self.gf('django.db.models.fields.PositiveIntegerField')(null=True), keep_default=False)

        # Adding field 'Facility.daily_patients'
        db.add_column('facility_facility', 'daily_patients', self.gf('django.db.models.fields.PositiveIntegerField')(null=True), keep_default=False)

        # Adding field 'Facility.nurses'
        db.add_column('facility_facility', 'nurses', self.gf('django.db.models.fields.PositiveIntegerField')(null=True), keep_default=False)

        # Adding field 'Facility.doctors'
        db.add_column('facility_facility', 'doctors', self.gf('django.db.models.fields.PositiveIntegerField')(null=True), keep_default=False)

        # Changing field 'Facility.point'
        db.alter_column('facility_facility', 'point', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=900913, null=True))


    def backwards(self, orm):
        
        # Deleting field 'Facility.distance_to_town'
        db.delete_column('facility_facility', 'distance_to_town')

        # Deleting field 'Facility.closest_town'
        db.delete_column('facility_facility', 'closest_town')

        # Deleting field 'Facility.population_coverage'
        db.delete_column('facility_facility', 'population_coverage')

        # Deleting field 'Facility.daily_patients'
        db.delete_column('facility_facility', 'daily_patients')

        # Deleting field 'Facility.nurses'
        db.delete_column('facility_facility', 'nurses')

        # Deleting field 'Facility.doctors'
        db.delete_column('facility_facility', 'doctors')

        # Changing field 'Facility.point'
        db.alter_column('facility_facility', 'point', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True))


    models = {
        'facility.facility': {
            'Meta': {'object_name': 'Facility'},
            'closest_town': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'daily_patients': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'distance_to_town': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'doctors': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'facility_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'facility_type_other': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nurses': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '900913', 'null': 'True'}),
            'population_coverage': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'postal_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['facility']
