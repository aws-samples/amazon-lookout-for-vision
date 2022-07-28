# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. // SPDX-License-Identifier: MIT-0
import time
import numpy as np
import cv2
from pypylon import pylon
import platform
import sys


info = pylon.DeviceInfo()
print("getting camera serial number "+sys.argv[1])
info.SetSerialNumber(sys.argv[1])
converter = pylon.ImageFormatConverter()

tl_factory = pylon.TlFactory.GetInstance()
camera = pylon.InstantCamera()
camera.Attach(tl_factory.CreateFirstDevice(info)) # change this to use device serial number
camera.Open()
camera.StartGrabbing(1)
grab = camera.RetrieveResult(5000, pylon.TimeoutHandling_Return)
if grab.GrabSucceeded():
    img = grab.GetArray()
    print(f'Size of image: {img.shape}')
    image = converter.Convert(grab)
    img = image.GetArray()
    cv2.namedWindow('title', cv2.WINDOW_NORMAL)
    cv2.imshow('title', img)
    cv2.waitKey(0)
    cv2.imwrite(sys.argv[2],img)

camera.Close()
cv2.destroyAllWindows()

