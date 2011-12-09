from xml.dom import minidom
from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.template import Template, Context, TemplateDoesNotExist
from django.views.generic.simple import direct_to_template

from devices import models as dev_models
from openrosa import models as or_models

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
        facility_type = getTag(dom, 'type_of_facility')
        if 'hospital' in facility_type:
            facility['icon'] = 'red_dot'
        elif 'clinic' in facility_type:
            facility['icon'] = 'yellow_dot'
        elif ('pharmacy' in facility_type) or ('dispensary' in facility_type):
            facility['icon'] = 'green_dot'
        else:
            facility['icon'] = 'blue_dot'
        facilities.append(facility)
    extra_context = {'facilities': facilities}
    return direct_to_template(request, template='reports/facility/data.txt', extra_context=extra_context)

def facilitiesKML(request):
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
        facility['id'] = submission.id
        facility_type = getTag(dom, 'type_of_facility')
        if 'hospital' in facility_type:
            facility['icon'] = 'red_dot'
        elif 'clinic' in facility_type:
            facility['icon'] = 'yellow_dot'
        elif ('pharmacy' in facility_type) or ('dispensary' in facility_type):
            facility['icon'] = 'green_dot'
        else:
            facility['icon'] = 'blue_dot'
        facilities.append(facility)
    extra_context = {'facilities': facilities}
    return direct_to_template(request, template='reports/facility/data.kml', extra_context=extra_context)

def facilityInfo(request, submission_id):
    submission = or_models.ORFormSubmission.objects.get(id=submission_id)
    facility = {}
    dom = minidom.parse(submission.get_full_xml_path())
    facility['name'] = getTag(dom, 'facility_name')
    facility['description'] = getTag(dom, 'facility_description')
    facility['doctors'] = getTag(dom, 'facility_doctors')
    facility['nurses'] = getTag(dom, 'facility_nurses')
    facility['coverage'] = getTag(dom, 'facility_coverage')
    device_id = getTag(dom, 'device_id')
    photo = getTag(dom, 'photo1')
    facility['photo_url'] = reverse('openrosa_media', kwargs={'device_id': device_id, 'filename': photo})
    facility_type = getTag(dom, 'type_of_facility')
    if 'hospital' in facility_type:
        facility['icon'] = 'red_dot'
    elif 'clinic' in facility_type:
        facility['icon'] = 'yellow_dot'
    elif ('pharmacy' in facility_type) or ('dispensary' in facility_type):
        facility['icon'] = 'green_dot'
    else:
        facility['icon'] = 'blue_dot'
    extra_context = {'facility': facility}
    return direct_to_template(request, template='reports/facility/info.html', extra_context=extra_context)
