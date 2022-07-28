# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. // SPDX-License-Identifier: MIT-0
import time
import numpy as np
import cv2


#
# this sample is for the Raspberry Pi V2 camera, mounted sideways
# please adjust the cropped values to make your subject center and as little background as possible for good results
#
#
def gstreamer_pipeline(
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
    framerate=30,
    flip_method=1,
):
    return (
          "nvarguscamerasrc ! "
          "video/x-raw(memory:NVMM), "
          "width=(int)%d, height=(int)%d, "
          "format=(string)NV12, framerate=(fraction)%d/1 ! "
          "nvvidconv flip-method=1 ! "
          "videocrop top=1300 bottom=200 left=0 right=0 !"
          "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
          "videoconvert ! "
          "video/x-raw, format=(string)BGR ! appsink"
          % (
               capture_width,
               capture_height,
               framerate,
               display_width,
               display_height,
            )
          )

cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
if cap.isOpened():
    ret_val, img = cap.read()
#    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#    print("ret_val="+str(ret_val))
#    print("img="+str(img))
    cv2.imwrite("frame.jpg",img)
    cap.release()
    print("picture taken to frame.jpg")


else:
    print("Unable to open camera")
