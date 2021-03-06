import os
from xml.dom import minidom
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings

from general.utils import value_or_none, date_or_none
from general.parser import SubmissionParser

class ORForm(models.Model):
    name = models.CharField(max_length=100)
    form_id = models.CharField(max_length=30, verbose_name="Form ID")
    majorminorversion = models.CharField(max_length=10, verbose_name="Major Minor Version")
    description = models.CharField(max_length=10, null=True, blank=True)
    modified_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.majorminorversion)

    class Meta:
        verbose_name_plural = "OR Forms"
        verbose_name = "OR Form"
        unique_together = ('name', 'form_id',)

    def get_absolute_url(self):
        return reverse("openrosa_formxml") + "?formId=" + self.form_id

    def get_filename(self):
        return self.form_id + ".xml"

class ORFormSubmission(models.Model):
    form = models.ForeignKey(ORForm, null=True)
    filename = models.CharField(max_length=30)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    device_id = models.CharField(max_length=30, null=True)
    subscriber_id = models.CharField(max_length=30, null=True)
    sim_id = models.CharField(max_length=30, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "OR Form Submissions"
        verbose_name = "OR Form Submission"

    def __init__(self, *args, **kwargs):
        super(ORFormSubmission, self).__init__(*args, **kwargs)
        self.content = SubmissionParser.from_file(self.get_full_xml_path())
    
    def __unicode__(self):
        return "%s (%s)" % (self.form, self.created_date)

    def get_absolute_url(self):
        return reverse("openrosa_view_submission", kwargs={"id" : self.id})

    def get_full_xml_path(self):
        path = os.path.join(settings.OPENROSA_SUBMISSIONS_DIR, self.filename)
        return path
    
    def save(self, *args, **kwargs):
        is_new = self.id == None
        super(ORFormSubmission, self).save(*args, **kwargs)
        
        if is_new:
            xml = minidom.parse(self.get_full_xml_path()) 
            self.device_id = value_or_none(xml, "device_id")
            self.subscriber_id = value_or_none(xml, "subscriber_id")
            self.sim_id = value_or_none(xml, "sim_id")

            self.start_time = date_or_none(xml, "start_time")
            self.end_time = date_or_none(xml, "end_time")

            self.save()
            
class ORSubmissionMedia(models.Model):
    submission = models.ForeignKey(ORFormSubmission)
    filename = models.CharField(max_length=30)

    def get_absolute_url(self):
        url = reverse("openrosa_media", kwargs={
            "device_id" : self.submission.device_id, 
            "filename" : self.filename
        })
        return url

    def get_absolute_path(self):
        media_dir = os.path.join(settings.OPENROSA_IMAGES_DIR, self.submission.device_id)
        path = os.path.join(media_dir, self.filename)
        if os.path.exists(path):
            return path
        return None

    def __unicode__(self):
        return self.filename

    class Meta:
        verbose_name_plural = "OR Submission Media"
        verbose_name = "OR Submission Media"
