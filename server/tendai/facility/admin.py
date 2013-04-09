from django.contrib.gis import admin
from olwidget.admin import GeoModelAdmin
import models
from facility.management.commands.merge_facilities import Command as MergeCommand


class FacilityAdmin(GeoModelAdmin):
    options = {
            'layers': ['ve.hybrid'],
            'overlayStyle': {
                'fillColor': '#ffff00',
                'strokeWidth': 5,
            },
            'defaultLon': -72,
            'defaultLat': 44,
            'defaultZoom': 4,
            'mapOptions' : {
                'displayProjection' : 'EPSG:900913'
            }
        }

    def merge_facilities(self, request, queryset):
        """
        Merge all the facilities in the queryset into one
        """
        merged = deleted = 0
        command = MergeCommand()
        num_facilities = queryset.count()
        if queryset.count() > 1:
            first = queryset[0] 
            for facility in queryset:
                if facility == first: continue
                (m, d) = command.merge_facilities(facility, first)
                merged += m
                deleted += d
            
            self.message_user(request, "Successfully merged %d facilities and moved %d submissions" % (num_facilities, merged))
        else:
            self.message_user(request, "Expected at least two facilities to merge")

    list_display = ['name', 'community_monitor', 'registered', 'country']
    actions = ['merge_facilities']
    merge_facilities.short_description = "Merge selected facilities"

    def community_monitor(self, obj):
        try:
            return obj.facilitysubmission_set.all()[0].submission.submissionworkerdevice.community_worker
        except:
            pass

    def registered(self, obj):
        try:
            return obj.facilitysubmission_set.all()[0].submission.start_time
        except:
            pass

    def country(self, obj):
        try:
            return obj.facilitysubmission_set.all()[0].submission.submissionworkerdevice.community_worker.country
        except:
            pass

admin.site.register(models.Facility, FacilityAdmin)
