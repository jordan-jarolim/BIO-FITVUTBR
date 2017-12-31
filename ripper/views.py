from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.core.files.images import get_image_dimensions
import os
from django.views.decorators.csrf import csrf_exempt
import logging
from ripper.models import analyzeFingerPrint
from ripper.models import getOriginalName
import re

# Get an instance of a logger
logger = logging.getLogger(__name__)

@csrf_exempt
def chooseArea(request): 
    name = getOriginalName()
    path = settings.STATIC_URL + settings.MEDIA_URL + name
    if os.path.exists(path):
        # Returns the (width, height) of an image, given an open file or a path
        w, h = get_image_dimensions(path)

    return render(request, 'choose-area.html', {'width': w, 'height': h, 'name': "upload/"+name})


@csrf_exempt
def analyze(request):
    name = getOriginalName()

    ridgeCount = analyzeFingerPrint(request.POST['x1'], request.POST['y1'], request.POST['x2'], request.POST['y2'])
    return render(request, 'analyze.html', {'x1': int(float(request.POST['x1'])), 'y1': int(float(request.POST['y1'])), 'x2': int(float(request.POST['x2'])), 'y2': int(float(request.POST['y2'])), 'ridgeCount': ridgeCount, 'name': "upload/"+name})
