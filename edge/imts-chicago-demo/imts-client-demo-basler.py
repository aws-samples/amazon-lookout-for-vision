# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. // SPDX-License-Identifier: MIT-0
import cv2
import grpc
import edge_agent_pb2 as pb2 
from edge_agent_pb2_grpc import ( 
    EdgeAgentStub
)
from pypylon import pylon
import numpy as np
import sys
from base_l4v_client import process_segmentation, check_for_anomalies

if (len(sys.argv) < 3):
    print("usage: capture-subject-basler <deviceSerialNumber> <componentName>")
    sys.exit(1)
print ("usage: capture-subject-basler <deviceSerialNumber> <componentName>")

info = pylon.DeviceInfo()
print("getting camera serial number "+sys.argv[1])
img_1 = np.zeros([1080,1920,1],dtype=np.uint8)
img_1.fill(0)
# or img[:] = 255
cv2.putText(img=img_1, text='Welcome to Amazon Lookout For Vision' , org=(100, 150), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=2, color=(255, 0, 255),thickness=2)
cv2.putText(img=img_1, text='Place subject under camera and press any key' , org=(100, 250), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=2, color=(255, 0, 255),thickness=2)
cv2.imshow('Welcome to Amazon Lookout For Vision', img_1)
cv2.waitKey(0)
info.SetSerialNumber(sys.argv[1])
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
#`converter.OutputPixelFormat = pylon.PixelType_BayerRG8
tl_factory = pylon.TlFactory.GetInstance()
camera = pylon.InstantCamera()
camera.Attach(tl_factory.CreateFirstDevice(info)) # change this to use device serial number
camera.Open()
#camera.PixelFormat.SetValue("BayerRG8")
camera.StartGrabbing(1)
grab = camera.RetrieveResult(5000, pylon.TimeoutHandling_Return)
if grab.GrabSucceeded():
    img = grab.GetArray()
    print(f'Size of image: {img.shape}')
    image = converter.Convert(grab)
    img = image.GetArray()
    cropped_image = img[50:450, 280:900]
    dim = (550,380)
    resized_image = cv2.resize(cropped_image, dim, interpolation = cv2.INTER_AREA)


    cv2.namedWindow('ORIGINAL', cv2.WINDOW_FULLSCREEN)
    cv2.imshow('ORIGINAL', cv2.resize(resized_image, (1920,1080),interpolation = cv2.INTER_AREA))
    cv2.waitKey(0)
    cv2.imwrite(sys.argv[3],img)
    cv2.imwrite("cropped-"+sys.argv[3],resized_image)
    print("start client")
    converted_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
    detect_anomalies_response = check_for_anomalies(converted_image, sys.argv[2])
    process_segmentation(converted_image, detect_anomalies_response)


camera.Close()
cv2.destroyAllWindows()

