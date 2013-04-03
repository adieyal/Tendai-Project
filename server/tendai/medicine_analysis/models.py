from django.db import models
from django.db import transaction
from datetime import timedelta
import iso8601

from devices.models import Medicine
from facility.models import Facility
from openrosa.models import ORFormSubmission

class MedicineStock(models.Model):
    medicine = models.ForeignKey(Medicine)
    facility = models.ForeignKey(Facility)
    submission = models.ForeignKey(ORFormSubmission)
    timestamp = models.DateTimeField()
    amount = models.IntegerField()
    inconsistent = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u'%d units of %s' % (self.amount, self.medicine)
    
    class Meta:
        verbose_name_plural = 'Medicine Stock Levels'
        ordering = ('timestamp',)


class MedicineRestockExpectation(models.Model):
    medicine = models.ForeignKey(Medicine)
    facility = models.ForeignKey(Facility)
    submission = models.ForeignKey(ORFormSubmission)
    timestamp = models.DateTimeField()
    start = models.DateField()
    end = models.DateField()
    amount = models.IntegerField(blank=True, null=True)
    inconsistent = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u'%s units of %s' % (self.amount or 'Unknown number of', self.medicine)
    
    class Meta:
        verbose_name_plural = 'Medicine Restock Expectations'
        ordering = ('-timestamp',)


class MedicineRestock(models.Model):
    medicine = models.ForeignKey(Medicine)
    facility = models.ForeignKey(Facility)
    submission = models.ForeignKey(ORFormSubmission)
    timestamp = models.DateTimeField()
    start = models.DateField()
    end = models.DateField()
    amount = models.IntegerField(blank=True, null=True)
    inconsistent = models.BooleanField(default=False)
    
    def __unicode__(self):
        return u'%s units of %s' % (self.amount or 'Unknown number of', self.medicine)
    
    class Meta:
        verbose_name_plural = 'Medicine Restock Events'
        ordering = ('-timestamp',)

class MedicineStockout(models.Model):
    medicine = models.ForeignKey(Medicine)
    facility = models.ForeignKey(Facility)
    submission = models.ForeignKey(ORFormSubmission)

    def __unicode__(self):
        return "Stockout of %s at %s in %s" % (self.medicine, self.facility, self.submission.end_time.month)

VALUE_TO_TIMEDELTA = {'blank_period': None,
                      '1-3_days': (timedelta(days=1), timedelta(days=3)),
                      '4-7_days': (timedelta(days=4), timedelta(days=7)),
                      '1-2_weeks': (timedelta(weeks=1), timedelta(weeks=2)),
                      '2-3_weeks': (timedelta(weeks=2), timedelta(weeks=3)),
                      '3-4_weeks': (timedelta(weeks=3), timedelta(weeks=4)),
                      '1-2_months': (timedelta(days=30), timedelta(days=60)),
                      '2-3_months': (timedelta(days=60), timedelta(days=90)),
                      'more_than_3_months': (timedelta(days=90), timedelta(days=365)),
                      'unknown': None
                      }

def get_start_and_end_dates(value, datetime, ago=False):
    td = VALUE_TO_TIMEDELTA[value]
    if not td:
        return None, None
    else:
        if ago:
            return datetime-td[1], datetime-td[0]
        else:
            return datetime+td[0], datetime+td[1]


def create_models_from_submission(submission):
    if submission.form.name != 'Medicines Form':
        return
    with transaction.commit_on_success():
        content = submission.content
        name = content.section_general.facility_name
        try:
            facility = submission.facilitysubmission_set.all()[0].facility
        except IndexError:
            raise ValueError('Submission is not linked to a facility.')
        timestamp = iso8601.parse_date(content.start_time)
        meds = [m for m in content.section_stocked.nodes() if not m.endswith('_comments')]
        for m in meds:
            if getattr(content.section_stocked, m).lower() == 'yes':
                medicine = Medicine.from_name(m)
                medicine_node = getattr(content, 'medicine-'+m)
                # Create MedicineStock object.
                if medicine_node.medicine_available:
                    amount = int(medicine_node.packs_available)
                else:
                    amount = 0
                MedicineStock.objects.create(
                    submission = submission,
                    facility = facility,
                    medicine = medicine,
                    timestamp = timestamp,
                    amount = amount
                    )
                # Create MedicineRestockExpected object.
                time = medicine_node.restock_date
                start, end = get_start_and_end_dates(time, timestamp)
                if start and end:
                    amount = int(medicine_node.restock_ordered)
                    if amount == 9999:
                        amount = None
                    MedicineRestockExpectation.objects.create(
                        submission = submission,
                        facility = facility,
                        medicine = medicine,
                        timestamp = timestamp,
                        start = start,
                        end = end,
                        amount = amount
                        )
                # Create MedicineRestock object.
                time = medicine_node.last_restock_date
                start, end = get_start_and_end_dates(time, timestamp, ago=True)
                if start and end:
                    amount = int(medicine_node.last_restock_amount)
                    if amount == 9999:
                        amount = None
                    MedicineRestock.objects.create(
                        submission = submission,
                        facility = facility,
                        medicine = medicine,
                        timestamp = timestamp,
                        start = start,
                        end = end,
                        amount = amount
                        )

