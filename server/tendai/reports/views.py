from xml.dom import minidom
from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.template import Template, Context, TemplateDoesNotExist
#from django.template.loader import get_template
#from django.utils import translation

from devices import models as dev_models
from openrosa import models as or_models
#import models

def facilitiesMap(request):
    extra_context = None
    return direct_to_template(request, template='reports/facilities.html', extra_context=extra_context)
    return Http404()

def getTag(dom, name):
    element = dom.getElementsByTagName(name)[0]
    if element:
        if element.firstChild:
            if element.firstChild.nodeType==element.firstChild.TEXT_NODE:
                content = element.firstChild.data
                return content
    return ''

def facilitiesData(request):
    facilities = []
    forms = or_models.ORForm.objects.filter(name='Facility Form')
    submissions = []
    for form in forms:
        submissions.extend(form.orformsubmission_set.all())
    for submission in submissions:
        facility = {}
        dom = minidom.parse(submission.get_full_xml_path())
        gps = getTag(dom, 'facility_location').split()[0:2]
        facility['lat'] = float(gps[0])
        facility['lon'] = float(gps[1])
        facility['name'] = getTag(dom, 'facility_name').replace('\t',' ')
        facility['description'] = getTag(dom, 'facility_description').replace('\t',' ')
        device_id = getTag(dom, 'device_id')
        filename = getTag(dom, 'photo1')
        facility['photo_url'] = reverse('openrosa_media', kwargs={'device_id': device_id, 'filename': filename})
        facilities.append(facility)
    extra_context = {'facilities': facilities}
    return direct_to_template(request, template='reports/facility_data.txt', extra_context=extra_context)
