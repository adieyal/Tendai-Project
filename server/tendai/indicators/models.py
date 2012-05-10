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


class MOHInteraction(models.Model):
    country = models.ForeignKey(devices.models.Country)
    points = models.IntegerField()
    comment = models.TextField()
    date = models.DateField()
    
    objects = PriorToManager()
    
    class Meta:
        ordering = ('-date',)


class Disbursement(models.Model):
    country = models.ForeignKey(devices.models.Country)
    amount = models.FloatField()
    date = models.DateField()
    
    objects = PriorToManager()
    
    class Meta:
        ordering = ('-date',)
