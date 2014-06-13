from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('scorecards.views',
    (r'^(?P<country>[a-z]{2})/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', 'scorecard', {}, 'scorecard'),
)
