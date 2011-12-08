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

class ORSubmissionMediaAdmin(admin.ModelAdmin):
    pass

class ORFormAdmin(admin.ModelAdmin):
    list_display = ('name', 'majorminorversion', 'modified_date', 'active')
    list_filter = ('name', 'active')

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
