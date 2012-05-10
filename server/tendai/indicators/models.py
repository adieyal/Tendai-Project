from django.db import models

import devices.models


class MOHInteractionLevelManager(models.Manager):
    def default_for_country(self, country):
        try:
            return super(MOHInteractionLevelManager, self).get_query_set().filter(country=country)[0]
        except IndexError:
            return None

class MOHInteractionLevel(models.Model):
    level = models.IntegerField()
    country = models.ForeignKey(devices.models.Country)
    created = models.DateTimeField(auto_now_add=True)
    
    objects = MOHInteractionLevelManager()
    
    class Meta:
        ordering = ('created',)


class ProjectCostManager(models.Manager):
    def default_for_country(self, country):
        try:
            return super(ProjectCostManager, self).get_query_set().filter(country=country)[0]
        except IndexError:
            return None

class ProjectCost(models.Model):
    cost = models.FloatField()
    country = models.ForeignKey(devices.models.Country)
    created = models.DateTimeField(auto_now_add=True)
    
    objects = ProjectCostManager()
    
    class Meta:
        ordering = ('created',)
