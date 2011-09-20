from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^formXml/$', "openrosa.views.formXml", {}, "openrosa_formxml"),
    (r'^formList/$', "openrosa.views.formList", {}, "openrosa_formlist"),
    (r'^submission/$', "openrosa.views.submission", {}, "openrosa_submission"),
    (r'^submission/view/(?P<id>\d+)/$', "openrosa.views.view_submission", {}, "openrosa_view_submission"),
)

