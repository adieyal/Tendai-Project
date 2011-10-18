from django.conf.urls.defaults import *
from openrosa import urls as openrosa_urls

urlpatterns = patterns('',
    (r'^formList/$', "devices.views.formList", {}, "openrosa_formlist"),
)

urlpatterns += openrosa_urls.urlpatterns
