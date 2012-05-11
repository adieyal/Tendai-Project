from django.contrib.gis.db import models
from django.dispatch import receiver
from openrosa.signals import on_submission
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D 
import fuzzywuzzy.process

@receiver(on_submission)
def create_new_facility(sender, submission, **kwargs):
    if not submission: return
    if submission.form.name == "Facility Form":
        create_facility_from_facility_submission(submission)
    if submission.form.name == "Medicines Form":
        create_facility_from_medicine_submission(submission)

class SubmissionCoordinateFactory(object):
    @staticmethod 
    def parse(coordinates):
        c = coordinates.split()
        return Coordinates(float(c[0]), float(c[1]))
    
class Coordinates(object):
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    @property
    def latitude(self):
        return self.lat

    @property
    def longitude(self):
        return self.lng

    def __str__(self):
        return "[Coordinates] %s %s" % (self.latitude, self.longitude)

def point_medicines_form_to_facility(mq_submission):
    from devices.models import FacilitySubmission
    content = mq_submission.content

    coordinates = Coordinates(content.section_general.gps)

    point = Point(coordinates.longitude, coordinates.latitude, srid=4326)
    point.transform(900913)

    mq_facility_name = content.section_general.facility_name
    mq_submission_id = mq_submission.id
    mq_submitter = mq_submission.submissionworkerdevice.community_worker
    mq_date = mq_submission.created_date

    nb_facilities = Facility.objects.filter(point__distance_lt=(point, D(m=500)))
    if nb_facilities.count() == 1:
        nb_facility = nb_facilities[0]
        nb_facility_name = nb_facility.name
        nb_facility_id = nb_facility.id
        nb_submission = nb_facility.facilitysubmission_set.all()[0].submission
        nb_submission_id = nb_submission.id
        nb_swd = nb_submission.submissionworkerdevice
        nb_submitter = nb_swd.community_worker
        nb_swd_id = nb_swd.id
        nb_date = nb_submission.created_date

        _, score = fuzzywuzzy.process.extract(mq_facility_name, [nb_facility.name])[0]
        if score < 80:
            print """
    MQ Name: %(mq_facility_name)s
    MQ Submission ID: %(mq_submission_id)s
    MQ Submitter: %(mq_submitter)s
    MQ Date: %(mq_date)s
    NB Facility: %(nb_facility_name)s ID: %(nb_facility_id)s
    NB Submission ID: %(nb_submission_id)s
    NB SWD ID: %(nb_swd_id)s
    NB Submitter: %(nb_submitter)s
    NB Date: %(nb_date)s
    """ % locals()
            print ""
            
            #if nearby_facility.distance.m <= 50:
    

def create_facility_from_medicine_submission(submission):
    from devices.models import FacilitySubmission
    content = submission.content
    coordinates = content.section_general.gps

    name = content.section_general.facility_name

    lat, lng, _, _ = coordinates.split()
    point = Point(float(lng), float(lat), srid=4326)
    point.transform(900913)

    facility = Facility(
        name=name,
        longitude=float(lng),
        latitude=float(lat),
        point=point,
    )
    facility.save()
    
    
    FacilitySubmission.objects.create(
        submission=submission,
        facility=facility
    )
    
    return facility


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
    point.transform(900913)

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
    #point = models.PointField(help_text="Represented as (longitude, latitude)")
    point = models.PointField(help_text="Represented as (longitude, latitude)", srid=900913, null=True)
    objects = models.GeoManager()
    
    @classmethod
    def from_location(cls, location, name=None):
        point = Point(float(location[1]), float(location[0]), srid=4326)
        nearby = cls.objects.filter(point__distance_lt=(point, D(m=100)))
        if nearby.count() == 0:
            raise ValueError('No nearby facilities found.')
        if nearby.count() == 1:
            return nearby[0]
        if not name:
            raise ValueError('More than one facility nearby and no name provided.')
        match = fuzzywuzzy.process.extractOne(name, [facility.name for facility in nearby])
        if not match:
            raise ValueError('More than one facility nearby and no match for name found.')
        facility, score = match
        if score < 80:
            raise ValueError('More than one facility nearby and no close name match found.')
        return cls.objects.filter(name=facility)[0]
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Facilities"
