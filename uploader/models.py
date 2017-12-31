from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os
from .forms import UploadFileForm
from django.conf import settings
from django.db import models
import time


def handle_uploaded_file(file):
    path=settings.STATIC_URL+settings.MEDIA_URL
    if not os.path.exists(path):
        os.mkdir(path)
    else: 
        folder = path
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
 
    created = str(time.time())
    with open(path + "ripper-"+created+".png", 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return created