import os
from xml.dom import minidom
from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.template import Template, Context, TemplateDoesNotExist
from django.template.loader import get_template
from django.db.models import Q
from django.utils import translation

from openrosa import models as or_models
from openrosa import forms
import models

def formXml(request, country_code, language=None):
    if request.method == "GET":
        form_id = request.GET["formId"]
        
        country = get_object_or_404(models.Country, code=country_code)
        form = get_object_or_404(or_models.ORForm, form_id=form_id, countryform__countries=country)
        countryform_language = form.countryform_set.all()[0].language
        template_name = os.path.join('surveys', form.form_id + '.xml')
        
        try:
            template = get_template(template_name)
        except TemplateDoesNotExist:
            raise Http404
        
        context = Context({
            "country" : country,
            "districts" : models.District.objects.filter(country=country).order_by('name'),
            "medicines" : models.Medicine.objects.filter(countries=country).order_by('name'),
            "currencies" : models.Currency.objects.all(),
        })
        cur_language = translation.get_language()
        if language:
            translation.activate(language)
        elif countryform_language:
            translation.activate(countryform_language.code)
        else:
            translation.activate(country.language.code)
        data = template.render(context)
        translation.activate(cur_language)
        response = HttpResponse(data, mimetype='text/xml; charset=utf-8')
        return response
    raise Http404

def formList(request):
    if request.method != "GET":
        raise Http404

    active_forms = or_models.ORForm.objects.filter(active=True)
    country = None
    
    if "deviceid" in request.GET:
        try:
            worker = models.CommunityWorker.objects.get(device__device_id=request.GET["deviceid"])
            if worker.country != None:
                country = worker.country
        except models.CommunityWorker.DoesNotExist:
            pass
    
    if not country:
        try:
            country = models.Country.objects.get_default()
        except models.Country.DoesNotExist:
            raise Http404
    
    country_forms = active_forms.filter(countryform__countries=country)
    url = "http://" + request.get_host() + reverse("openrosa_dynamic_formxml", kwargs={"country_code" : country.code}) +"?formId="
    context = Context({
        "country" : country,
        "forms" : country_forms,
        "url" : url,
    })
    template = Template("""
    <xforms xmlns="http://openrosa.org/xforms/xformsList"> 
        {% for form in forms %}
        <xform>
            <formID>{{ form.form_id }}</formID>
            <name>{{ country.name}} {{ form.name }} ({{ country.language.name }})</name> 
            <majorMinorVersion>{{ form.majorminorversion }}</majorMinorVersion> 
            <descriptionText>{{ form.description }}</descriptionText> 
            <downloadUrl>{{ url }}{{ form.form_id }}</downloadUrl>
        </xform>
        {% endfor %}
    </xforms>
    """)
    response = HttpResponse(template.render(context), mimetype='text/xml; charset=utf-8')
    response["X-OpenRosa-Version"] = "1.0"
    return response

def get_view(form):
    if not form.name in form_view_lookup:
        return None

    if not form.majorminorversion in form_view_lookup[form.name]:
        return None

    return form_view_lookup[form.name][form.majorminorversion]

def view_swd(request, id=None):
    if request.method == "GET":
        swd = get_object_or_404(models.SubmissionWorkerDevice, pk=id)
        form = swd.submission.form
        path = os.path.join(settings.OPENROSA_SUBMISSIONS_DIR, swd.submission.filename)
        if not os.path.exists(path):
            raise Http404
        form_view = get_view(form)
        if not form_view:
            return HttpResponse(open(path).read(), mimetype='text/xml; charset=utf-8')
        else:
            xml = minidom.parse(path)
            return form_view(request, xml)
    raise Http404

def get_leaf_nodes(root):
    num_children = 0
    for child in [child for child in root.childNodes 
        if child.nodeType != minidom.Element.TEXT_NODE]:
            num_children += 1
            for descendent in get_leaf_nodes(child):
                yield descendent
    if num_children == 0:
        yield root

def get_leaf_map(xml, root_name):
    root = xml.getElementsByTagName(root_name)[0]
    m = {}
    for leaf in get_leaf_nodes(root):
        if leaf.firstChild:
            m[leaf.tagName] = leaf.firstChild.nodeValue
    return m

def view_training_survey(request, xml, template_name="forms/training_survey.html", extra_context=None):
    extra_context = extra_context or {}
    m = get_leaf_map(xml, "data")
    extra_context.update(m)

    return direct_to_template(request, template=template_name, extra_context=extra_context)

def view_facility(request, xml, template_name="forms/facility_survey.html", extra_context=None):
    extra_context = extra_context or {}
    extra_context["main"] = get_leaf_map(xml, "data")
    extra_context["section_name"] = get_leaf_map(xml, "section_name")
    extra_context["section_contact"] = get_leaf_map(xml, "section_contact")
    extra_context["section_respondent"] = get_leaf_map(xml, "section_respondent")
    extra_context["section_location"] = get_leaf_map(xml, "section_location")
    extra_context["section_photos"] = get_leaf_map(xml, "section_photos")
    extra_context["section_general"] = get_leaf_map(xml, "section_general")
    extra_context["section_services"] = get_leaf_map(xml, "section_services")
    extra_context["section_medicines_list"] = get_leaf_map(xml, "section_medicines_list")
    extra_context["section_comments"] = get_leaf_map(xml, "section_comments")

    return direct_to_template(request, template=template_name, extra_context=extra_context)

def view_interview_survey(request, xml, template_name="forms/interview_survey.html", extra_context=None):
    extra_context = extra_context or {}
    extra_context["main"] = get_leaf_map(xml, "data")

    return direct_to_template(request, template=template_name, extra_context=extra_context)

def view_submissions(request, template_name="devices/submissions_overview.html", extra_context=None):
    extra_context = extra_context or {}
    extra_context["organisations"] = models.Organisation.objects.all()
    return direct_to_template(request, template=template_name, extra_context=extra_context)

form_view_lookup = {
    "Training Survey" : {
        "0.8" : view_training_survey,
        "0.9" : view_training_survey,
        "0.10" : view_training_survey,
    },
    "Tendai Interview" : {
        "0.8" : view_interview_survey,
    },
    "RSA Facility" : {
        "0.17" : view_facility,
    },
    "Zimbabwe Facility" : {
        "0.1" : view_facility,
    }
}
