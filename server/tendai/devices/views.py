from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
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
