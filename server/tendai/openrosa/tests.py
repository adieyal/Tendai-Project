import os
from xml.dom import minidom
import tempfile

from django.test import TestCase
from django.core.urlresolvers import reverse

import models

class ORFormTest(TestCase):
    def setUp(self):
        self.orform = models.ORForm.objects.create(
            name="Test Form",
            form_id="TestFormID",
            majorminorversion="0.5"
        )

    def test_no_form_exists(self):
        resp = self.client.get("/openrosa/formXml/?formId=NoFormExists")
        assert resp.status_code == 404

    def test_absolute_url(self):
        assert self.orform.get_absolute_url() == "/openrosa/formXml/?formId=%s" % self.orform.form_id

    def test_absolute_url_no_file(self):
        url = self.orform.get_absolute_url()
        resp = self.client.get(url)
        assert resp.status_code == 404

    def test_absolute_get_form_exists(self):
        f = open("openrosa/orforms/TestFormID.xml", "w")
        f.write("testtesttest")
        f.close()

        url = self.orform.get_absolute_url()
        resp = self.client.get(url)
        assert resp.status_code == 200
        assert resp.content == "testtesttest"

        os.unlink("openrosa/orforms/TestFormID.xml")

class ORFormSubmissionTest(TestCase):
    def setUp(self):
        self.submission_url = reverse("openrosa_submission")

    def submit_file(self, filename):
        f = open(filename)
        self.client.post(self.submission_url, {"xml_submission_file": f})
        f.close()
