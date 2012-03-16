from django.contrib.gis.db import models

class Facility(models.Model):
    name = models.CharField(max_length=50)
    longitude = models.FloatField()
    latitude = models.FloatField()

    district = models.CharField(max_length=50, null=True, blank=True)
    postal_address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)

    facility_type = models.CharField(max_length=50, null=True, blank=True)
    facility_type_other = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    # GeoDjango-specific: a geometry field (MultiPolygonField), and
    # overriding the default manager with a GeoManager instance.
    point = models.PointField(help_text="Represented as (longitude, latitude)", null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Facilities"
