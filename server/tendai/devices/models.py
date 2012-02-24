from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from datetime import datetime, timedelta

from openrosa import models as ormodels

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
    
    def get_container(self):
        return _(self.form.container)
    container=property(get_container)
        
    def get_containers(self):
        return _(self.form.containers)
    containers=property(get_containers)
    
    def get_unit(self):
        return _(self.form.unit)
    unit=property(get_unit)
    
    def get_units(self):
        return _(self.form.units)
    units=property(get_units)
    
    def stocked(self, country, year=None, month=None):
        tag_name = slugify(self.name) + '-' + slugify(self.form.unit)
        stocked_yes = 0
        stocked_no = 0
        forms = SubmissionWorkerDevice.objects.filter(community_worker__country=country).filter(submission__form__name='Medicines Form')
        if year:
            forms = forms.filter(created_date__year=year)
        if month:
            forms = forms.filter(created_date__month=month)
        for form in forms:
            content = form.submission.content
            if content:
                try:
                    stocked = getattr(content.section_stocked, tag_name)
                except:
                    stocked = 'not_found'
                if stocked == 'yes':
                    stocked_yes += 1
                if stocked == 'no':
                    stocked_no += 1
        #Note all integer math. Will be percentage rounded down to whole.
        if (stocked_yes+stocked_no)>0:
            return (stocked_yes*100)/(stocked_yes+stocked_no)
        return '-'
    
    def stockout(self, country, year=None, month=None):
        tag_name = 'medicine-' + slugify(self.name) + '-' + slugify(self.form.unit)
        stockout_yes = 0
        stockout_no = 0
        forms = SubmissionWorkerDevice.objects.filter(community_worker__country=country).filter(submission__form__name='Medicines Form')
        if year:
            forms = forms.filter(created_date__year=year)
        if month:
            forms = forms.filter(created_date__month=month)
        for form in forms:
            content = form.submission.content
            if content:
                try:
                    section = getattr(content, tag_name)
                    stockout = section.medicine_available
                except:
                    stockout = 'not_found'
                if stockout == 'yes':
                    stockout_yes += 1
                if stockout == 'no':
                    stockout_no += 1
        #Note all integer math. Will be percentage rounded down to whole.
        if (stockout_yes+stockout_no)>0:
            return (stockout_yes*100)/(stockout_yes+stockout_no)
        return '-'
    
    def level(self, country, year=None, month=None):
        tag_name = 'medicine-' + slugify(self.name) + '-' + slugify(self.form.unit)
        total_level = 0
        facilities = 0
        forms = SubmissionWorkerDevice.objects.filter(community_worker__country=country).filter(submission__form__name='Medicines Form')
        if year:
            forms = forms.filter(created_date__year=year)
        if month:
            forms = forms.filter(created_date__month=month)
        for form in forms:
            content = form.submission.content
            if content:
                try:
                    section = getattr(content, tag_name)
                    level = int(section.packs_available)
                except:
                    level = 0
                if level > 0:
                    total_level += level
                    facilities += 1
        #Note all integer math. Will be percentage rounded down to whole.
        if (facilities)>0:
            return total_level/facilities
        return '-'
    
    def stockout_days(self, country, year=None, month=None):
        tag_name = 'medicine-' + slugify(self.name) + '-' + slugify(self.form.unit)
        total_days = 0
        facilities = 0
        forms = SubmissionWorkerDevice.objects.filter(community_worker__country=country).filter(submission__form__name='Medicines Form')
        if year:
            forms = forms.filter(created_date__year=year)
        if month:
            forms = forms.filter(created_date__month=month)
        for form in forms:
            content = form.submission.content
            if content:
                try:
                    section = getattr(content, tag_name)
                    days = VALUE_TO_DAYS[section.stockout_duration]
                except:
                    days = 0
                if days > 0:
                    total_days += days
                    facilities += 1
        if (facilities)>0:
            return total_days/facilities
        return '-'
    
    def replenish_days(self, country, year=None, month=None):
        tag_name = 'medicine-' + slugify(self.name) + '-' + slugify(self.form.unit)
        total_days = 0
        facilities = 0
        forms = SubmissionWorkerDevice.objects.filter(community_worker__country=country).filter(submission__form__name='Medicines Form')
        if year:
            forms = forms.filter(created_date__year=year)
        if month:
            forms = forms.filter(created_date__month=month)
        for form in forms:
            content = form.submission.content
            if content:
                try:
                    section = getattr(content, tag_name)
                    days = VALUE_TO_DAYS[section.restock_date]
                except:
                    days = 0
                if days > 0:
                    total_days += days
                    facilities += 1
        if (facilities)>0:
            return total_days/facilities
        return '-'
    
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

class CommunityWorker(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    organisation = models.ForeignKey(Organisation)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)
    
    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)
    
    def get_name(self):
        try:
            first_name = self.first_name.split(' ', 1)[0]
        except:
            first_name = self.first_name
        return "%s %s" % (first_name, self.last_name)

    def get_forms_count(self, days=30):
        forms = ormodels.ORForm.objects.order_by('name').values('name').distinct()
        forms_count = {}
        for form in forms:
            count = self.submissionworkerdevice_set.filter(submission__form__name=form['name']).filter(created_date__gte=datetime.now()-timedelta(days=days)).count()
            forms_count[form['name']] = count
        return forms_count
    
    def __unicode__(self):
        return "%s %s (%s)" % (self.first_name, self.last_name, self.organisation)

class Device(models.Model):
    device_id = models.CharField(max_length=30)
    community_worker = models.ForeignKey(CommunityWorker)

    def __unicode__(self):
        return "%s" % self.device_id

class SubmissionWorkerDevice(models.Model):
    community_worker = models.ForeignKey(CommunityWorker, null=True)
    device = models.ForeignKey(Device, null=True)
    submission = models.ForeignKey(ormodels.ORFormSubmission, null=True)
    # I don't like this field but adminmodels can't use date_hierarchy on a related object (submission)
    created_date = models.DateTimeField(auto_now_add=True) 
    active = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("devices_view_swd", kwargs={"id" : self.id})

    def __unicode__(self):
        return unicode(self.community_worker)

class CountryForm(models.Model):
    """
    A model that assigns a form to a number of countries
    """
    countries = models.ManyToManyField(Country)
    language = models.ForeignKey(Language, blank=True, null=True)
    form = models.ForeignKey(ormodels.ORForm)

    def __unicode__(self):
        return unicode("%s" % self.form, "utf-8")
