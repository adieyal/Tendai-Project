from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

from django.http import HttpResponseRedirect
from django.views.generic.simple import redirect_to

from views import slider_view, recent_stories

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^openrosa/', include('openrosa.urls')),
    ('^$', slider_view, {}, "home"),
    ('^stories/$', recent_stories, {}, "recent_stories"),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT,}),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.STATIC_ROOT,}),
    )

    urlpatterns += staticfiles_urlpatterns()
