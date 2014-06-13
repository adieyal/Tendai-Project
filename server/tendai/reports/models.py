from django.db import models


#class Feedback(models.Model):
#    submission = models.ForeignKey(ORFormSubmission)
#    title = models.CharField(max_length=50, blank=True)
#    district_coordinator = models.CharField(max_length=60, blank=True)
#    facility = models.ForeignKey(Facility, null=True, blank=True)
#    last_monitoring_date = models.DateField()
#    campaign_activities = models.TextField()
#    advocacy_activities = models.TextField()
#
#    def __unicode__(self):
#        return "Feedback report by %s for %s" % (self.submission.submissionworkerdevice.community_worker, self.last_monitoring_date)
