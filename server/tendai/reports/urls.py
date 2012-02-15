from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('reports.views',
    (r'^facility/map/$', direct_to_template, {'template': 'reports/facilities.html'}, 'reports_facilities_map'),
    (r'^facility/map/data.kml$', 'facilities_kml', {}, 'reports_facilities_kml'),
    (r'^facility/(?P<submission_id>\w+)/$', 'facility_info', {}, 'reports_facilities_info'),
    (r'^country/(?P<country_code>\w+)/$', 'country', {}, 'reports_country'),
    (r'^country/$', 'country', {'country_code': 'za'}, 'reports_country_default'),
    (r'^submission/(?P<id>\w+)/$', 'submission', {}, 'devices_view_swd'),
    (r'^validate/(?P<id>\w+)/$', 'submission', {'validate': True}, 'devices_verify_swd'),
)
