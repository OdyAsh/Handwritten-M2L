import cv2
import numpy as np
from functools import cmp_to_key
from PIL import Image
from typing import Union
from tensorflow import keras

def extractSymbols(imgOrig: Union[Image.Image, np.ndarray], showSteps = False, 
                    returnSteps = False, medFilter = False, verticalSymbols = False): # The ": Union[]" syntax is to be able to show the possible types that could be passed to "imgOrig" whenever extractSymbols() gets called 
    debugImgSteps = []
    if isinstance(imgOrig, Image.Image): # if true, then "imgOrig" is a PIL Image object, not a CV image (ndarray) object so we will convert it
        imgOrig = np.array(imgOrig)[:, :, ::-1] # the "-1" is to get the ndarray as BGR not RGB, as the PIL image was originally in RGB
    imgGray = cv2.cvtColor(imgOrig,cv2.COLOR_BGR2GRAY) # converts image from BGR to grayscale 
    if medFilter:
        imgGray = cv2.medianBlur(imgGray, 5) # performs median filter with 5x5 filter size
        debugImgSteps.append(imgGray)
    
    imgCanny = cv2.Canny(imgGray, 50,180) # performs canny edge detection with low threshold as 50 and high threshold as 180
    debugImgSteps.append(imgCanny)

    kernel = np.ones((5,5), np.uint8)
    imgDilated = cv2.dilate(imgCanny, kernel, iterations=5) # dilating the image 5 times to connect symbols (e.g. "=" instead of 2 "-")
    debugImgSteps.append(imgDilated)

    contours, _= cv2.findContours(imgDilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # returns contours which the bounding boxes of each symbol will be extracted from

    boundingBoxes = []
    for contour in contours:
        x,y,w,h = cv2.boundingRect(contour)
        boundingBoxes.append((x,y,w,h))

    global rowsG # Global because it will be used in leftRightTopBottom()
    rowsG, _, _ = imgOrig.shape
    key_leftRightTopBottom = cmp_to_key(leftRightTopBottom) # Wrapper to allow a custom function with 2 parameters to be the key function when sorting
    
    if (verticalSymbols):
        boundingBoxes = sorted(boundingBoxes, key=key_leftRightTopBottom) # sort with priority on y-coordinate
    else:
        boundingBoxes = sorted(boundingBoxes, key=lambda x : x[0]) # sort with priority on x-coordinate

    symbols = []
    for box in boundingBoxes:
        x,y,w,h = box
        mathSymbol = imgOrig[y:y+h, x:x+w]
        mathSymbol = cv2.cvtColor(mathSymbol, cv2.COLOR_BGR2GRAY) #converting to Gray as tensorflow deals with grayscale or RGB, not BGR
        mathSymbol = cv2.resize(mathSymbol, (45,45), interpolation=cv2.INTER_AREA) #to have the same size as trained images in the dataset
        debugImgSteps.append(mathSymbol)
        mathSymbolF = mathSymbol.astype('float32') #optional: tensorflows deals with float32, not uint8
        symbols.append(mathSymbolF.reshape(1, 45, 45)) # reshaped to be compatible with model

    if showSteps:
        dispImages(debugImgSteps)

    if returnSteps:
        return symbols, debugImgSteps

    return symbols
    

def leftRightTopBottom(tup1, tup2):
    x1, y1, _, _ = tup1
    x2, y2, _, _ = tup2
    rows = rowsG
    yRegion1, yRegion2 = -1, -1

    for i in range(4):
        if y1 < rows/4 + rows*(i/4.0):
            yRegion1 = i
            break
    else:
        if yRegion1 == -1:
            yRegion1 = 4

    for i in range(4):
        if y2 < rows/4 + rows*(i/4.0):
            yRegion2 = i
            break
    else:
        if yRegion2 == -1:
            yRegion2 = 4
    
    if yRegion1 < yRegion2:
        return -1
    elif yRegion2 < yRegion1:
        return 1
    elif x1 <= x2:
        return -1
    else:
        return 1

def dispImages(imgs):
    for img in imgs:
        cv2.imshow('Image', img)
        cv2.waitKey(0)
    else:
        cv2.destroyAllWindows()