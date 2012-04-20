from django.conf.urls.defaults import *

urlpatterns = patterns('sms.views',
    url(r'^status/(?P<sms_id>\d+)/$', 'status', {}, 'sms_callback'),
    url(r'^callback$', 'callback', {}, 'sms_callback'),
)
