from django.conf import settings
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

class SVGEditor(object):
    def __init__(self, svg):
        self.svg = svg
        self.nsmap = {
            'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
            'cc': 'http://web.resource.org/cc/',
            'svg': 'http://www.w3.org/2000/svg',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'xlink': 'http://www.w3.org/1999/xlink',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
        }

    def xpath(self, xpath):
        return self.svg.xpath(xpath, namespaces=self.nsmap)

    #Helpers for XPath based SVG modification.
    def set_text(self, xpath, value):
        if type(value) == float:
            value = '%.1f' % value
        else:
            value = str(value)
        element = self.xpath(xpath)[0]
        element.text = value

    def set_attr(self, xpath, attr, value):
        element = self.xpath(xpath)[0]
        element.set(attr, str(value))

    def set_all_attr(self, xpath, attr, value):
        elements = self.xpath(xpath)
        for element in elements:
            element.set(attr, str(value))

    def set_image(self, xpath, image):
        attr = "{%s}href" % self.nsmap["xlink"]
        data = b64encode(image.read())
        value = 'data:image/jpg;base64,%s' % data
        self.set_attr(xpath, attr, value)

class MonitorMonthSubmissions(dev_models.MonitorSubmissions):
    def __init__(self, monitor, year, month):
        super(MonitorMonthSubmissions, self).__init__(monitor)
        self.year = year;
        self.month = month;

    @property
    def all_submissions(self):
        return self.monitor.my_submissions.filter(
            created_date__year=self.year,
            created_date__month=self.month
        )

def scorecard(request, country, year=2011, month=12):
    country = get_object_or_404(dev_models.Country, code=country)
    year = int(year)
    month = int(month)

    monitors = dev_models.CommunityWorker.objects.filter(country=country).order_by('first_name')
    valid_swds = dev_models.SubmissionWorkerDevice.objects.filter(
        created_date__year=year, 
        created_date__month=month, 
        verified=True, 
        valid=True
    )
    valid_swds_by_country = valid_swds.filter(community_worker__country=country)

    template = open(path.join(settings.STATIC_ROOT, 'scorecard.svg'))
    svg = etree.XML(template.read())
    
    svgeditor = SVGEditor(svg)
    
    def render_general(country):
        "Country name for heading."
        svgeditor.set_text('//svg:text[@id="country.name"]', country.name.upper() + ' - %s %04d' % (MONTHNAMES[month-1].upper(), year))

    def render_monitors_table():
        "Monitors table."

        name = '//svg:text[@id="monitor.%d.name"]'
        facilities = '//svg:text[@id="monitor.%d.facilities"]'
        medicines = '//svg:text[@id="monitor.%d.medicines"]'
        interviews = '//svg:text[@id="monitor.%d.interviews"]'
        stories = '//svg:text[@id="monitor.%d.stories"]'
        totals = '//svg:text[@id="monitor.%d.totals"]'

        def render_monitor_row(monitor, line):
            if monitor:
                monitor_submissions = MonitorMonthSubmissions(monitor, year, month)
                svgeditor.set_text(name % (line), monitor.get_name())
                svgeditor.set_text(facilities % (line), monitor_submissions.facility_submissions.count())
                svgeditor.set_text(medicines % (line), monitor_submissions.medicines_submissions.count())
                svgeditor.set_text(interviews % (line), monitor_submissions.interview_submissions.count())
                svgeditor.set_text(stories % (line), monitor_submissions.story_submissions.count())
                svgeditor.set_text(totals % (line), monitor_submissions.all_submissions.count())
            else:
                svgeditor.set_text(name % (line), ' ')
                svgeditor.set_text(facilities % (line), ' ')
                svgeditor.set_text(medicines % (line), ' ')
                svgeditor.set_text(interviews % (line), ' ')
                svgeditor.set_text(stories % (line), ' ')
                svgeditor.set_text(totals % (line), ' ')

        [render_monitor_row(monitor, line) for line, monitor in enumerate(monitors)]
        # Fill out the rest of the table with blanks
        [render_monitor_row(None, line) for line in range(len(monitors), 22)]

    def render_submission_sliders():
        #Submissions sliders.
        country_number = '//svg:text[@id="country.submissions.text"]'
        country_slider = '//svg:g[@id="country.submissions.slider"]'
        overall_number = '//svg:text[@id="average.submissions.text"]'
        overall_slider = '//svg:g[@id="average.submissions.slider"]'

        avg_per_monitor = lambda monitors, submissions : float(submissions) / float(monitors)

        def slider_update(monitors, submissions, number, slider):
            per_monitor = avg_per_monitor(monitors, submissions)
            svgeditor.set_text(number, '%0.1f' % (per_monitor))
            svgeditor.set_attr(slider, 'transform', 'translate(%.2f)' % (min(per_monitor, 4.0) * 44.0))


        country_submission_count = valid_swds_by_country.count()
        num_country_monitors = dev_models.CommunityWorker.objects.filter(country=country).count()
        overall_submissions_count = valid_swds.count()
        total_monitors = dev_models.CommunityWorker.objects.count()

        slider_update(num_country_monitors, country_submission_count, country_number, country_slider)
        slider_update(total_monitors, overall_submissions_count, overall_number, overall_slider)

    def render_monitor_of_the_month():
        name = '//svg:text[@id="best_monitor.name"]'
        organisation = '//svg:text[@id="best_monitor.organisation"]'
        submissions = '//svg:text[@id="best_monitor.submissions"]'
        photo = '//svg:image[@id="best_monitor.image"]'

        monitors_submissions = (MonitorMonthSubmissions(monitor, year, month) for monitor in monitors)
        submission_counts = (s.all_submissions.count() for s in monitors_submissions)
        best_monitor = sorted(zip(submission_counts, monitors))[-1][1]
        
        #Monitor of the month.
        svgeditor.set_text(name, best_monitor.get_name())
        svgeditor.set_text(organisation, 'Organisation: %s' % best_monitor.organisation.name)
        svgeditor.set_text(submissions, valid_swds_by_country.filter(community_worker=best_monitor).count())

        image = open(path.join(settings.STATIC_ROOT, 'user.jpg'))
        svgeditor.set_image(photo, image)

    def render_medicines_table():
        #Medicines table.
        name = '//svg:text[@id="medicine.%d.name"]'
        stocked = '//svg:text[@id="medicine.%d.stocked"]'
        stockout = '//svg:text[@id="medicine.%d.stockout"]'
        level = '//svg:text[@id="medicine.%d.level"]'
        stockout_days = '//svg:text[@id="medicine.%d.stockout_days"]'
        replenish_days = '//svg:text[@id="medicine.%d.replenish_days"]'
        medicines = country.medicine_set.all().order_by('name')

        def render_medicines_row(medicine, line):
            if medicine:
                svgeditor.set_text(name % (line), medicine.name)
                svgeditor.set_text(stocked % (line), medicine.stocked(country, year, month))
                svgeditor.set_text(stockout % (line), medicine.stock(country, year, month))
                svgeditor.set_text(level % (line), medicine.level(country, year, month))
                svgeditor.set_text(stockout_days % (line), medicine.stockout_days(country, year, month))
                svgeditor.set_text(replenish_days % (line), medicine.replenish_days(country, year, month))
            else:
                svgeditor.set_text(name % (line), ' ')
                svgeditor.set_text(stocked % (line), ' ')
                svgeditor.set_text(stockout % (line), ' ')
                svgeditor.set_text(level % (line), ' ')
                svgeditor.set_text(stockout_days % (line), ' ')
                svgeditor.set_text(replenish_days % (line), ' ')


        [render_medicines_row(medicine, line) for line, medicine in enumerate(medicines)]
        # Fill out the rest of the table with blanks
        [render_medicines_row(None, line) for line in range(len(medicines), 14)]

    def render_stories():
        #Best stories.
        text = '//svg:flowPara[@id="story.%d.text"]'
        story_name = '//svg:text[@id="story.%d.name"]'
        story_date = '//svg:text[@id="story.%d.date"]'
        story_country = '//svg:text[@id="story.%d.country"]'
        image = '//svg:image[@id="story.%d.image"]'
        stories = (1589, 1461)
        images = ('356652045028675/1330014282214.jpg', None)

        for number in (0, 1):
            try:
                story = dev_models.SubmissionWorkerDevice.objects.get(pk=stories[number])
                svgeditor.set_text(text % (number), story.submission.content.story.story_description)
                svgeditor.set_text(story_name % (number), story.community_worker.get_name())
                svgeditor.set_text(story_date % (number), story.created_date.strftime('%d %B %Y'))
                svgeditor.set_text(story_country % (number), story.community_worker.country.name)
                try:
                    image_path = story.submission.orsubmissionmedia_set.all()[1].get_absolute_path()
                    image_file = open(image_path)
                    svgeditor.set_image(image % number, image_file)
                except:
                    element = svgeditor.xpath(image % (number))[0]
                    element.getparent().remove(element)
            except:
                pass

    def render_stockout_map():

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

        #Stockout map.
        map_layer = '//svg:g[@id="%s"]'
        #Ugly hacks for ends-with which is not supported in XPath.
        district = '//svg:g[substring(@id, string-length(@id) - string-length("%s")+ 1, string-length(@id)) = "%s"]/svg:path'
        ew = '//svg:g[substring(@id, string-length(@id) - string-length("%s")+ 1, string-length(@id)) = "%s"]'

        #SVG styles.
        STOCKOUT = 'fill:#c11e1e'
        MONITORED = 'fill:#f6e1b9'
        UNMONITORED = 'fill:#fefee9'

        def remove_country(country):
            element = svgeditor.xpath(map_layer % (country.code))[0]
            element.getparent().remove(element)

        [ # All countries are present in the SVG - remove the irrelevant ones
            remove_country(svg_country) 
            for svg_country in dev_models.Country.objects.all() 
            if svg_country != country
        ]

        #Color the map.
        #Go through all medicine questionnaires and determine stockouts.
        medicine_submissions = valid_swds_by_country.filter(submission__form__name='Medicines Form')
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
                    svgeditor.set_all_attr(district % (district_name, district_name),
                                 'style', MONITORED)
                except:
                    print 'MONITORED District failure: %s' % (district_name)
            if content:
                sections = [section for section in content.nodes() if section.startswith('medicine-')]
                for section in sections:
                    stock = getattr(content, section).medicine_available
                    if stock == 'No':
                        try:
                            svgeditor.set_all_attr(district % (district_name, district_name),
                                         'style', STOCKOUT)
                        except:
                            print 'STOCKOUT District failure: %s' % (district_name)

    
    #facility_submissions = my_swds.filter(submission__form__name='Facility Form').values("submission__facilitysubmission__facility").distinct()

    render_general(country)
    render_monitors_table()
    render_submission_sliders()
    render_monitor_of_the_month()
    render_medicines_table()
    render_stories()
    render_stockout_map()

    response = HttpResponse(etree.tostring(svg), mimetype='image/svg+xml')
    filename = 'scorecard_%s.svg' % (country.code.lower())
    response['Content-Disposition'] = 'filename=%s' % (filename)
    return response
