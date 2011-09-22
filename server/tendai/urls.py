from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

from django.http import HttpResponseRedirect
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url' :'/admin'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^openrosa/', include('openrosa.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT,}),
    )

