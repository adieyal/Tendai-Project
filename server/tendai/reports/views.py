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

def facilities_kml(request):
    facilities = []
    submissions = or_models.ORFormSubmission.objects.filter(form__name='Facility Form',submissionworkerdevice__active=True)
    extra_context = {'submissions': submissions}
    return direct_to_template(request, template='reports/facility/data.kml', extra_context=extra_context)

def facility_info(request, submission_id):
    submission = get_object_or_404(or_models.ORFormSubmission, pk=submission_id)
    swd = submission.submissionworkerdevice_set.all()[0]
    extra_context={'submission': submission,
                   'swd': swd}
    return direct_to_template(request, template='reports/facility/info.html', extra_context=extra_context)
