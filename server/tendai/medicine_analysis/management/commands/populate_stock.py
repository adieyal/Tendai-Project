from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

import openrosa.models
import medicine_analysis.models

class Command(BaseCommand):
    def handle(self, *args, **options):
        created = 0
        errors = 0
        query = Q(medicinestock=None)
        query &= Q(medicinerestock=None)
        query &= Q(medicinerestockexpectation=None)
        with transaction.commit_on_success():
            for submission in openrosa.models.ORFormSubmission.objects.filter(query):
                try:
                    medicine_analysis.models.create_models_from_submission(submission)
                    created += 1
                except Exception, e:
                    print '%s' % (e)
                    errors += 1
        print 'Created models for %d submissions.' % (created)
        print 'Errors occured for %d submissions.' % (errors)

