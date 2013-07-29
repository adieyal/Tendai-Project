from os import path
from base64 import b64encode
from lxml import etree
import devices.models as dev_models
from facility.models import Coordinates, SubmissionCoordinateFactory
import facility.models as fac_models
import models
from medicine_analysis.models import MedicineStockout
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

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
            'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
            'tendai': "http://tendai.medicinesinfohub.net/namespaces/tendai",
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

    def set_flowtext(self, xpath, value):
        """
        Add flow paragraphs to a flow region.
        xpath should point to the parent element
        i.e. the flowRoot
        """
        lines = str(value).split("\n")
        element = self.xpath(xpath)[0]
        for line in lines:
            para = etree.Element("flowPara")
            para.text = line
            element.append(para)

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
    def __init__(self, monitor, month):
        super(MonitorMonthSubmissions, self).__init__(monitor)
        self.month = month;

    @property
    def all_submissions(self):
        return self.monitor.my_submissions.filter(
            created_date__year=self.month.year,
            created_date__month=self.month.month
        )

class ScoreCardGenerator(object):
    def __init__(self, template, resource_dir):

        self.template = template
        self.resource_dir = resource_dir
        self.svg = etree.XML(self.template.read())
        
        self.svgeditor = SVGEditor(self.svg)
    
    def render_general(self, country, month):
        "Country name for heading."
        month_name = month.month_as_str.upper()

        self.svgeditor.set_text(
            '//svg:text[@id="country.name"]', 
            country.name.upper() + ' - %s %04d' % (month_name, month.year)
        )

    def render_monitors_table(self, monitors, month):
        "Monitors table."

        name = '//svg:text[@id="monitor.%d.name"]'
        facilities = '//svg:text[@id="monitor.%d.facilities"]'
        medicines = '//svg:text[@id="monitor.%d.medicines"]'
        interviews = '//svg:text[@id="monitor.%d.interviews"]'
        stories = '//svg:text[@id="monitor.%d.stories"]'
        totals = '//svg:text[@id="monitor.%d.totals"]'

        def render_monitor_row(monitor, line):
            if monitor:
                monitor_submissions = MonitorMonthSubmissions(monitor, month)
                self.svgeditor.set_text(name % (line), monitor.get_name())
                self.svgeditor.set_text(facilities % (line), monitor_submissions.facility_submissions.count())
                self.svgeditor.set_text(medicines % (line), monitor_submissions.medicines_submissions.count())
                self.svgeditor.set_text(interviews % (line), monitor_submissions.interview_submissions.count())
                self.svgeditor.set_text(stories % (line), monitor_submissions.story_submissions.count())
                self.svgeditor.set_text(totals % (line), monitor_submissions.all_submissions.count())
            else:
                self.svgeditor.set_text(name % (line), ' ')
                self.svgeditor.set_text(facilities % (line), ' ')
                self.svgeditor.set_text(medicines % (line), ' ')
                self.svgeditor.set_text(interviews % (line), ' ')
                self.svgeditor.set_text(stories % (line), ' ')
                self.svgeditor.set_text(totals % (line), ' ')

        [render_monitor_row(monitor, line) for line, monitor in enumerate(monitors)]
        # Fill out the rest of the table with blanks
        [render_monitor_row(None, line) for line in range(len(monitors), 22)]

    def render_submission_sliders(self, monitors, valid_swds, valid_swds_by_country):
        #Submissions sliders.
        country_number = '//svg:text[@id="country.submissions.text"]'
        country_slider = '//svg:g[@id="country.submissions.slider"]'
        overall_number = '//svg:text[@id="average.submissions.text"]'
        overall_slider = '//svg:g[@id="average.submissions.slider"]'

        avg_per_monitor = lambda num_monitors, submissions : float(submissions) / float(num_monitors)

        def slider_update(num_monitors, submissions, number, slider):
            per_monitor = avg_per_monitor(num_monitors, submissions)
            self.svgeditor.set_text(number, '%0.1f' % (per_monitor))
            self.svgeditor.set_attr(slider, 'transform', 'translate(%.2f)' % (min(per_monitor, 4.0) * 44.0))


        country_submission_count = valid_swds_by_country.count()
        num_country_monitors = monitors.count()
        overall_submissions_count = valid_swds.count()
        total_monitors = dev_models.CommunityWorker.objects.count()

        slider_update(num_country_monitors, country_submission_count, country_number, country_slider)
        slider_update(total_monitors, overall_submissions_count, overall_number, overall_slider)

    def render_monitor_of_the_month(self, monitors, valid_swds_by_country, month):
        name = '//svg:text[@id="best_monitor.name"]'
        organisation = '//svg:text[@id="best_monitor.organisation"]'
        submissions = '//svg:text[@id="best_monitor.submissions"]'
        photo = '//svg:image[@id="best_monitor.image"]'

        monitors_submissions = (MonitorMonthSubmissions(monitor, month) for monitor in monitors)
        submission_counts = (s.all_submissions.count() for s in monitors_submissions)
        best_monitor = sorted(zip(submission_counts, monitors))[-1][1]
        
        #Monitor of the month.
        self.svgeditor.set_text(name, best_monitor.get_name())
        self.svgeditor.set_text(organisation, 'Organisation: %s' % best_monitor.organisation.name)
        self.svgeditor.set_text(submissions, valid_swds_by_country.filter(community_worker=best_monitor).count())

        #image_path = story.submission.orsubmissionmedia_set.all()[1].get_absolute_path()
        #image_file = open(image_path)
        #self.svgeditor.set_image(image % number, image_file)

        monitor_profiles = dev_models.SubmissionWorkerDevice.objects.all_valid.filter(
            submission__form__name='Monitor Profile',
            community_worker=best_monitor
        )
        image = open(path.join(self.resource_dir, 'user.jpg'))
        if monitor_profiles.count() > 0:
            try:
                profile = list(monitor_profiles)[-1]
                image_path = profile.submission.orsubmissionmedia_set.all()[0].get_absolute_path()
                image = open(image_path)
            except:
                import traceback
                pass
                
        self.svgeditor.set_image(photo, image)

    def render_medicines_table(self, country, month):
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
                self.svgeditor.set_text(name % (line), medicine.name)
                self.svgeditor.set_text(stocked % (line), medicine.stocked(country, month) or '-')
                self.svgeditor.set_text(stockout % (line), medicine.stock(country, month) or '-')
                self.svgeditor.set_text(level % (line), medicine.level(country, month) or '-')
                self.svgeditor.set_text(stockout_days % (line), medicine.stockout_days(country, month) or '-')
                self.svgeditor.set_text(replenish_days % (line), medicine.replenish_days(country, month) or '-')
            else:
                self.svgeditor.set_text(name % (line), ' ')
                self.svgeditor.set_text(stocked % (line), ' ')
                self.svgeditor.set_text(stockout % (line), ' ')
                self.svgeditor.set_text(level % (line), ' ')
                self.svgeditor.set_text(stockout_days % (line), ' ')
                self.svgeditor.set_text(replenish_days % (line), ' ')


        [render_medicines_row(medicine, line) for line, medicine in enumerate(medicines)]
        # Fill out the rest of the table with blanks
        [render_medicines_row(None, line) for line in range(len(medicines), 14)]

    def render_stories(self, country, month, swds):
        #Best stories.
        text_delete = '//svg:flowPara[@id="story.%d.text"]'
        text = '//svg:flowRoot[@id="story.%d.textroot"]'
        story_name = '//svg:text[@id="story.%d.name"]'
        story_date = '//svg:text[@id="story.%d.date"]'
        story_country = '//svg:text[@id="story.%d.country"]'
        image = '//svg:image[@id="story.%d.image"]'

        story_submissions = swds.filter(
            submission__form__name='Tendai Story'
        ).exclude(scorecardstory=None)

        stories = models.ScorecardStory.objects.filter(
            submission_worker_device__created_date__year=month.year,
            submission_worker_device__created_date__month=month.month,
            submission_worker_device__community_worker__country=country
        )
        images = ('356652045028675/1330014282214.jpg', None)

        for number, story in enumerate(stories):
            placeholder_text = self.svgeditor.xpath(text_delete % (number))[0]
            placeholder_text.getparent().remove(placeholder_text)

            community_worker = story.submission_worker_device.community_worker
            submission = story.submission_worker_device.submission
            self.svgeditor.set_flowtext(text % number, story.edited_text)
            self.svgeditor.set_text( story_name % (number), community_worker.get_name())

            self.svgeditor.set_text(
                story_date % (number),
                story.submission_worker_device.created_date.strftime('%d %B %Y')
            )

            self.svgeditor.set_text(story_country % (number), community_worker.country.name)
            try:
                image_path = submission.orsubmissionmedia_set.all()[0].get_absolute_path()
                image_file = open(image_path)
                self.svgeditor.set_image(image % number, image_file)
            except:
                element = self.svgeditor.xpath(image % (number))[0]
                element.getparent().remove(element)

    def render_stockout_text(self, country, month):
        flow_root = '//svg:flowRoot[@id="stockouts.text"]'
        flow_para = '//svg:flowPara[@id="stockouts.text.remove"]'

        flow_para_element = self.svgeditor.xpath(flow_para)[0]
        flow_para_element.getparent().remove(flow_para_element)

        stockouts = MedicineStockout.objects.filter(
            submission__end_time__year=month.year,
            submission__end_time__month=month.month,
            submission__submissionworkerdevice__community_worker__country=country,
        ).order_by("facility", "medicine")

        stockout_text = ""
        current_facility = None
        medicines = []
        stockouts_dict = defaultdict(set)
        for stockout in stockouts:
            stockouts_dict[stockout.facility.name].add(stockout.medicine.name)
            medicines.append(stockout.medicine.name) 

        flow_root_element = self.svgeditor.xpath(flow_root)[0]
        for facility, medicines in sorted(stockouts_dict.items(), key=lambda x : x[0]):
            new_para = etree.Element("flowPara")

            bold_span = etree.Element("flowSpan")
            bold_span.text = "%s: " % facility
            bold_span.set("style", "font-weight:bold")
            new_para.append(bold_span)

            medicines_str = ", ".join(sorted(medicines))
            normal_span = etree.Element("flowSpan")
            normal_span.text = medicines_str
            new_para.append(normal_span)

            flow_root_element.append(new_para)
        
    def render_stockout_map(self, country, valid_swds_by_country):

        #Stockout map.
        map_layer = '//svg:g[@id="%s"]'
        #Ugly hacks for ends-with which is not supported in XPath.

        district = '//svg:g[substring(@id, string-length(@id) - string-length("%s")+ 1, string-length(@id)) = "%s"]/svg:path'
        ew = '//svg:g[substring(@id, string-length(@id) - string-length("%s")+ 1, string-length(@id)) = "%s"]'

        def remove_country(country):
            layers = self.svgeditor.xpath(map_layer % country.code)
            if len(layers) == 0:
                return
            element = layers[0]
            element.getparent().remove(element)

        def remove_unwanted_countries(svg_country):
            [ # All countries are present in the SVG - remove the irrelevant ones
                remove_country(svg_country) 
                for svg_country in dev_models.Country.objects.all() 
                if svg_country != country
            ]

        remove_unwanted_countries(country)

        class MapBBox(object):
            def __init__(self, element):
                self.element = element

            def _attrib(self, key):
                return float(self.element.attrib[key])

            @property
            def width(self):
                return self._attrib("width")

            @property
            def height(self):
                return self._attrib("height")

            @property
            def x(self):
                return self._attrib("x")

            @property
            def y(self):
                return self._attrib("y")

        class MapGroup(object):
            def __init__(self, element):
                self.element = element 
                self.namespace = "http://tendai.medicinesinfohub.net/namespaces/tendai"

            def get_attr(self, attr):
                return self.element.attrib["{%s}%s" % (self.namespace, attr)]

            @property
            def minx(self):
                return float(self.get_attr("minx"))

            @property
            def maxx(self):
                return float(self.get_attr("maxx"))

            @property
            def miny(self):
                return float(self.get_attr("miny"))

            @property
            def maxy(self):
                return float(self.get_attr("maxy"))

        class StockoutSpotFactory(object):
            def __init__(self, parent, map_group, map_box):
                self.map_group = map_group
                self.map_box = map_box
                self.parent = parent

            def convert_to_pixels(self, coordinates):
                c_width = map_group.maxx - map_group.minx
                c_height = map_group.maxy - map_group.miny
                
                adj_x = coordinates.longitude - map_group.minx
                adj_y = coordinates.latitude - map_group.miny
                
                ratio_x = adj_x / c_width
                # to compensate for the origin at the top left
                ratio_y = 1 - adj_y / c_height

                p_x = map_box.width * ratio_x + map_box.x
                p_y = map_box.height * ratio_y + map_box.y
                
                return (p_x, p_y)

            def add_spot(self, coordinates, stockout=True):
                x, y = self.convert_to_pixels(coordinates)
                if x < map_box.x or x > (map_box.x + map_box.width): return
                if y < map_box.y or y > (map_box.y + map_box.height): return
                circle = etree.Element("circle")
                circle.attrib["cx"] = "%s" % x
                circle.attrib["cy"] = "%s" % y
                circle.attrib["r"] = "10"
                #circle.attrib["style"] = "fill:#c11e1e;fill-opacity:0.56086957"
                if stockout:
                    circle.attrib["style"] = "fill:url(#red_gradient);fill-opacity:0.96086957"
                else:
                    circle.attrib["style"] = "fill:url(#green_gradient);fill-opacity:0.96086957"
                self.parent.append(circle)

        #Color the map.
        #Go through all medicine questionnaires and determine stockouts.
        medicine_submissions = valid_swds_by_country.filter(submission__form__name='Medicines Form')
        facility_submissions = dev_models.SubmissionWorkerDevice.objects.all_valid.filter(
            submission__form__name='Facility Form',
            community_worker__country=country
            
        )
        districts = set()
        xp_map_group = '//svg:g[@id="%s"]/svg:g[@id="%s_map"]' % (country.code, country.code)
        xp_box = '//svg:g[@id="%s"]/svg:rect[@id="%s_box"]' % (country.code, country.code)

        map_group = MapGroup(self.svgeditor.xpath(xp_map_group)[0])
        map_box = MapBBox(self.svgeditor.xpath(xp_box)[0])
        spot_factory = StockoutSpotFactory(map_group.element.getparent(), map_group, map_box)

        for form in facility_submissions:
            content = form.submission.content
            if content:
                coordinates = SubmissionCoordinateFactory.parse(content.section_location.facility_location)
                spot_factory.add_spot(coordinates, False)

        for form in medicine_submissions:
            content = form.submission.content
            
            if content:
                coordinates = SubmissionCoordinateFactory.parse(content.section_general.gps)
                sections = [section for section in content.nodes() if section.startswith('medicine-')]
                for section in sections:
                    stock = getattr(content, section).medicine_available
                    if stock == 'No':
                        spot_factory.add_spot(coordinates) 
                        break
                #else:
                #    spot_factory.add_spot(coordinates, False) 
    def render_all(self, country, month):
        monitors = dev_models.CommunityWorker.objects.all_active.filter(country=country).order_by('first_name')
        valid_swds = dev_models.SubmissionWorkerDevice.objects.all_valid.filter(
            created_date__year=month.year, 
            created_date__month=month.month, 
        )
        valid_swds_by_country = valid_swds.filter(community_worker__country=country)

        self.render_general(country, month)
        self.render_monitors_table(monitors, month)
        self.render_submission_sliders(monitors, valid_swds, valid_swds_by_country)
        self.render_monitor_of_the_month(monitors, valid_swds_by_country, month)
        self.render_medicines_table(country, month)
        self.render_stories(country, month, valid_swds_by_country)
        self.render_stockout_map(country, valid_swds_by_country)
        self.render_stockout_text(country, month)

        return etree.tostring(self.svg)
