from django.shortcuts import render
from .models import Field
from .forms import SigMFUploadForm
from django.http import HttpResponseRedirect
import sigmf

# Create your views here.

def index(request):
    global_fields = Field.objects.filter(key_category="global")
    capture_fields = Field.objects.filter(key_category="capture")
    annotations_fields = Field.objects.filter(key_category="annotations")
    categories = [{'name': "global",
                   'fields': global_fields},
                  {'name': "capture",
                   'fields': capture_fields},
                  {'name': "annotations",
                   'fields': annotations_fields}]

    sigmf_upload_form = SigMFUploadForm()
    context = {'categories': categories, 'sigmf_upload_form':
                sigmf_upload_form}

    if request.method == "POST":
        form = SigMFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            print("Received valid upload")
            ul_file = request.FILES['sigmf_meta_file']
            print("File size:")
            print(ul_file.size)
            sigmf_file_str = ul_file.read()
            sigmf_file_str = sigmf_file_str.decode("utf-8")
            sigmf_validator = sigmf.SigMFFile(sigmf_file_str)
            file_is_valid = sigmf_validator.validate()
            if file_is_valid:
                context['validator_result'] = True
            else:
                print(file_is_valid.error)
                context['validator_result'] = False
                context['validator_error'] = str(file_is_valid)

            return render(request, 'validator/index.html', context)
        print("Received invalid form upload")
        return HttpResponseRedirect('/validator/')
    else:
        return render(request, 'validator/index.html', context)

def fields(request):
    global_fields = Field.objects.filter(key_category="global")
    capture_fields = Field.objects.filter(key_category="capture")
    annotations_fields = Field.objects.filter(key_category="annotations")
    categories = [{'name': "global",
                   'fields': global_fields},
                  {'name': "capture",
                   'fields': capture_fields},
                  {'name': "annotations",
                   'fields': annotations_fields}]
    context = {'categories': categories}
    return render(request, 'validator/fields.html', context)
