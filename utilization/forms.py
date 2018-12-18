from django import forms
from utilization.models import Document

class FileUploadForm(forms.Form):
    file = forms.FileField(required=True)
