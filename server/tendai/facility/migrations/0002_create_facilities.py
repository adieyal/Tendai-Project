# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from facility.models import Facility
from devices.models import SubmissionWorkerDevice as SWD, FacilitySubmission
from django.contrib.gis.geos import Point, fromstr

class Migration(SchemaMigration):

    def forwards(self, orm):
        for s in SWD.objects.filter(submission__form__name="Facility Form"):
            content = s.submission.content
            coordinates = content.section_location.facility_location

            name = content.section_name.facility_name
            district = content.section_name.facility_district
            postal_address = content.section_contact.postal_address
            phone_number = content.section_contact.phone_number
            email = content.section_contact.email

            facility_type = getattr(content.section_general, "facility_type", "")
            facility_type_other = getattr(content.section_general, "facility_type_other", "")
            description = getattr(content.section_general, "facility_description", "")

            comments = getattr(content.section_comments, "comments", "")

            lat, lng, _, _ = coordinates.split()
            point = fromstr("POINT(%s %s)" % (lng, lat))
            print point
            facility = Facility(
                name=name,
                longitude=float(lng),
                latitude=float(lat),
                district=district,
                postal_address=postal_address,
                phone_number=phone_number,
                email=email,
                facility_type=facility_type,
                facility_type_other=facility_type_other,
                description=description,
                comments=comments,
                point=point
            )
            print facility.name
            facility.save()
            
            FacilitySubmission.objects.create(
                submission=s.submission,
                facility=facility
            )

    def backwards(self, orm):
        pass
        


    models = {
        'facility.facility': {
            'Meta': {'object_name': 'Facility'},
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'facility_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'facility_type_other': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'}),
            'postal_address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['facility']
