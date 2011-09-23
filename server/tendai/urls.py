from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

from django.http import HttpResponseRedirect
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^openrosa/', include('openrosa.urls')),
    ('^$', direct_to_template, {
        'template': 'home.html'
    })
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT,}),
    )

    urlpatterns += staticfiles_urlpatterns()
