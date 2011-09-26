from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^formXml/$', "openrosa.views.formXml", {}, "openrosa_formxml"),
    (r'^formList/$', "openrosa.views.formList", {}, "openrosa_formlist"),
    (r'^media/(?P<device_id>\w+)/(?P<filename>.*)$', "openrosa.views.show_media", {}, "openrosa_media"),
    (r'^submission/$', "openrosa.views.submission", {}, "openrosa_submission"),
    (r'^submission/view/(?P<id>\d+)/$', "openrosa.views.view_submission", {}, "openrosa_view_submission"),
)
