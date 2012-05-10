from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.CombinedView.as_view(), {}, 'dashboard_indicators'),
)
