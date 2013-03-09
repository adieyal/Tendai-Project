from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django import http
import json
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.helpers import ThumbnailError


import models

def home(request):
    return page(request, slug='home')
    return direct_to_template(request, 'website/home.html', extra_context)

def page(request, slug=None, page_id=None):
    if slug:
        page = get_object_or_404(models.Page, slug=slug)
    else:
        page = get_object_or_404(models.Page, pk=page_id)
    extra_context = { 'page': page }
    return direct_to_template(request, page.template.path, extra_context)

def stories(request):
    country = request.GET.get('country', None)
    count = request.GET.get('count', 5)
    stories = models.Story.objects.filter(status='p').order_by("-submission__end_time")
    if country and country != 'all':
        stories = stories.filter(country__code=country)

    def thumbnail(url, size):
        try:
            return get_thumbnail(url, size).url
        except ThumbnailError:
            return ""
    data = [{
            'id': s.id,
            'heading': s.heading,
            'content': s.content,
            'photo': s.imageurl,
            'thumbnail': thumbnail(s.photo, '240x240'),
            'monitor': s.monitor.get_name(),
            'country': s.country.name,
            'date': str(s.submission.end_time),
            } for s in stories[0:count]]            
    return http.HttpResponse(json.dumps(data, indent=2), content_type='application/json')
