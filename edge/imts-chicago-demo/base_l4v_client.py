# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. // SPDX-License-Identifier: MIT-0
import time
import numpy as np
import cv2
import grpc
import edge_agent_pb2 as pb2
from edge_agent_pb2_grpc import (
    EdgeAgentStub
)

import logging


import sys
import json
import io



def process_segmentation(img, detect_anomalies_response):
    defects_over_threshold = {}
    all_defects = {}
    if detect_anomalies_response.detect_anomaly_result.is_anomalous:
        anomalies = detect_anomalies_response.detect_anomaly_result.anomalies

        if detect_anomalies_response.detect_anomaly_result.anomaly_mask is not None:
            if (detect_anomalies_response.detect_anomaly_result.anomaly_mask and detect_anomalies_response.detect_anomaly_result.anomaly_mask.byte_data):
                # Anomaly mask was returned as bytes over the wire - you can also used shared memory for increased performance, see below.
                predicted_anomaly_mask_buffer = detect_anomalies_response.detect_anomaly_result.anomaly_mask.byte_data
            elif (detect_anomalies_response.detect_anomaly_result.anomaly_mask and detect_anomalies_response.detect_anomaly_result.anomaly_mask.shared_memory_handle):
                # Anomaly mask was returned as shm segment.
                # See the developer guide for information on how to use shared memory for increased performance at
                # https://docs.aws.amazon.com/lookout-for-vision/latest/developer-guide/models-devices.html
                raise Exception("SHM functionality not implemented")
            else:
                # Anomaly mask was not returned.
                raise Exception(
                    "Anomaly mask is present in the dataset, but is missing in the model response."
                )

            # Loading predicted anomaly mask.
            predicted_anomaly_mask = np.frombuffer(
                predicted_anomaly_mask_buffer,
                dtype=np.uint8,
            ).reshape(
                detect_anomalies_response.detect_anomaly_result.anomaly_mask.height,
                detect_anomalies_response.detect_anomaly_result.anomaly_mask.width,
                3,
            )
            # convert the mask back to BGR so it looks correct
            predicted_anomaly_mask_bgr = cv2.cvtColor(
                predicted_anomaly_mask, cv2.COLOR_RGB2BGR)
            cv2.imwrite("./defectmask.png", predicted_anomaly_mask_bgr)
            # we need to convert the mask and the image and blend the two together
            alpha = 0.7
            beta = 1 - alpha
            blended = cv2.addWeighted(
                img, alpha, predicted_anomaly_mask, beta, 0)
            blended_bgr = cv2.cvtColor(blended, cv2.COLOR_RGB2BGR)
            cv2.imwrite("./blended.png", blended_bgr)
            cv2.namedWindow('ANOMALY', cv2.WINDOW_FULLSCREEN)
            cv2.putText(img=blended_bgr, text='ANOMALY', org=(10, 50), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=2, color=(0, 0, 255),thickness=3)
            for anomaly in anomalies:
                if anomaly.pixel_anomaly.total_percentage_area > 0.01:
                    # ignore tag with 'background' or any other defect you wish to ignore
                    if anomaly.pixel_anomaly and anomaly.name != 'background':
                        print("anomaly:"+str(anomaly))
                        defects_over_threshold[anomaly.name] = anomaly.pixel_anomaly.hex_color
                        all_defects[anomaly.name] = anomaly.pixel_anomaly.hex_color
            if len(defects_over_threshold) > 0:
                print(
                    f"Image is anomalous, ({detect_anomalies_response.detect_anomaly_result.confidence * 100} % confidence) contains defects with total area over .1%: {defects_over_threshold}")
            else:
                print(
                    f"Image is anomalous, ({detect_anomalies_response.detect_anomaly_result.confidence * 100} % confidence) contains no defects with total area over .1%. Needs manual inspection for defects {all_defects}")
            if anomaly.name != "background": 
               cv2.putText(img=blended_bgr, text=anomaly.name, org=(10, 320), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 0, 255),thickness=1) 
            resized = cv2.resize(blended_bgr, (1100,760), interpolation = cv2.INTER_AREA)
            cv2.imshow('ANOMALY', cv2.resize(resized, (1920,1080),interpolation = cv2.INTER_AREA))            
            cv2.waitKey(0)
    else:
        print(f"Image is normal")
        cv2.namedWindow('NORMAL', cv2.WINDOW_FULLSCREEN)
        cv2.putText(img=img, text='NORMAL', org=(10, 50), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=2, color=(0, 0, 255),thickness=3)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        cv2.imshow('NORMAL', cv2.resize(img, (1920,1080),interpolation = cv2.INTER_AREA))
        cv2.waitKey(0)



def check_for_anomalies(img, modelName):
    with grpc.insecure_channel("unix:///tmp/aws.iot.lookoutvision.EdgeAgent.sock") as channel:
        print("channel set")
        stub = EdgeAgentStub(channel)
        h, w, c = img.shape
        print("shape="+str(img.shape))
        detect_anomalies_response = stub.DetectAnomalies(
            pb2.DetectAnomaliesRequest(
                model_component=sys.argv[2],
                bitmap=pb2.Bitmap(
                    width=w,
                    height=h,
                    byte_data=bytes(img.tobytes())
                )
            )
        )
        return detect_anomalies_response
