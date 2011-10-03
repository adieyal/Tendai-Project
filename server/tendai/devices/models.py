from django.db import models
from openrosa import models as ormodels

class Organisation(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name

class CommunityWorker(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    organisation = models.ForeignKey(Organisation)
    phone_number = models.CharField(max_length=30, blank=True, null=True)

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

    def __unicode__(self):
        return unicode(self.community_worker)
