from django.db import models
from django.db.models import Q, Sum
from utils import last_day_of_month
import calendar

import devices.models


class MOHInteractionLevelManager(models.Manager):
    def default_for_country(self, country):
        try:
            return super(MOHInteractionLevelManager, self).get_query_set().filter(country=country)[0]
        except IndexError:
            return None

class MOHInteractionLevel(models.Model):
    country = models.ForeignKey(devices.models.Country)
    level = models.IntegerField()
    comment = models.TextField()
    date = models.DateField()
    
    objects = MOHInteractionLevelManager()
    
    class Meta:
        ordering = ('date',)


class DisbursementManager(models.Manager):
    def total_for_country(self, country, year, month):
        last_day = last_day_of_month(year, month)
        query = Q(country=country)
        query &= Q(date__lte=last_day)
        to_date = super(DisbursementManager, self).get_query_set().filter(query).aggregate(total_amount=Sum('amount'))
        return to_date['total_amount'] or 0.0

class Disbursement(models.Model):
    country = models.ForeignKey(devices.models.Country)
    amount = models.FloatField()
    date = models.DateField()
    
    objects = DisbursementManager()
    
    class Meta:
        ordering = ('date',)
