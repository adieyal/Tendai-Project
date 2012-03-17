from django.contrib.gis import admin
from olwidget.admin import GeoModelAdmin
import models

class FacilityAdmin(GeoModelAdmin):
    list_display = ['name', 'community_monitor', 'registered', 'country']

    def community_monitor(self, obj):
        try:
            return obj.facilitysubmission_set.all()[0].submission.submissionworkerdevice_set.all()[0].community_worker
        except:
            pass

    def registered(self, obj):
        try:
            return obj.facilitysubmission_set.all()[0].submission.start_time
        except:
            pass

    def country(self, obj):
        try:
            return obj.facilitysubmission_set.all()[0].submission.submissionworkerdevice_set.all()[0].community_worker.country
        except:
            pass

admin.site.register(models.Facility, FacilityAdmin)
