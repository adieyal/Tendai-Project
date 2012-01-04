from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import get_template
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

def country(request, country_code):
    countries = dev_models.Country.objects.all()
    country = dev_models.Country.objects.get(code=country_code)
    workers = dev_models.CommunityWorker.objects.filter(country=country)
    extra_context={'workers': workers,
                   'selected_country': country,
                   'countries': countries}
    return direct_to_template(request, template='reports/country/report.html', extra_context=extra_context)

def submission(request, id):
    submission = get_object_or_404(or_models.ORFormSubmission, pk=id)
    swd = submission.submissionworkerdevice_set.all()[0]
    form_id = submission.form.form_id
    try:
        # Get specific form template...
        template = get_template('reports/submission/' + form_id + '.html')
    except TemplateDoesNotExist:
        try:
            # ...or get general form template...
            template = get_template('reports/submission/' +
                                    form_id.rsplit('-',1)[0] +
                                    '.html')
        except TemplateDoesNotExist:
            # ...and if all else fails get the general template.
            template = get_template('reports/submission/general.html')
    extra_context={'submission': submission,
                   'content': submission.content,
                   'swd': swd}
    c = RequestContext(request, extra_context)
    return HttpResponse(template.render(c))
