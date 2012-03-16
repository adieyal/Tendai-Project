from django.contrib.gis import admin
from olwidget.admin import GeoModelAdmin
import models

class FacilityAdmin(GeoModelAdmin):
 list_display = ['name','point',]

admin.site.register(models.Facility, FacilityAdmin)
