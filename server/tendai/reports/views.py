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
    submissions = or_models.ORFormSubmission.objects.filter(form__name='Facility Form', submissionworkerdevice__valid=True)
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

def submission(request, id=None, validate=False, country=None, submission_type=None):


    must_mark_as_valid = lambda : request.GET.get("valid", None) == "true"
    must_mark_as_invalid = lambda : request.GET.get("valid", None) == "false"

    class SubmissionSet(object):
        def __init__(self):
            self.filtered = dev_models.SubmissionWorkerDevice.objects.exclude(verified=True)
            if country:
                self.filtered = self.filtered.filter(community_worker__country=country)

            if submission_type:
                self.filtered = self.filtered.filter(submission__form__name=submission_type)
        @property
        def count(self):
            return self.filtered.count()

        @property
        def submissions(self):
            return self.filtered

    class SWDFinder(object):
        def __init__(self, submission_set, id=None): 
            self.submission_set = submission_set
            if not id: id = self._first_unverified_swd.id
            self.id = id

        @property
        def _first_unverified_swd(self):
            # Find first unverified entry if none is specified. Redirect there.
            try:
                return self.submission_set.submissions.order_by('id')[0]
            except:
                return dev_models.SubmissionWorkerDevice.objects.order_by('id')[0]

        @property
        def next_swd(self):
            try:
                return self.submission_set.submissions.filter(pk__gt=self.id).order_by('id')[0]
            except:
                return None 

        @property
        def prev_swd(self):
            try:
                return self.submission_set.submissions.filter(pk__lt=self.id).order_by('-id')[0]
            except:
                return None 

        @property
        def current_swd(self):
            return get_object_or_404(dev_models.SubmissionWorkerDevice, pk=self.id)

    class Router(object):
        def __init__(self, finder):
            self.finder = finder

        @property
        def basic_kwargs(self):
            kwargs = {}
            if country:
                kwargs["country"] = country.code

            if submission_type:
                kwargs["submission_type"] = submission_type
            return kwargs

        def _get_url(self, swd):
            kwargs = self.basic_kwargs
            kwargs["id"] = swd.id
            return reverse('devices_verify_country_swd', kwargs=kwargs)

        @property
        def current_url(self):
            return self._get_url(self.finder.current_swd)

        @property
        def prev_url(self):
            return self._get_url(self.finder.prev_swd or self.finder.current_swd)

        @property
        def next_url(self):
            return self._get_url(self.finder.next_swd or self.finder.current_swd)

    if country: country = dev_models.Country.objects.get(code=country)

    submission_set = SubmissionSet()
    navigator = SWDFinder(submission_set, id)
    router = Router(navigator)

    # Find first unverified entry if none is specified. Redirect there.
    if not id: 
        print "Redirecting current url: %s" % router.current_url
        redirect(router.current_url)

    swd = navigator.current_swd

    if request.GET.get('navigate', None) == 'next':
        print "Redirecting next url: %s" % router.next_url
        return redirect(router.next_url)

    if request.GET.get('navigate', None) == 'prev':
        print "Redirecting prev url: %s" % router.prev_url
        return redirect(router.prev_url)

    if request.user.is_staff and validate and "valid" in request.GET:
        verified = True
        valid = True if must_mark_as_valid() else False
        swd.verified = verified
        swd.valid = valid
        swd.save()
        print "Redirecting validate: %s" % router.next_url
        return redirect(router.next_url)

    submission = swd.submission
    specific_template = "%s.html" % submission.form.form_id        # specific form template
    general_form_template = "%s.html" % submission.form.form_id.rsplit('-', 1)[0]  # general form template
    general_template = "general.html"                              # general template

    for template_name in [specific_template, general_form_template, general_template]:
        try:
            template = get_template("reports/submission/%s" % template_name)
            break
        except TemplateDoesNotExist, e:
            continue

    extra_context={
        'submission': submission,
        'content': submission.content,
        'swd': swd,
        'validate': validate,
        'remaining': submission_set.count 
    }

    if country:
        extra_context['filter'] = country.name
    c = RequestContext(request, extra_context)
    return HttpResponse(template.render(c))
