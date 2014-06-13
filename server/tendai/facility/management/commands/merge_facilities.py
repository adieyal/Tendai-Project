from itertools import chain
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import translation
from facility import models as facilitymodels
from devices import models as devicemodels
from django.contrib.gis.measure import D 
import fuzzywuzzy.process

class Command(BaseCommand):
    """
    Create facilities for all new facility and medicines submissions then try to consolidate facilities
    in order to remove duplicates
    """

    def merge_facilities(self, from_facility, to_facility):
        merged_count = deleted_count = 0
        # 
        if to_facility.pk:
            print "Merged %s (%s) => %s (%s)" % (from_facility.pk, from_facility.facilitysubmission_set.count(), to_facility.pk, to_facility.facilitysubmission_set.count())
            for fs in from_facility.facilitysubmission_set.all():
                merged_count += 1
                fs.facility = to_facility
                fs.save()
            if from_facility.pk: 
                from_facility.delete()
                deleted_count += 1
        return (merged_count, deleted_count)

    def match_by_name(self, facility1, facility2, threshold=80):
        _, score = fuzzywuzzy.process.extract(facility1.name, [facility2.name])[0]
        if score > threshold:
            return True
        return False 

    def get_nearby_facilities(self, facility):
        point = facility.point
        for nearby_facility in facilitymodels.Facility.objects.filter(point__distance_lt=(point, D(m=500))):
            if facility == nearby_facility: continue
            yield nearby_facility

    def get_facilities_in_country(self, facility):
        country_set = devicemodels.Country.objects.filter(communityworker__submissionworkerdevice__submission__facilitysubmission__facility=facility)
        if len(country_set) > 0:
            country = country_set[0]
            other_facilities = facilitymodels.Facility.objects.filter(
                facilitysubmission__submission__submissionworkerdevice__community_worker__country=country
            ).distinct().count()
            return other_facilities
        return []
        
    def handle(self, *args, **options):
        facilities = facilitymodels.Facility.objects.all() 
        merged_count = deleted_count = added_count = 0

        with transaction.commit_on_success():
            # Create new facilities for all facility submissions without facilities before merging
            query = Q(submission__form__name="Facility Form") | Q(submission__form__name="Medicines Form")
            query &= Q(submission__facilitysubmission=None)
            for swd in devicemodels.SubmissionWorkerDevice.objects.all_valid.filter(query):
                print 'Creating SWD: %s' % (swd.id)
                facility = facilitymodels.create_new_facility(devicemodels.SubmissionWorkerDevice, swd.submission)
                if facility:
                    added_count += 1

            for facility in facilities:
                for nearby_facility in chain(self.get_nearby_facilities(facility)):
                    if facility == nearby_facility: continue
                    #if nearby_facility.distance.m <= 50:
                    if self.match_by_name(facility, nearby_facility):
                        from_facility, to_facility = sorted([facility, nearby_facility], key=lambda x : x.facilitysubmission_set.count())
                        (m, d) = self.merge_facilities(from_facility, to_facility)
                        merged_count += m
                        deleted_count += d
                    else:
                        print "Location match, not name: %s => %s" % (facility.name, nearby_facility.name)
        print "Merged %d submissions" % merged_count
        print "Deleted %d facilities" % deleted_count
        print "Created %d facilities" % added_count

