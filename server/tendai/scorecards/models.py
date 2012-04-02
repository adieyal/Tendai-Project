from django.db import models
from openrosa import models as ormodels
from devices import models as devmodels

class ScorecardStory(models.Model):
    submission_worker_device = models.ForeignKey(devmodels.SubmissionWorkerDevice)

    def __unicode__(self):
        return unicode(self.submission_worker_device)

    class Meta:
        verbose_name_plural = "Scorecard Stories"
