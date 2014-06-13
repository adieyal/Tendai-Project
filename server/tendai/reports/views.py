import logging
import csv
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import get_template
from django.views.generic.simple import direct_to_template

from devices import models as dev_models
from openrosa import models as or_models
from medicine_analysis import models as med_models

from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.helpers import ThumbnailError
from facility.models import Facility
import datetime
from website.models import Story
from general.utils import Month, count

logger = logging.getLogger(__name__)

def facilities_kml(request):
    facilities = []
    submissions = or_models.ORFormSubmission.objects.filter(form__name='Facility Form', submissionworkerdevice__valid=True)
    extra_context = {
        'submissions': submissions,
        'facilities' : Facility.objects.all()
    }
    return direct_to_template(request, template='reports/facility/data.kml', extra_context=extra_context)

def thumbnail(url, size):
    try:
        return get_thumbnail(url, size).url
    except ThumbnailError, e:
        logger.error("Could not create thumbnail: %s", e.message)
        return ""

def facility_info(request, submission_id):
    submission = get_object_or_404(or_models.ORFormSubmission, pk=submission_id)
    swd = submission.submissionworkerdevice
    photos = or_models.ORSubmissionMedia.objects.filter(
        filename__in=list(submission.content.section_photos)
    )
    extra_context={
        'submission': submission,
        'swd': swd,
        'photos' : photos,
        'thumbnails' : [thumbnail(photo.get_absolute_path(), 'x270') for photo in photos],
    }
    return direct_to_template(request, template='reports/facility/info.html', extra_context=extra_context)

def country(request, country_code):
    month = request.GET.get("month", None)
    year = request.GET.get("year", None)
    
    if month == None or year == None:
        mydate = datetime.datetime.utcnow().replace(day=1) - datetime.timedelta(days=1)
        month = mydate.month
        year = mydate.year
    

    countries = dev_models.Country.objects.all()
    country = dev_models.Country.objects.get(code=country_code)
    workers = dev_models.CommunityWorker.objects.all_active.filter(country=country)

    forms = or_models.ORForm.objects.order_by('name').values('name').distinct()
    extra_context={
        'workers': workers,
        'selected_country': country,
        'countries': countries,
        'forms' : [form["name"] for form in forms],
        'month' : str(month),
        'year' : str(year),
        'mydate' : datetime.datetime(int(year), int(month), 1)
    }

    return direct_to_template(
        request,
        template='reports/country/report.html',
        extra_context=extra_context
    )

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
        def first_swd(self):
            try:
                return self.submission_set.submissions.all().order_by('id')[0]
            except:
                return None 

        @property
        def last_swd(self):
            try:
                return self.submission_set.submissions.all().order_by('-id')[0]
            except:
                return None 

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

        @property
        def first_url(self):
            return self._get_url(self.finder.first_swd or self.finder.current_swd)

        @property
        def last_url(self):
            return self._get_url(self.finder.last_swd or self.finder.current_swd)

    if country: country = dev_models.Country.objects.get(code=country)

    submission_set = SubmissionSet()
    navigator = SWDFinder(submission_set, id)
    router = Router(navigator)

    # Find first unverified entry if none is specified. Redirect there.
    if not id: 
        logger.info("Redirecting current url: %s" % router.current_url)
        redirect(router.current_url)

    swd = navigator.current_swd

    # This might be a little more inefficient since each
    # url needs to be calculated whereas a series of if-thens
    # would be more efficient - but until this is a problem
    # I prefer to go with elegant over gross
    routes = {
        "next" : router.next_url,
        "prev" : router.prev_url,
        "first" : router.first_url,
        "last" : router.last_url,
    }

    request_route = request.GET.get("navigate", None)
    route = routes.get(request_route, None)
    if route:
        logger.info("Redirecting next url: %s" % route)
        return redirect(route)

    if request.user.is_staff and validate and "valid" in request.GET:
        verified = True
        valid = True if must_mark_as_valid() else False
        swd.verified = verified
        swd.valid = valid
        swd.save()
        logger.info("Redirecting validate: %s" % router.next_url)
        return redirect(router.next_url)

    submission = swd.submission
    logger.info(submission.filename)
    versioned_form_name = submission.form.form_id
    general_form_name = versioned_form_name.rsplit('-', 1)[0]
    specific_template = "%s.html" % versioned_form_name
    general_form_template = "%s.html" % general_form_name
    general_template = "general.html"
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

def stockout_reports(request, country_code):
    country = dev_models.Country.objects.get(code=country_code)
    stockouts = med_models.MedicineStockout.objects.filter(
        submission__submissionworkerdevice__community_worker__country=country
    )
    
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachement; filename="stockouts_%s.csv"' % country

    writer = csv.writer(response)
    writer.writerow(["Date", "Medicine", "Facility", "Monitor", "Count"])  
    for stockout in stockouts:
        writer.writerow([
            "%s/%s" % (
                stockout.submission.end_time.year,
                stockout.submission.end_time.strftime("%m"),
            ),
            stockout.medicine,
            stockout.facility,
            stockout.submission.submissionworkerdevice.community_worker,
            "1",
        ])
    return response

def export_reports(request, extra_context=None):
    extra_context = extra_context or {}
    countries = dev_models.Country.objects.all()
    stories = {}
    for country in countries:
        stories[country] = Story.objects.published.filter(country=country)

    extra_context["stories"] = stories.items()

    return direct_to_template(
        request,
        "reports/export_reports.html", extra_context=extra_context
    )

def export_stories(request, country, extra_context=None):
    extra_context = extra_context or {}
    stories = Story.objects.published.filter(country__code=country)
    
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachement; filename="story_%s.csv"' % country

    writer = csv.writer(response)
    writer.writerow(["Submitted Date", "Heading", "Content", "Monitor", "URL on Site"])  
    for story in stories:
        writer.writerow([
            story.submission.end_time,
            story.heading.encode("utf8"),
            story.content.encode("utf8"),
            story.monitor.get_full_name().encode("utf8"),
            story.get_absolute_url()
        ])

    return response
