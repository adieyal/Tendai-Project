from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from openrosa.models import ORFormSubmission
from devices.models import Medicine
from medicine_analysis.models import MedicineStockout
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Find medicine submissions that have not yet been processed for stockouts
    """
    def handle(self, *args, **options):
        created = 0
        errors = 0
        submissions = ORFormSubmission.objects.filter(
            form__name="Medicines Form",
            medicinestockout=None,
            submissionworkerdevice__valid=True,
            submissionworkerdevice__verified=True
        )
        for submission in submissions:
            content = submission.content
                
            try:
                meds_names = [m for m in content.nodes() if str(m).startswith('medicine-')] 
                meds = [(med, getattr(content, med)) for med in meds_names]
                for med_name, section in meds:
                    if section.medicine_available.lower() == "no":
                        try:
                            medicine = Medicine.from_name(med_name)
                            try:
                                facility = submission.facilitysubmission_set.all()[0].facility
                                MedicineStockout.objects.create(
                                    medicine=medicine,
                                    facility=facility,
                                    submission=submission
                                )
                                created += 1
                            except IndexError:
                                errors += 1
                                logger.warn("Could not find facility for: %s (%d)" % (submission.filename, submission.id))
                        except Exception, e:
                            errors += 1
                            logger.exception(e)
            except Exception, e:
                errors += 1
                logger.exception(e)
        print "%d created and %d errors" % (created, errors)
