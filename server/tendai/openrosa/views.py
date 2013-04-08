import os
import tempfile
from xml.dom import minidom

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseRedirect, Http404

import models
import forms
from general.utils import value_or_none
import signals
import logging

logger = logging.getLogger(__name__)

def formXml(request):
    if request.method == "GET":
        form_id = request.GET["formId"] 
        orform = get_object_or_404(models.ORForm, form_id=form_id)
        form_path = os.path.join(settings.OPENROSA_FORMS_DIR, orform.get_filename())
        if not os.path.exists(form_path):
            raise Http404
        f = open(form_path)
        response = HttpResponse(f.read(), mimetype='text/xml; charset=utf-8')
        return response
    raise Http404

def formList(request):
    if request.method != "GET":
        raise Http404

    if "deviceid" in request.GET:
        print request.GET["deviceid"]
        
    url = "http://" + request.get_host() + reverse("openrosa_formxml") + "?formId="
    context = Context({
        "forms" : models.ORForm.objects.filter(active=True),
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

@csrf_exempt
def submission(request):
    def handle_uploaded_file(f, file):
        for chunk in f.chunks():
            file.write(chunk)
        if file.tell() == 0:
            logger.warn("file: %s is empty" % file.name) 
        file.close()

    def create_media_folder(xml):
        device_id = value_or_none(xml, "device_id")
        if device_id:
            path = os.path.join(settings.OPENROSA_IMAGES_DIR, device_id)
        else:
            path = os.path.join(settings.OPENROSA_IMAGES_DIR, "no_device_id")

        if not os.path.exists(path):
            os.mkdir(path)
        return path    

    if request.method == "GET":
        response =  HttpResponse("", status=204) 
        url = "http://" + request.get_host() + reverse("openrosa_submission")
        response["Location"] = url
    elif request.method == "POST":

        form = forms.UploadORInstance(request.POST, request.FILES)
        if form.is_valid():
            f = tempfile.NamedTemporaryFile(
                prefix="submission_", suffix=".xml", 
                dir=settings.OPENROSA_SUBMISSIONS_DIR, delete=False)

            handle_uploaded_file(request.FILES["xml_submission_file"], f)
            dom = minidom.parse(f.name)

            data_elements = dom.getElementsByTagName("data")
            orform = None
            form_name = None
            if len(data_elements) == 1:
                form_name = data_elements[0].attributes["id"].value
                orforms = models.ORForm.objects.filter(form_id=form_name)
                if len(orforms) == 1:
                   orform = orforms[0]

            filename = os.path.basename(f.name)
            new_model, _ = models.ORFormSubmission.objects.get_or_create(
                form=orform,
                filename=filename
            )

            media_dir = create_media_folder(dom)
            for filename, stream in request.FILES.items():
                if filename != "xml_submission_file":
                    media_path = os.path.join(media_dir, filename)
                    media_file = open(media_path, "w")
                    handle_uploaded_file(stream, media_file)
                    new_media, _ = models.ORSubmissionMedia.objects.get_or_create(
                        submission=new_model,
                        filename=filename
                    )

        signals.on_submission.send_robust(sender=models.ORFormSubmission, submission=new_model)
        response = HttpResponse("", status=202) 
        
    return response

def view_submission(request, id=None):
    if request.method == "GET":
        submission = get_object_or_404(models.ORFormSubmission, pk=id)
        path = os.path.join(settings.OPENROSA_SUBMISSIONS_DIR, submission.filename)
        if not os.path.exists(path):
            raise Http404
        f = open(path)
        response = HttpResponse(f.read(), mimetype='text/xml; charset=utf-8')
        return response
    raise Http404

def edit_submission_xml(request, object_id, template_name="openrosa/edit_submission_xml.html", extra_context=None):
    extra_context = extra_context or {}
    submission = get_object_or_404(models.ORFormSubmission, pk=object_id)
    xml_path = submission.get_full_xml_path()
    if request.method == "GET":
        xml = open(xml_path).read()
        form = extra_context["form"] = forms.SubmissionXMLForm(initial={"xml" : xml})
    elif request.method == "POST":
        form = extra_context["form"] = forms.SubmissionXMLForm(request.POST)
        if form.is_valid():
            f = open(xml_path, "w")
            xml = form.cleaned_data["xml"]
            f.write(xml)
            f.close()
            submission.save()
            return HttpResponseRedirect("/admin/openrosa/orformsubmission")
        
    return direct_to_template(request, template=template_name, extra_context=extra_context)

def show_media(request, device_id, filename):
    media_dir = os.path.join(settings.OPENROSA_IMAGES_DIR, device_id)
    path = os.path.join(media_dir, filename)
    if os.path.exists(path):
        mimetype = "application/octet-stream"
        if filename.endswith("jpg"):
            mimetype = "image/jpg"
        elif filename.endswith("amr"):
            mimetype = "audio/amr"
        return HttpResponse(open(path).read(), mimetype=mimetype)

    raise Http404
    
