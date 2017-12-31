from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os
from .forms import UploadFileForm
from django.conf import settings
from django.db import models

from uploader.models import handle_uploaded_file

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/ripper/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def index(request):
    return render(request, 'index.html')