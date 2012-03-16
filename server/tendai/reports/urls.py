from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('reports.views',
    (r'^facility/map/$', direct_to_template, {'template': 'reports/facilities.html'}, 'reports_facilities_map'),
    (r'^facility/map/data.kml$', 'facilities_kml', {}, 'reports_facilities_kml'),
    (r'^facility/(?P<submission_id>\d+)/$', 'facility_info', {}, 'reports_facilities_info'),
    (r'^country/(?P<country_code>[a-z]{2})/$', 'country', {}, 'reports_country'),
    (r'^country/$', 'country', {'country_code': 'za'}, 'reports_country_default'),
    (r'^submission/(?P<id>\d+)/$', 'submission', {}, 'devices_view_swd'),
    (r'^validate/(?P<id>\d+)/$', 'submission', {'validate': True}, 'devices_verify_swd'),
    (r'^validate/$', 'submission', {'validate': True}, 'devices_verify_swd'),
    (r'^validate/(?P<id>\d+)/$', 'submission', {'validate': True}, 'devices_verify_country_swd'),
    (r'^validate/(?P<country>[a-z]{2})/(?P<id>\d+)/$', 'submission', {'validate': True}, 'devices_verify_country_swd'),
    (r'^validate/(?P<country>[a-z]{2})/$', 'submission', {'validate': True}, 'devices_verify_country_swd'),
    (r'^validate/(?P<submission_type>[^/]+)/$', 'submission', {'validate': True}, 'devices_verify_country_swd'),
    (r'^validate/(?P<submission_type>[^/]+)/(?P<id>\d+)/$', 'submission', {'validate': True}, 'devices_verify_country_swd'),
)
