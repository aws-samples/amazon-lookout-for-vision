# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. // SPDX-License-Identifier: MIT-0
import time
import numpy as np
import cv2
import grpc
import edge_agent_pb2 as pb2 
from edge_agent_pb2_grpc import ( 
    EdgeAgentStub
)  
import sys
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json
from base_l4v_client import process_segmentation, check_for_anomalies

ENDPOINT = "aidnfuomgla6i-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "l4vJetsonXavierNx"
PATH_TO_CERTIFICATE = "/greengrass/v2/thingCert.crt"
PATH_TO_PRIVATE_KEY = "/greengrass/v2/privKey.key"
PATH_TO_AMAZON_ROOT_CA_1 = "/greengrass/v2/rootCA.pem"
TOPIC = "l4v/testclient"




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
    cv2.imwrite("frame.bmp",img)
    cap.release()
    print("start client <modelName>")

    detect_anomalies_response = check_for_anomalies(img, sys.argv[1])
    process_segmentation(img, detect_anomalies_response)
        
    anomalies = {}
    for anomaly in detect_anomalies_response.detect_anomaly_result.anomalies:
        anomalies[anomaly.name] = {
            "height": detect_anomalies_response.detect_anomaly_result.anomaly_mask.height,
            "width": detect_anomalies_response.detect_anomaly_result.anomaly_mask.width
        }

    messageToIotCore = {
        "is_anomalous": str(detect_anomalies_response.detect_anomaly_result.is_anomalous),
        "confidence": detect_anomalies_response.detect_anomaly_result.confidence,
        "anomalies": anomalies
    }

    print("message to MQTT:"+json.dumps(messageToIotCore, indent=4))

    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
                        endpoint=ENDPOINT,
                        cert_filepath=PATH_TO_CERTIFICATE,
                        pri_key_filepath=PATH_TO_PRIVATE_KEY,
                        client_bootstrap=client_bootstrap,
                        ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
                        client_id=CLIENT_ID,
                        clean_session=False,
                        keep_alive_secs=6
                        )
    print("Connecting to {} with client ID '{}'...".format(
                ENDPOINT, CLIENT_ID))
    # Make the connect() call
    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")
    # Publish message to server desired number of times.
    print('Begin Publish')
    data = "{} [{}]".format(str(messageToIotCore), 1)
    message = {"message" : data}
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published: '" + json.dumps(message) + "' to the topic: " + TOPIC)
    t.sleep(0.1)
    print('Publish End')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    
else:
    print("Unable to open camera")
