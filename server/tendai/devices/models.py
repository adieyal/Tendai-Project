from django.db import models
from django.core.urlresolvers import reverse

from openrosa import models as ormodels

class Country(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"

class Organisation(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

class CommunityWorker(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    organisation = models.ForeignKey(Organisation)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True)

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

    def get_absolute_url(self):
        return reverse("devices_view_swd", kwargs={"id" : self.id})

    def __unicode__(self):
        return unicode(self.community_worker)

class CountryForm(models.Model):
    country = models.ForeignKey(Country)
    form = models.ForeignKey(ormodels.ORForm)

    def __unicode__(self):
        return unicode("%s %s" % (self.country, self.form), "utf-8")
