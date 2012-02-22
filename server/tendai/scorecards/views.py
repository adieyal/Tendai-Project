import settings

from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from os import path
from lxml import etree
from fuzzywuzzy import fuzz
from datetime import datetime, timedelta
from django.db.models import Count
from base64 import b64encode

import devices.models as dev_models
import openrosa.models as or_models

def index(request):
    return Http404

def scorecard(request, country, year=2011, month=12):
    country = get_object_or_404(dev_models.Country, code=country)
    year = int(year)
    month = int(month)
    swds = dev_models.SubmissionWorkerDevice.objects.filter(community_worker__country=country).filter(created_date__year=year, created_date__month=month)
    
    template = open(path.join(settings.STATIC_ROOT, 'scorecard.svg'))
    svg = etree.XML(template.read())
    
    nsmap = {
        'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
        'cc': 'http://web.resource.org/cc/',
        'svg': 'http://www.w3.org/2000/svg',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'xlink': 'http://www.w3.org/1999/xlink',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
        }
    
    #Helpers for XPath based SVG modification.
    def set_text(xpath, value):
        element = svg.xpath(xpath, namespaces=nsmap)[0]
        element.text = str(value)
    def set_attr(xpath, attr, value):
        element = svg.xpath(xpath, namespaces=nsmap)[0]
        element.set(attr, str(value))
    
    #Country name for heading.
    set_text('//svg:text[@id="country.name"]', country.name.upper())
    
    #Monitors table.
    name = '//svg:text[@id="monitor.%d.name"]'
    facilities = '//svg:text[@id="monitor.%d.facilities"]'
    medicines = '//svg:text[@id="monitor.%d.medicines"]'
    interviews = '//svg:text[@id="monitor.%d.interviews"]'
    stories = '//svg:text[@id="monitor.%d.stories"]'
    totals = '//svg:text[@id="monitor.%d.totals"]'
    monitors = dev_models.CommunityWorker.objects.filter(country=country)
    most_submissions = -1
    best_monitor = None
    for line in range(22):
        try:
            monitor = monitors[line]
            forms_count = monitor.get_forms_count(days=70)
            forms_count = {}
            forms = or_models.ORForm.objects.order_by('name').values('name').distinct()
            for form in forms:
                count = swds.filter(submission__form__name=form['name'], community_worker=monitor).count()
                forms_count[form['name']] = count
            forms_count['Total'] = sum([value for key, value in forms_count.items()])
            if forms_count['Total'] > most_submissions:
                best_monitor = monitor
                most_submissions = forms_count['Total']
        except:
            monitor = None
        selector = 'monitor.' + str(line) + '.name'
        monitor_name = svg.xpath('//svg:text[@id="'+selector+'"]',namespaces=nsmap)[0]
        selector = 'monitor.' + str(line) + '.medicines'
        monitor_medicines = svg.xpath('//svg:text[@id="'+selector+'"]',namespaces=nsmap)[0]
        
        if monitor:
            set_text(name % (line), monitor.get_name())
            set_text(facilities % (line), '-')
            set_text(medicines % (line), forms_count['Medicines Form'])
            set_text(interviews % (line), forms_count['Tendai Interview'])
            set_text(stories % (line), forms_count['Tendai Story'])
            set_text(totals % (line), forms_count['Total'])
        else:
            set_text(name % (line), ' ')
            set_text(facilities % (line), ' ')
            set_text(medicines % (line), ' ')
            set_text(interviews % (line), ' ')
            set_text(stories % (line), ' ')
            set_text(totals % (line), ' ')
            
    #Submissions sliders.
    number = '//svg:text[@id="country.submissions.text"]'
    slider = '//svg:g[@id="country.submissions.slider"]'
    count = swds.filter(community_worker__country=country).count()
    monitors = dev_models.CommunityWorker.objects.filter(country=country).count()
    per_monitor = float(count)/float(monitors)
    set_text(number, '%0.1f' % (per_monitor))
    set_attr(slider, 'transform', 'translate(%.2f)' % (min(per_monitor,4.0)*44.0))
    number = '//svg:text[@id="average.submissions.text"]'
    slider = '//svg:g[@id="average.submissions.slider"]'
    count = dev_models.SubmissionWorkerDevice.objects.filter(created_date__year=year, created_date__month=month).count()
    monitors = dev_models.CommunityWorker.objects.count()
    per_monitor = float(count)/float(monitors)
    set_text(number, '%0.1f' % (per_monitor))
    set_attr(slider, 'transform', 'translate(%.2f)' % (min(per_monitor,4.0)*44.0))
    
    #Monitor of the month.
    name = '//svg:text[@id="best_monitor.name"]'
    organisation = '//svg:text[@id="best_monitor.organisation"]'
    submissions = '//svg:text[@id="best_monitor.submissions"]'
    photo = '//svg:image[@id="best_monitor.image"]'
    set_text(name, best_monitor.get_name())
    set_text(organisation, 'Organisation: %s' % best_monitor.organisation.name)
    set_text(submissions, swds.filter(community_worker=best_monitor).count())
    image = open(path.join(settings.STATIC_ROOT, 'user.jpg'))
    data = b64encode(image.read())
    set_attr(photo, '{%s}href' % (nsmap['xlink']), 'data:image/jpg;base64,%s' % (data))
    
  
    response = HttpResponse(etree.tostring(svg), mimetype='image/svg+xml')
    filename = 'scorecard_%s.svg' % (country.code.lower())
    response['Content-Disposition'] = 'filename=%s' % (filename)
    return response
