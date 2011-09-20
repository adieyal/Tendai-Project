from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

from django.http import HttpResponseRedirect
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url' :'/admin'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^openrosa/', include('openrosa.urls')),
)
