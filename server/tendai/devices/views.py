import os
from xml.dom import minidom
from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404
from django.template import Template, Context
from django.db.models import Q

from openrosa import models as or_models
from openrosa import forms
import models

def formList(request):
    if request.method != "GET":
        raise Http404

    forms = or_models.ORForm.objects.filter(active=True)

    if "deviceid" in request.GET:
        try:
            worker = models.CommunityWorker.objects.get(device__device_id=request.GET["deviceid"])
            if worker.country != None:
                forms = forms.filter(Q(countryform__country=worker.country) | Q(countryform=None))

        except models.CommunityWorker.DoesNotExist:
            pass
        
    url = "http://" + request.get_host() + reverse("openrosa_formxml") + "?formId="
    context = Context({
        "forms" : forms,
        "url" : url,
    })
    template = Template("""
    <xforms xmlns="http://openrosa.org/xforms/xformsList"> 
        {% for form in forms %}
        <xform>
            <formID>{{ form.form_id }}</formID>
            <name>{{ form.name }}</name> 
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

def view_training_survey(request, xml, template_name="forms/training_survey.html", extra_context=None):
    extra_context = extra_context or {}
    root = xml.getElementsByTagName("data")[0]
    for leaf in get_leaf_nodes(root):
        if leaf.firstChild:
            extra_context[leaf.tagName] = leaf.firstChild.nodeValue

    return direct_to_template(request, template=template_name, extra_context=extra_context)

form_view_lookup = {
    "Training Survey" : {
        "0.8" : view_training_survey,
        "0.9" : view_training_survey,
        "0.10" : view_training_survey,
    }
}
