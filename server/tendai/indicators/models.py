from django.db import models
from django.db.models import Q, Sum
from utils import last_day_of_month
import calendar

import devices.models


class PriorToManager(models.Manager):
    def prior_to(self, year, month):
        last_day = last_day_of_month(year, month)
        query = Q(date__lte=last_day)
        return super(PriorToManager, self).get_query_set().filter(query)


class MOHInteractionLevel(models.Model):
    country = models.ForeignKey(devices.models.Country)
    level = models.IntegerField()
    comment = models.TextField()
    date = models.DateField()
    
    objects = PriorToManager()
    
    class Meta:
        ordering = ('-date',)


class MOHInteractionType(models.Model):
    description = models.CharField(max_length=32)
    points = models.IntegerField(
        help_text='Please enter an integer for the number of points associated with this interaction type.'
        )
    
    def __unicode__(self):
        return u'%2d points - %s' % (self.points, self.description)
    class Meta:
        ordering = ('-points',)

class MOHInteraction(models.Model):
    country = models.ForeignKey(devices.models.Country)
    type = models.ForeignKey(MOHInteractionType)
    comment = models.TextField()
    date = models.DateField()
    
    objects = PriorToManager()
    
    class Meta:
        ordering = ('-date',)


class Disbursement(models.Model):
    country = models.ForeignKey(devices.models.Country)
    amount = models.FloatField(help_text='Please enter the amount disbursed in British Pounds.')
    date = models.DateField()
    
    objects = PriorToManager()
    
    class Meta:
        ordering = ('-date',)


class TendaiProgressReport(models.Model):
    country = models.ForeignKey(devices.models.Country)
    date = models.DateField()
    reporting = models.BooleanField(verbose_name='Satisfactory')
    reporting_comment = models.TextField(verbose_name='Comments')
    adjustment = models.BooleanField(verbose_name='Satisfactory')
    adjustment_comment = models.TextField(verbose_name='Comments')
    
    objects = PriorToManager()
    
    class Meta:
        ordering = ('-date',)


class Risk(models.Model):
    LEVELS = (('low', 'Low'),
              ('medium', 'Medium'),
              ('high', 'High'))
    country = models.ForeignKey(devices.models.Country)
    date = models.DateField()
    level = models.CharField(max_length=6, choices=LEVELS)
    comment = models.TextField()
    
    class Meta:
        ordering = ('-date',)
