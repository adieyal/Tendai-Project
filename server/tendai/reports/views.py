from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
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

def submission(request, id=None, validate=False, country=None):
    if country:
        country = dev_models.Country.objects.get(code=country)
        filtered = dev_models.SubmissionWorkerDevice.objects.exclude(verified=True).filter(community_worker__country=country)
    else:
        filtered = dev_models.SubmissionWorkerDevice.objects.exclude(verified=True)
    remaining = filtered.count()
    # Find first unverified entry if none is specified. Redirect there.
    if not id:
        try:
            first_swd = filtered.order_by('id')[0]
        except:
            first_swd = dev_models.SubmissionWorkerDevice.objects.order_by('id')[0]
        if country:
            return redirect(reverse('devices_verify_country_swd', kwargs={'id': first_swd.id, 'country': country.code}))
        return redirect(reverse('devices_verify_swd', kwargs={'id': first_swd.id}))
    swd = get_object_or_404(dev_models.SubmissionWorkerDevice, pk=id)
    submission = swd.submission
    # Navigation options.
    try:
        next_swd = filtered.filter(pk__gt=id).order_by('id')[0]
    except:
        next_swd = swd
    try:
        prev_swd = filtered.filter(pk__lt=id).order_by('-id')[0]
    except:
        prev_swd = swd
    if country:
        next_url = reverse('devices_verify_country_swd', kwargs={'id': next_swd.id, 'country': country.code})
        prev_url = reverse('devices_verify_country_swd', kwargs={'id': prev_swd.id, 'country': country.code})
    else:
        next_url = reverse('devices_verify_swd', kwargs={'id': next_swd.id})
        prev_url = reverse('devices_verify_swd', kwargs={'id': prev_swd.id})
    if country:
        filtered = filtered.filter(community_worker__country=country)
    if request.GET.get('navigate', None)=='next':
        return redirect(next_url)
    if request.GET.get('navigate', None)=='prev':
        return redirect(prev_url)
    # Validation actions.
    if not request.user.is_staff:
        validate = False
    if validate:
        if request.GET.get('valid', None)=='true':
            swd.verified = True
            swd.valid = True
            swd.save()
            return redirect(next_url)
        if request.GET.get('valid', None)=='false':
            swd.verified = True
            swd.valid = False
            swd.save()
            return redirect(next_url)

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
                   'swd': swd,
                   'validate': validate,
                   'remaining': remaining }
    if country:
        extra_context['filter'] = country.name
    c = RequestContext(request, extra_context)
    return HttpResponse(template.render(c))
