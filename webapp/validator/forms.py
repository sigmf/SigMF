from django import forms

class SigMFUploadForm(forms.Form):
    sigmf_meta_file = forms.FileField()
