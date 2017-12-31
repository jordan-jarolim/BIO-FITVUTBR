from django.db import models
import cv2
from django.conf import settings
import numpy as np
import logging
import os
import re




# Get an instance of a logger
logger = logging.getLogger(__name__)

# helper to readimg
def readImg(name, profile):
    path = settings.STATIC_URL + settings.MEDIA_URL
    return cv2.imread(path + name, profile)

#helper to write img
def writeImg(name, img):
    path = settings.STATIC_URL + settings.MEDIA_URL
    if os.path.exists(path+name):
        os.remove(path+name)
    cv2.imwrite(path + name, img)

# get actual ripper filename
def getOriginalName():
    listing = os.listdir(settings.STATIC_URL + settings.MEDIA_URL)
    regex = re.compile("^ripper-[0-9]*\.[0-9]*\.png")
    name = str(list(filter(regex.match, listing))[0])
    return name

#threshold image and save new instance
def thresholdImg():
    img = readImg("contrasted.png", cv2.IMREAD_GRAYSCALE)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(img)
    #blured = cv2.medianBlur(img, 3)
    #thresholded = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    ret, thresholded = cv2.threshold(img, minVal + ((maxVal - minVal) / 2), 255, cv2.THRESH_BINARY)
    writeImg("thresholded.png", thresholded)

# contrast and save new instance
def adjustContrast():
    name = getOriginalName()
    img = readImg(name, cv2.IMREAD_GRAYSCALE)
    #final = cv2.equalizeHist(img)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    final = clahe.apply(img)
    writeImg("contrasted.png", final)

#https://stackoverflow.com/questions/32328179/opencv-3-0-python-lineiterator
def createLineIterator(P1, P2, img):
    #define local variables for readability
    imageH = img.shape[0]
    imageW = img.shape[1]
    P1X = P1[0]
    P1Y = P1[1]
    P2X = P2[0]
    P2Y = P2[1]

    #difference and absolute difference between points
    #used to calculate slope and relative location between points
    dX = P2X - P1X
    dY = P2Y - P1Y
    dXa = np.abs(dX)
    dYa = np.abs(dY)

    #predefine numpy array for output based on distance between points
    itbuffer = np.empty(shape=(np.maximum(dYa,dXa),3),dtype=np.float32)
    itbuffer.fill(np.nan)

    #Obtain coordinates along the line using a form of Bresenham's algorithm
    negY = P1Y > P2Y
    negX = P1X > P2X
    if P1X == P2X: #vertical line segment
        itbuffer[:,0] = P1X
        if negY:
            itbuffer[:,1] = np.arange(P1Y - 1,P1Y - dYa - 1,-1)
        else:
            itbuffer[:,1] = np.arange(P1Y+1,P1Y+dYa+1)              
    elif P1Y == P2Y: #horizontal line segment
        itbuffer[:,1] = P1Y
        if negX:
            itbuffer[:,0] = np.arange(P1X-1,P1X-dXa-1,-1)
        else:
            itbuffer[:,0] = np.arange(P1X+1,P1X+dXa+1)
    else: #diagonal line segment
        steepSlope = dYa > dXa
        if steepSlope:
            slope = dX.astype(np.float32)/dY.astype(np.float32)
            if negY:
                itbuffer[:,1] = np.arange(P1Y-1,P1Y-dYa-1,-1)
            else:
                itbuffer[:,1] = np.arange(P1Y+1,P1Y+dYa+1)
            itbuffer[:,0] = (slope*(itbuffer[:,1]-P1Y)).astype(np.int) + P1X
        else:
            slope = dY.astype(np.float32)/dX.astype(np.float32)
            if negX:
                itbuffer[:,0] = np.arange(P1X-1,P1X-dXa-1,-1)
            else:
                itbuffer[:,0] = np.arange(P1X+1,P1X+dXa+1)
            itbuffer[:,1] = (slope*(itbuffer[:,0]-P1X)).astype(np.int) + P1Y

    #Remove points outside of image
    colX = itbuffer[:,0]
    colY = itbuffer[:,1]
    itbuffer = itbuffer[(colX >= 0) & (colY >=0) & (colX<imageW) & (colY<imageH)]

    #Get intensities from img ndarray
    itbuffer[:,2] = img[itbuffer[:,1].astype(np.uint),itbuffer[:,0].astype(np.uint)]

    return itbuffer


# count changes from white to black
def countLines(x1, y1, x2, y2):
    numbX1 = int(float(x1))
    numbY1 = int(float(y1))
    numbX2 = int(float(x2))
    numbY2 = int(float(y2))

    img = readImg("thresholded.png", cv2.IMREAD_GRAYSCALE)
    points = createLineIterator(np.array([numbX1, numbY1]), np.array([numbX2, numbY2]), img)
  
    previous = -1
    ridgeCount = 0

    for tuplePoint in points:    
        # start to black
        if ((previous == -1) and (tuplePoint[2] == 0)):
            previous = 0
            ridgeCount += 1

        # white to black
        if ((previous == 255) and (tuplePoint[2] == 0)):
            previous = 0
            ridgeCount += 1

        #white to white
        if ((previous == 255) and (tuplePoint[2] == 255)):
            pass

        #black to black
        if ((previous == 0) and (tuplePoint[2] == 0)):
            pass

        #black to white
        if ((previous == 0) and (tuplePoint[2] == 255)):
            previous = 255

    #write into final img
    name = getOriginalName()
    BWFinal = readImg(name, cv2.IMREAD_GRAYSCALE)
    final = cv2.cvtColor(BWFinal,cv2.COLOR_GRAY2RGB)

    #add line there
    cv2.line(final,(numbX1, numbY1),(numbX2, numbY2),(0,0,255),2)

    #write it
    writeImg("final.png", final)

    return ridgeCount


def analyzeFingerPrint(x1, y1, x2, y2):
    adjustContrast()
    thresholdImg()
    ridgeCount = countLines(x1, y1, x2, y2)
    return ridgeCount
