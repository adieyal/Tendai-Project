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

MONTHNAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def index(request):
    return Http404

def scorecard(request, country, year=2011, month=12):
    country = get_object_or_404(dev_models.Country, code=country)
    year = int(year)
    month = int(month)
    valid_swds = dev_models.SubmissionWorkerDevice.objects.filter(
        created_date__year=year, 
        created_date__month=month, 
        verified=True, 
        valid=True
    )

    country_valid_swds = valid_swds.filter(
        community_worker__country=country,
    )

    forms = or_models.ORForm.objects.order_by('name').values('name').distinct()
    
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
        if type(value) == float:
            value = '%.1f' % value
        else:
            value = str(value)
        element = svg.xpath(xpath, namespaces=nsmap)[0]
        element.text = value
    def set_attr(xpath, attr, value):
        element = svg.xpath(xpath, namespaces=nsmap)[0]
        element.set(attr, str(value))
    def set_all_attr(xpath, attr, value):
        elements = svg.xpath(xpath, namespaces=nsmap)
        for element in elements:
            element.set(attr, str(value))
        
    #Locations lookup file.
    locations_file = open(path.join(settings.STATIC_ROOT, 'locations.csv'))
    locations_file.readline()
    locations = {}
    for line in locations_file.readlines():
        data = line.split(',')
        locations[int(data[0])] = {'country': data[3],
                                   'province': data[4],
                                   'district': data[5],
                                   'uid': data[6]}
    locations_file.close()
    
    #Country name for heading.
    set_text('//svg:text[@id="country.name"]', country.name.upper() + ' - %s %04d' % (MONTHNAMES[month-1].upper(), year))
    
    #Monitors table.
    name = '//svg:text[@id="monitor.%d.name"]'
    facilities = '//svg:text[@id="monitor.%d.facilities"]'
    medicines = '//svg:text[@id="monitor.%d.medicines"]'
    interviews = '//svg:text[@id="monitor.%d.interviews"]'
    stories = '//svg:text[@id="monitor.%d.stories"]'
    totals = '//svg:text[@id="monitor.%d.totals"]'
    monitors = dev_models.CommunityWorker.objects.filter(country=country).order_by('first_name')
    most_submissions = -1
    best_monitor = None

    for line in range(22):
        try:
            monitor = monitors[line]
            my_swds = country_valid_swds.filter(community_worker=monitor)
            submissions_count = {}
            for form in forms:
                count = my_swds.filter(submission__form__name=form['name']).count()
                submissions_count[form['name']] = count
            submissions_count['Total'] = sum(submissions_count.values())
            if submissions_count['Total'] > most_submissions:
                best_monitor = monitor
                most_submissions = submissions_count['Total']
            #Get unique facilities.
            facility_submissions = my_swds.filter(submission__form__name='Facility Form').values("submission__facilitysubmission__facility").distinct()
        except:
            monitor = None
        
        if monitor:
            set_text(name % (line), monitor.get_name())
            set_text(facilities % (line), len(facility_submissions))
            set_text(medicines % (line), submissions_count['Medicines Form'])
            set_text(interviews % (line), submissions_count['Tendai Interview'])
            set_text(stories % (line), submissions_count['Tendai Story'])
            set_text(totals % (line), submissions_count['Total'])
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
    count = country_valid_swds.count()
    monitors = dev_models.CommunityWorker.objects.filter(country=country).count()
    per_monitor = float(count)/float(monitors)
    set_text(number, '%0.1f' % (per_monitor))
    set_attr(slider, 'transform', 'translate(%.2f)' % (min(per_monitor, 4.0) * 44.0))
    number = '//svg:text[@id="average.submissions.text"]'
    slider = '//svg:g[@id="average.submissions.slider"]'
    count = valid_swds.count()
    monitors = dev_models.CommunityWorker.objects.count()
    per_monitor = float(count)/float(monitors)
    set_text(number, '%0.1f' % (per_monitor))
    set_attr(slider, 'transform', 'translate(%.2f)' % (min(per_monitor, 4.0) * 44.0))
    
    #Monitor of the month.
    name = '//svg:text[@id="best_monitor.name"]'
    organisation = '//svg:text[@id="best_monitor.organisation"]'
    submissions = '//svg:text[@id="best_monitor.submissions"]'
    photo = '//svg:image[@id="best_monitor.image"]'
    set_text(name, best_monitor.get_name())
    set_text(organisation, 'Organisation: %s' % best_monitor.organisation.name)
    set_text(submissions, country_valid_swds.filter(community_worker=best_monitor).count())
    image = open(path.join(settings.STATIC_ROOT, 'user.jpg'))
    data = b64encode(image.read())
    set_attr(photo, '{%s}href' % (nsmap['xlink']), 'data:image/jpg;base64,%s' % (data))
    
    #Medicines table.
    name = '//svg:text[@id="medicine.%d.name"]'
    stocked = '//svg:text[@id="medicine.%d.stocked"]'
    stockout = '//svg:text[@id="medicine.%d.stockout"]'
    level = '//svg:text[@id="medicine.%d.level"]'
    stockout_days = '//svg:text[@id="medicine.%d.stockout_days"]'
    replenish_days = '//svg:text[@id="medicine.%d.replenish_days"]'
    #medicines = dev_models.Medicine.objects.filter(country=country)
    medicines = country.medicine_set.all().order_by('name')
    for line in range(14):
        try:
            medicine = medicines[line]
        except:
            medicine = None
        
        if medicine:
            set_text(name % (line), medicine.name)
            set_text(stocked % (line), medicine.stocked(country, year, month))
            set_text(stockout % (line), medicine.stock(country, year, month))
            set_text(level % (line), medicine.level(country, year, month))
            set_text(stockout_days % (line), medicine.stockout_days(country, year, month))
            set_text(replenish_days % (line), medicine.replenish_days(country, year, month))
        else:
            set_text(name % (line), ' ')
            set_text(stocked % (line), ' ')
            set_text(stockout % (line), ' ')
            set_text(level % (line), ' ')
            set_text(stockout_days % (line), ' ')
            set_text(replenish_days % (line), ' ')
    
    #Best stories.
    text = '//svg:flowPara[@id="story.%d.text"]'
    story_name = '//svg:text[@id="story.%d.name"]'
    story_date = '//svg:text[@id="story.%d.date"]'
    story_country = '//svg:text[@id="story.%d.country"]'
    image = '//svg:image[@id="story.%d.image"]'
    stories = (1589,1461)
    images = ('356652045028675/1330014282214.jpg',None)
    for number in (0,1):
        try:
            story = dev_models.SubmissionWorkerDevice.objects.get(pk=stories[number])
            set_text(text % (number), story.submission.content.story.story_description)
            set_text(story_name % (number), story.community_worker.get_name())
            set_text(story_date % (number), story.created_date.strftime('%d %B %Y'))
            set_text(story_country % (number), story.community_worker.country.name)
            try:
                image_path = story.submission.orsubmissionmedia_set.all()[1].get_absolute_path()
                image_file = open(image_path)
                data = b64encode(image_file.read())
                set_attr(image % (number), '{%s}href' % (nsmap['xlink']), 'data:image/jpg;base64,%s' % (data))
            except:
                element = svg.xpath(image % (number),namespaces=nsmap)[0]
                element.getparent().remove(element)
        except:
            pass
    
    #Stockout map.
    map_layer = '//svg:g[@id="%s"]'
    #Ugly hack for ends-with which is not supported in XPath.
    district = '//svg:g[substring(@id, string-length(@id) - string-length("%s")+ 1, string-length(@id)) = "%s"]/svg:path'
    #SVG styles.
    STOCKOUT = 'fill:#c11e1e'
    MONITORED = 'fill:#f6e1b9'
    UNMONITORED = 'fill:#fefee9'
    for svg_country in dev_models.Country.objects.all():
        if svg_country != country:
            element = svg.xpath(map_layer % (svg_country.code),namespaces=nsmap)[0]
            element.getparent().remove(element)
        else:
            #Color the map.
            #Ugly hack for ends-with which is not supported in XPath.
            ew='//svg:g[substring(@id, string-length(@id) - string-length("%s")+ 1, string-length(@id)) = "%s"]'
            #Go through all medicine questionnaires and determine stockouts.
            medicine_submissions = country_valid_swds.filter(submission__form__name='Medicines Form')
            districts = set()
            for form in medicine_submissions:
                content = form.submission.content
                try:
                    district_name = locations[form.submission.id]['district']
                except:
                    district_name = 'not_in_locations_file'
                if district_name not in districts:
                    districts.add(district_name)
                    try:
                        set_all_attr(district % (district_name, district_name),
                                     'style', MONITORED)
                    except:
                        print 'MONITORED District failure: %s' % (district_name)
                if content:
                    sections = [section for section in content.nodes() if section.startswith('medicine-')]
                    for section in sections:
                        stock = getattr(content, section).medicine_available
                        if stock == 'No':
                            try:
                                set_all_attr(district % (district_name, district_name),
                                             'style', STOCKOUT)
                            except:
                                print 'STOCKOUT District failure: %s' % (district_name)

    response = HttpResponse(etree.tostring(svg), mimetype='image/svg+xml')
    filename = 'scorecard_%s.svg' % (country.code.lower())
    response['Content-Disposition'] = 'filename=%s' % (filename)
    return response
