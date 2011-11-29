from django.conf.urls.defaults import *
from openrosa import urls as openrosa_urls

urlpatterns = patterns('',
    (r'^formList/$', "devices.views.formList", {}, "openrosa_formlist"),
    (r'^formXml/(?P<country_id>\d+)/$', "devices.views.formXml", {}, "openrosa_dynamic_formxml"),
    (r'^swd/(?P<id>\d+)/$', "devices.views.view_swd", {}, "devices_view_swd"),
    (r'^submissions/$', "devices.views.view_submissions", {}, "devices_view_submissions"),
)

urlpatterns += openrosa_urls.urlpatterns
