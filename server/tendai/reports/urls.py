from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^facility/map/$', 'reports.views.facilitiesMap', {}, 'reports_facilities_map'),
    (r'^facility/map/data.txt$', 'reports.views.facilitiesData', {}, 'reports_facilities_data'),
)
