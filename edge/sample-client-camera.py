# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. // SPDX-License-Identifier: MIT-0
import time
import cv2
from base_l4v_client import process_segmentation, check_for_anomalies
import sys


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


if (len(sys.argv) < 2):
    print("missing command line arguements. Example: <modelName> ")
    sys.exit(1)

cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
if cap.isOpened():
    ret_val, img = cap.read()
    cv2.imwrite("frame.bmp", img)
    cap.release()
    print("start client <modelName>")
    
    detect_anomalies_response = check_for_anomalies(img, sys.argv[1])
    process_segmentation(img, detect_anomalies_response)


else:
    print("Unable to open camera")
