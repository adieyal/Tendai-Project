from django.views.generic.simple import direct_to_template

from openrosa.models import ORForm, ORFormSubmission, ORSubmissionMedia
from general.utils import value_or_none
from xml.dom import minidom
import json

def slider_view(request, template_name="home.html", extra_context=None):
    extra_context = extra_context or {}
    story_forms = ORForm.objects.filter(name="Tendai Story")
    story_submissions =  ORFormSubmission.objects.filter(
        form__in=story_forms,
        submissionworkerdevice__active=True
    ).order_by("-created_date")
    data = []
    for submission in story_submissions:
        xml = minidom.parse(submission.get_full_xml_path())
        media = ORSubmissionMedia.objects.filter(submission=submission)
        media1 = None
        if len(media) > 0:
            media1 = media[0]

	photo = media1
        data.append({
           "title" : value_or_none(xml, "story_title"),
           "description" : value_or_none(xml, "story_description"),
           "photo" : photo.get_absolute_url() if photo else None,
        })
    extra_context["stories"] = data
    return direct_to_template(request, template=template_name, extra_context=extra_context)

def recent_stories(request, template_name="stories.html", num_stories=100, extra_context=None):
    extra_context = extra_context or {}
    story_forms = ORForm.objects.filter(name="Tendai Story")
    story_submissions = ORFormSubmission.objects.filter(
        form__in=story_forms,
        submissionworkerdevice__active=True
    ).order_by("-created_date")[0:num_stories]

    data = []
    for submission in story_submissions:
        xml = minidom.parse(submission.get_full_xml_path())
        media = ORSubmissionMedia.objects.filter(submission=submission)
        media1 = None
        if len(media) > 0: media1 = media[0].get_absolute_path()
        swd = submission.submissionworkerdevice
        # If a story fails to be added for any reason it should just be skipped.
        try:
            data.append({
                    "title" : value_or_none(xml, "story_title"),
                    "description" : value_or_none(xml, "story_description"),
                    "photo" : media1,
                    "date" : submission.created_date,
                    "name" : "%s %s" % (swd.community_worker.first_name, swd.community_worker.last_name),
                    "organisation" : swd.community_worker.organisation,
                    "country" : swd.community_worker.country,
                    "id" : swd.id,
                    })
        except:
            pass
    extra_context["stories"] = data
    return direct_to_template(request, template=template_name, extra_context=extra_context)
