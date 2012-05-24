from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
import openrosa.models

class Command(BaseCommand):
    def handle(self, *args, **options):
        query = Q(submissionworkerdevice__verified=True)
        query &= Q(submissionworkerdevice__valid=True)
        query &= Q(facilitysubmission=None)
        facility = openrosa.models.ORFormSubmission.objects.filter(query).filter(form__name='Facility Form')
        medicine = openrosa.models.ORFormSubmission.objects.filter(query).filter(form__name='Medicines Form')
        print 'Facility submissions:'
        for submission in facility:
            print 'Submission: %5d  SWD: %5d' % (submission.id, submission.submissionworkerdevice.id)
        print 'Medicine submissions:'
        for submission in medicine:
            print 'Submission: %5d  SWD: %5d' % (submission.id, submission.submissionworkerdevice.id)

