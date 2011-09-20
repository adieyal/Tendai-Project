import csv
import os
from StringIO import StringIO
import re
from collections import OrderedDict, Counter, defaultdict
from xml.dom import minidom
from itertools import groupby

from django.contrib import admin
from django import forms
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf.urls.defaults import patterns, include, url
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.db.models import Count, Max

import models
import forms
import views
from general import utils

re_name = re.compile("title>([^<>]*)<")
def handle_uploaded_file(f, file):
    for chunk in f.chunks():
        file.write(chunk)

class ORSubmissionMediaAdmin(admin.ModelAdmin):
    pass

class ORFormAdmin(admin.ModelAdmin):
    def upload_form(self, request, template_name="openrosa/form_upload.html"):

        if request.method == 'POST':
            form = forms.UploadORForm(request.POST, request.FILES)
            if form.is_valid():
                buf = StringIO()
                handle_uploaded_file(request.FILES["file"], buf)
                buf.seek(0)
                xml = buf.read()

                name = re_name.search(xml).groups()[0]
                version = form.cleaned_data["majorminorversion"]
                slug = utils.slugify(name) + "-" + version

                models.ORForm.objects.create(
                    name=name,
                    form_id=slug,
                    majorminorversion=version
                )
                
                # ensure that the data.id attribute correctly identifies the form
                f = open("%s/%s.xml" % (settings.OPENROSA_FORMS_DIR, slug), "w+")
                dom = minidom.parseString(xml)
                data_elements = dom.getElementsByTagName("data")
                if len(data_elements) == 1:
                    data_elements[0].attributes["id"].value = slug

                # Horrible code
                # minidom self-closes empty tags with no option to change this
                # rather than moving to another xml library, I'm just replacing self-closed tags
                # with a more verbose representation
                xml = dom.toxml("utf-8")
                def foo(match):
                    m = match.groups()[0]
                    return "<%s></%s>" % (m, m)

                xml = re.sub("<([^<>\s*]+)\s*/>", foo, xml)
                f.write(xml)
                f.close()

                context = RequestContext(request, {
                    "submission_complete" : True}
                )
                self.message_user(request, "Successfully uploaded form")
                return HttpResponseRedirect("/admin/openrosa/orform")
        else:
            form = forms.UploadORForm()
        context = RequestContext(request, {"form" : form})
        return render_to_response(template_name, context)

    def get_urls(self):
        urls = super(ORFormAdmin, self).get_urls()
        my_urls = patterns('', 
            url(r'^upload_form/$', self.upload_form, {}, "openrosa_orform_upload_form"),
        )
        return my_urls + urls

class ORFormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('created_date', 'device_id', 'subscriber_id', 'sim_id')
    list_filter = ('form', 'device_id', 'subscriber_id', 'sim_id')
    date_hierarchy = 'created_date'

    def __init__(self, *args, **kwargs):
        super(ORFormSubmissionAdmin, self).__init__(*args, **kwargs)
        self.xmls = {}

    def get_urls(self):
        urls = super(ORFormSubmissionAdmin, self).get_urls()
        my_urls = patterns('', 
            url(r'^edit_xml/(?P<object_id>\d+)/$', self.edit_xml, {}, "openrosa_orformsubmission_edit_xml"),
        )
        return my_urls + urls

    def export_response(self, filename):
        response = HttpResponse(mimetype='text/csv')
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response

    def edit_xml(self, request, object_id):
        return views.edit_submission_xml(request, object_id)


admin.site.register(models.ORForm, ORFormAdmin)
admin.site.register(models.ORFormSubmission, ORFormSubmissionAdmin)
admin.site.register(models.ORSubmissionMedia, ORSubmissionMediaAdmin)
