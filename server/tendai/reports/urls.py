from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'^facility/map/$', direct_to_template, {'template': 'reports/facilities.html'}, 'reports_facilities_map'),
    (r'^facility/map/data.txt$', 'reports.views.facilitiesData', {}, 'reports_facilities_data'),
    (r'^facility/map/data.kml$', 'reports.views.facilitiesKML', {}, 'reports_facilities_kml'),
    (r'^facility/(?P<submission_id>\w+)/$', 'reports.views.facilityInfo', {}, 'reports_facilities_info'),
)
