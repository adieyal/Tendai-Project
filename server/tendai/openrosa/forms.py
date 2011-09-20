from xml.dom import minidom
import traceback
from django import forms

class UploadORForm(forms.Form):
    file = forms.FileField(label="Form XML File")
    majorminorversion = forms.CharField(label="Major Minor Version")

class UploadORInstance(forms.Form):
    xml_submission_file = forms.FileField(label="Form Submision")

class SubmissionXMLForm(forms.Form):
    xml = forms.CharField(widget=forms.Textarea)
    def clean_xml(self):
        data = self.cleaned_data['xml']
        try:
            minidom.parseString(data)
        except Exception:
            traceback.print_exc()
            raise forms.ValidationError("Invalid XML - please correct before saving")

        return data

class AddressCorrectionForm(forms.Form):
    file = forms.FileField(label="Address correction file")
