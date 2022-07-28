# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. // SPDX-License-Identifier: MIT-0


import cv2
import sys
# this base file below has the reusable functions common across these scripts
from base_l4v_client import process_segmentation, check_for_anomalies


if (len(sys.argv) < 3):
    print("missing command line arguements. Example: <imagefile> <modelName> ")
    sys.exit(1)

img = cv2.imread(sys.argv[1])
# this is very important to covert to RGB or you will not get good results
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
print("start client "+str(sys.argv))

detect_anomalies_response = check_for_anomalies(img, sys.argv[2])
process_segmentation(img, detect_anomalies_response)

