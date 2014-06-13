from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('data.views',
    (r'^submissions_per_day/html/(?P<country_code>\w{2})/$', direct_to_template, {'template' : 'data/calendar.html'},'submissions_per_day_html'),
    (r'^submissions_per_day/js/(?P<country_code>\w{2})/$', direct_to_template, {'template' : 'data/calendar.js'},'submissions_per_day_js'),
    (r'^submissions_per_day/csv/(?P<country_code>\w{2})/$', 'submissions_per_day', {},'submissions_per_day_csv'),
)
