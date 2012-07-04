from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('website.views',
    (r'^$', 'home', {}, 'website_home'),
    (r'^page/(?P<page_id>\d+)/$', 'page', {}, 'website_page_by_id'),
    (r'^page/(?P<slug>[a-z\-]+)/$', 'page', {}, 'website_page'),
    (r'^json/stories/$', 'stories', {}, 'website_stories'),
)
