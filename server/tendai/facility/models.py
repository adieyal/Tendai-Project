from django.contrib.gis.db import models
from django.dispatch import receiver
from openrosa.signals import on_submission
from django.contrib.gis.geos import Point

@receiver(on_submission)
def create_new_facility(sender, submission, **kwargs):
    if not submission: return
    if submission.form.name == "Facility Form":
        create_facility_from_facility_submission(submission)

def create_facility_from_facility_submission(submission):
    from devices.models import FacilitySubmission
    content = submission.content
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
    point = Point(float(lng), float(lat), srid=4326)

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
        point=point,
    )
    facility.save()

            
    FacilitySubmission.objects.create(
        submission=submission,
        facility=facility
    )

    return facility

 
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
    point = models.PointField(help_text="Represented as (longitude, latitude)")
    #point = models.PointField(help_text="Represented as (longitude, latitude)", srid=900913)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Facilities"
