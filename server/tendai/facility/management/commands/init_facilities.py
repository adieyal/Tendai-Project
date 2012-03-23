from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import translation
from facility import models as facilitymodels
from devices import models as devicemodels
from django.contrib.gis.measure import D 
from devices.models import SubmissionWorkerDevice as SWD

class Command(BaseCommand):
    def handle(self, *args, **options):
        facilities = facilitymodels.Facility.objects.all() 
        merged_count = deleted_count = 0

        with transaction.commit_on_success():
            for s in SWD.objects.filter(submission__form__name="Medicines Form"):
                facilitymodels.point_medicines_form_to_facility(s.submission)
            #for facility in facilities:
            #    point = facility.point
            #    for nearby_facility in facilitymodels.Facility.objects.filter(point__distance_lt=(point, D(m=50))):
            #        if facility == nearby_facility: continue
            #        #if nearby_facility.distance.m <= 50:
            #        _, score = fuzzywuzzy.process.extract(facility.name, [nearby_facility.name])[0]
            #        if score > 80:
            #            for fs in nearby_facility.facilitysubmission_set.all():
            #                merged_count += 1
            #                fs.facility = facility
            #                fs.save()
            #            nearby_facility.delete()
            #            deleted_count += 1
        #print "Merged %d submissions" % merged_count
        #print "Deleted %d facilities" % deleted_count

