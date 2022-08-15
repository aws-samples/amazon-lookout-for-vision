# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. // SPDX-License-Identifier: MIT-0
import cv2
import grpc
import edge_agent_pb2 as pb2 
from edge_agent_pb2_grpc import ( 
    EdgeAgentStub
)
from pypylon import pylon
import sys
from base_l4v_client import process_segmentation, check_for_anomalies

if (len(sys.argv) < 3):
    print("usage: capture-subject-basler <deviceSerialNumber> <componentName>")
    sys.exit(1)
print ("usage: capture-subject-basler <deviceSerialNumber> <componentName>")

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
    print("start client")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    detect_anomalies_response = check_for_anomalies(img, sys.argv[2])
    process_segmentation(img, detect_anomalies_response)


camera.Close()
cv2.destroyAllWindows()

