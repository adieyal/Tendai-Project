from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from datetime import datetime, timedelta
from facility import models as facilitymodels
from general.utils import Month, count
from fuzzywuzzy import fuzz
import fuzzywuzzy


from openrosa import models as ormodels
from sms import models as smsmodels

VALUE_TO_DAYS = {'blank_period': 0.0,
                 '1-3_days': 1.5,
                 '4-7_days': 5.5,
                 '1-2_weeks': 10.5,
                 '2-3_weeks': 17.5,
                 '3-4_weeks': 24.5,
                 '1-2_months': 45.0,
                 '2-3_months': 75.0,
                 'more_than_3_months': 90.0,
                 'unknown': 0.0, }

class Language(models.Model):
    name = models.CharField(max_length=30, verbose_name="Language")
    code = models.CharField(max_length=2, verbose_name="ISO639-1 Code")
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.code)

class CountryManager(models.Manager):
    def get_default(self):
        return super(CountryManager, self).get_query_set().all()[0]

class Country(models.Model):
    objects = CountryManager()
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=2, verbose_name="ISO 3166-1 alpha-2 Code")
    language = models.ForeignKey(Language)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"

class Organisation(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

class DosageForm(models.Model):
    container = models.CharField(max_length=30)
    containers = models.CharField(max_length=30, verbose_name="Containers (Plural)")
    unit = models.CharField(max_length=30)
    units = models.CharField(max_length=30, verbose_name="Units (Plural)")
    
    def __unicode__(self):
        return u"%s (%s)" % (self.container, self.units)


class Medicine(models.Model):
    name = models.CharField(max_length=60)
    form = models.ForeignKey(DosageForm)
    countries = models.ManyToManyField(Country)
    
    @property
    def container(self):
        return _(self.form.container)
        
    @property
    def containers(self):
        return _(self.form.containers)
    
    @property
    def unit(self):
        return _(self.form.unit)
    
    @property
    def units(self):
        return _(self.form.units)

    def _medicines_by_country_and_month(self, country, month):
        forms = SubmissionWorkerDevice.objects.medicines_submissions.filter(
            community_worker__country=country,
        )

        if month:
            forms = forms.filter(
                created_date__month=month.month,
                created_date__year=month.year
            )
        return forms

    def _medicine_tag_name(self):
        return 'medicine-%s-%s' % (slugify(self.name), slugify(self.form.unit))

    def _get_medicine_section(self, country, month):
        forms = self._medicines_by_country_and_month(country, month)
        tag_name = self._medicine_tag_name()
        return (
            getattr(form.submission.content, tag_name) 
            for form in forms 
            if form.submission.content and hasattr(form.submission.content, tag_name)
        )

    def _get_medicine_sections_with_packs(self, country, month):
        has_packs_available = lambda x : hasattr(x, "packs_available")
        return filter(has_packs_available, self._get_medicine_section(country, month))

    def _get_medicine_sections_with_medicine_available(self, country, month):
        has_medicine_available = lambda x : hasattr(x, "medicine_available")
        return filter(has_medicine_available, self._get_medicine_section(country, month))

    def _perc_yes(self, yes_vals, no_vals):
        #Note all integer math. Will be percentage rounded down to whole.
        if (yes_vals + no_vals) > 0:
            return (yes_vals * 100) / (yes_vals + no_vals)
        else: "-"

    def _safe_div(self, num, denom):
        if denom > 0:
            return num / denom
        return "-"

    def stocked(self, country, month=None):
        stocked_yes = stocked_no = 0
        forms = self._medicines_by_country_and_month(country, month)
        tag_name = self._medicine_tag_name().replace("medicine-", "")

        stocked_sections = [
            getattr(form.submission.content, "section_stocked")
            for form in forms
            if form.submission.content and hasattr(form.submission.content, "section_stocked")
        ]

        stock_values = [
            getattr(section, tag_name)
            for section in stocked_sections
            if hasattr(section, tag_name)
        ] 

        stocked_yes = count(stock_values, lambda x : x.lower() == "yes")
        stocked_no = count(stock_values, lambda x : x.lower() == "no")
        
        return self._perc_yes(stocked_yes, stocked_no)

    def stock(self, country, month=None):
        stockout_yes = stockout_no = 0

        sections_with_medicines = self._get_medicine_sections_with_medicine_available(country, month)
        stockout_values = [section.medicine_available for section in sections_with_medicines]
        stocked_yes = count(stockout_values, lambda x : x.lower() == "yes")
        stocked_no = count(stockout_values, lambda x : x.lower() == "no")

        #Note all integer math. Will be percentage rounded down to whole.
        return self._perc_yes(stocked_yes, stocked_no)
    
    def level(self, country, month=None):
        total_level = facilities = 0
        sections_with_packs = self._get_medicine_sections_with_packs(country, month)
        packs_available_values = [int(section.packs_available) for section in sections_with_packs]

        total_level = sum(v for v in packs_available_values if v not in [8888, 9999] )
        facilities = count(packs_available_values, lambda x : x > 0)

        return self._safe_div(total_level, facilities)

    def stockout_days(self, country, month=None):
        sections_with_packs = self._get_medicine_sections_with_packs(country, month)
        is_stockout = lambda section : int(section.packs_available) == 0
        zero_levels = filter(is_stockout, sections_with_packs)

        total_days = sum(VALUE_TO_DAYS[section.stockout_duration] for section in zero_levels)
        facilities = count(zero_levels, lambda section : VALUE_TO_DAYS[section.stockout_duration] > 0)

        return self._safe_div(total_days, facilities)
    
    def replenish_days(self, country, month=None):
        total_days = facilities = 0
        sections_with_packs = self._get_medicine_sections_with_packs(country, month)
        is_stockout = lambda section : int(section.packs_available) == 0
        zero_levels = filter(is_stockout, sections_with_packs)

        total_days = sum(VALUE_TO_DAYS[section.restock_date] for section in zero_levels)
        facilities = count(zero_levels, lambda section : VALUE_TO_DAYS[section.restock_date] > 0)

        return self._safe_div(total_days, facilities)
    
    @classmethod
    def from_name(cls, name):
        name = name.replace('-', ' ').lower()
        meds = [(item, item.name.replace('/','').lower()) for item in cls.objects.all()]
        best = (None, 0)
        for med in meds:
            score = fuzz.partial_ratio(med[1], name)
            if score > best[1]:
                best = (med[0], score)
        return best[0]
    
    def __unicode__(self):
        return u"%s %s" % (self.name, self.form.units)
    
    class Meta:
        unique_together = ('name', 'form',)

class Currency(models.Model):
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=30, blank=True, null=True)
    
    def __unicode__(self):
        return u"%s" % (self.name)
    
    class Meta:
        verbose_name_plural = "Currencies"

class District(models.Model):
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=30)
    country = models.ForeignKey(Country)
    
    def __unicode__(self):
        return u"%s, %s" % (self.name, self.country)

class CommunityWorkerManager(models.Manager):
    @property
    def all_active(self):
        return self.all().filter(
            active=True
        )

class CommunityWorker(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    organisation = models.ForeignKey(Organisation)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True, related_name="monitors")
    active = models.BooleanField(default=1)

    objects = CommunityWorkerManager()
    
    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)
    
    def get_name(self):
        try:
            first_name = self.first_name.split(' ', 1)[0]
        except:
            first_name = self.first_name
        return "%s %s" % (first_name, self.last_name)

    @property
    def my_submissions(self):
        return SubmissionWorkerDevice.objects.all_valid.filter(
            community_worker=self
        )

    def __unicode__(self):
        return "%s %s (%s)" % (self.first_name, self.last_name, self.organisation)

class MonitorSubmissions(object):
    def __init__(self, monitor):
        self.monitor = monitor

    @property
    def all_submissions(self):
        return self.monitor.my_submissions

    def submissions_by_form(self, form_name):
        return self.all_submissions.filter(submission__form__name=form_name) 

    @property
    def facility_submissions(self):
        return self.submissions_by_form("Facility Form")

    @property
    def medicines_submissions(self):
        return self.submissions_by_form("Medicines Form")

    @property
    def story_submissions(self):
        return self.submissions_by_form("Tendai Story")

    @property
    def interview_submissions(self):
        return self.submissions_by_form("Tendai Interview")


class Device(models.Model):
    device_id = models.CharField(max_length=30)
    community_worker = models.ForeignKey(CommunityWorker)

    def __unicode__(self):
        return "%s" % self.device_id

class SubmissionWorkerDeviceManager(models.Manager):
    @property
    def all_valid(self):
        return self.all().filter(
            verified=True, valid=True
        )

    @property
    def medicines_submissions(self):
        return self.all_valid.filter(
            submission__form__name="Medicines Form"
        )

    @property
    def story_submissions(self):
        return self.all_valid.filter(
            submission__form__name="Tendai Story"
        )

class SubmissionWorkerDevice(models.Model):
    community_worker = models.ForeignKey(CommunityWorker, null=True, related_name="submissions")
    device = models.ForeignKey(Device, null=True)
    submission = models.OneToOneField(ormodels.ORFormSubmission, null=True)
    # I don't like this field but adminmodels can't use date_hierarchy on a related object (submission)
    created_date = models.DateTimeField(auto_now_add=True) 
    active = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)

    objects = SubmissionWorkerDeviceManager()

    def get_absolute_url(self):
        return reverse("devices_view_swd", kwargs={"id" : self.id})

    def __unicode__(self):
        return str(self.pk)
        return "[%s] %s" % (self.pk, self.community_worker)

class FacilitySubmission(models.Model):
    submission = models.ForeignKey(ormodels.ORFormSubmission, null=True)
    facility = models.ForeignKey(facilitymodels.Facility, null=True)

    def __unicode__(self):
        return "%s, %s" % (self.submission, self.facility)

class CountryForm(models.Model):
    """
    A model that assigns a form to a number of countries
    """
    countries = models.ManyToManyField(Country)
    language = models.ForeignKey(Language, blank=True, null=True)
    form = models.ForeignKey(ormodels.ORForm)

    def __unicode__(self):
        return unicode("%s" % self.form, "utf-8")

@receiver(post_save, sender=SubmissionWorkerDevice)
def send_submission_sms(sender, instance, **kwargs):
    if "created" in kwargs and kwargs["created"]:
        # Only send SMS if phone number starts with '+'.
        number = instance.community_worker.phone_number
        if (len(number)>0) and (number[0] == "+"):
            sms = smsmodels.SMS()
            sms.number = number
            sms.message = "Hi %s. Thank you for your %s submission. We appreciate your commitment to the project. The InfoHub team." % (instance.community_worker.first_name, instance.submission.form.name)
            sms.save()


class MedicineFormMedicines(models.Model):
    """
    Class used to allocate specific medicines to specific forms. This is useful in the case where one country has multiple medicines forms. When creating the medicines form those medicines listed in this table will be allocated to that specific form. In the implementation, if a form is not listed here, then all the medicines listed in that country will be used instead. 

    I'm not really happy with this class because without the comment, it is not clear what it does but I'm not sure how to implement it in any other way. It also introduces redundancy in the country field with the medicines table.
    """
    countryform = models.ForeignKey(CountryForm)
    medicine = models.ManyToManyField(Medicine)

    class Meta:
        verbose_name_plural = "Medicine Form Medicines"

    def __unicode__(self):
        return u"%s" % (self.countryform)
