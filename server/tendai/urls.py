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
    url(r'^openrosa/', include('devices.urls')),
    #('^$', slider_view, {}, "home"),
    ('^stories/$', recent_stories, {}, "recent_stories"),
    url(r'^reports/', include('reports.urls')),
    url(r'^scorecards/', include('scorecards.urls')),
    url(r'^data/', include('data.urls')),
    url(r'^sms/', include('sms.urls')),
    url(r'^analysis/medicine/', include('medicine_analysis.urls')),
    url(r'^dashboard/indicators/', include('indicators.urls')),
    url('^', include('website.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT,}),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.STATIC_ROOT,}),
    )

    urlpatterns += staticfiles_urlpatterns()
